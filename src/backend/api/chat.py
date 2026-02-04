"""
Chat API Router

聊天相关的 API 路由。
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

from auth.dependencies import get_current_user_id, get_current_user
from infrastructure.database import db, UserConfigInDB
from services.chat_service import get_chat_service
from services.summary_service import get_summary_service
from services.download_service import get_download_service
from core.models import WorkLogReport
from utils.logger import get_logger
from utils.datetime import parse_datetime


router = APIRouter(prefix="/api/chat", tags=["Chat"])
logger = get_logger(__name__)


class ChatMessage(BaseModel):
    """聊天消息"""
    message: str = Field(..., description="用户消息")
    conversation_id: Optional[str] = Field(None, description="会话 ID（可选）")


class ChatResponse(BaseModel):
    """聊天响应"""
    content: str = Field(..., description="回复内容")
    role: str = Field(default="assistant", description="角色")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="元数据")
    attachments: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="附件列表")


class GenerateWorklogRequest(BaseModel):
    """生成工作日志请求"""
    since_date: Optional[str] = Field(None, description="开始日期 (ISO format)")
    until_date: Optional[str] = Field(None, description="结束日期 (ISO format)")
    branch: Optional[str] = Field(None, description="分支名称")
    project_id: Optional[str] = Field(None, description="项目 ID")
    include_stats: bool = Field(default=True, description="是否包含统计信息")
    time_range: Optional[str] = Field(None, description="时间范围描述 (如 '本周', '本月')")


@router.post("/message", response_model=ChatResponse)
async def chat_message(
    chat_message: ChatMessage,
    current_user_id: int = Depends(get_current_user_id)
) -> ChatResponse:
    """发送聊天消息

    处理用户消息，调用 LLM 和 MCP 工具，返回回复。

    Args:
        chat_message: 聊天消息
        current_user_id: 当前用户 ID

    Returns:
        聊天响应
    """
    # 获取用户配置
    config = await db.get_one_by_field(UserConfigInDB, "user_id", current_user_id)

    if not config:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请先配置 GitLab 或 GitHub"
        )

    try:
        # 调用聊天服务
        chat_service = get_chat_service()

        response = await chat_service.chat(
            user_message=chat_message.message,
            user_id=current_user_id,
            config=config
        )

        # 检查是否生成了工作日志（根据内容判断）
        attachments = []
        content = response["content"]

        # 如果回复包含工作日志，生成下载附件
        if "# 工作日志" in content or "## 📅" in content:
            # 简单的附件生成逻辑
            # 实际应用中可能需要更复杂的解析
            attachment = {
                "type": "markdown",
                "filename": f"worklog_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                "content": content  # 前端会处理编码
            }
            attachments.append(attachment)

        return ChatResponse(
            content=content,
            role=response.get("role", "assistant"),
            metadata=response.get("metadata", {}),
            attachments=attachments
        )

    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"处理消息时出错: {str(e)}"
        )


@router.post("/generate-worklog")
async def generate_worklog(
    request: GenerateWorklogRequest,
    current_user_id: int = Depends(get_current_user_id)
) -> Dict[str, Any]:
    """生成工作日志

    直接生成工作日志，不通过 LLM 对话。

    Args:
        request: 生成工作日志请求
        current_user_id: 当前用户 ID

    Returns:
        包含工作日志内容和附件的响应
    """
    # 获取用户配置
    config = await db.get_one_by_field(UserConfigInDB, "user_id", current_user_id)

    if not config:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请先配置 GitLab 或 GitHub"
        )

    try:
        # 确定时间范围
        since_date = None
        until_date = None

        if request.since_date:
            since_date = parse_datetime(request.since_date)
        if request.until_date:
            until_date = parse_datetime(request.until_date)

        # 如果指定了时间范围描述，使用该描述
        if request.time_range:
            chat_service = get_chat_service()
            time_params = await chat_service.parse_time_request(f"获取{request.time_range}的提交")
            since_date = time_params.get("since_date")
            until_date = time_params.get("until_date")

        # 使用默认时间范围（本周）
        if not since_date or not until_date:
            from utils.datetime import get_week_range
            since_date, until_date = get_week_range()

        # 获取提交记录
        from mcp_servers import MCPServerFactory
        server = MCPServerFactory.get_default_server(config)

        commits = await server.get_commits(
            since_date=since_date,
            until_date=until_date,
            branch=request.branch,
            project_id=request.project_id
        )

        # 生成工作日志报告
        summary_service = get_summary_service()
        report = summary_service.generate_worklog_report(
            commits=commits,
            start_date=since_date,
            end_date=until_date
        )

        # 格式化为 Markdown
        markdown_content = summary_service.format_markdown(report)

        # 准备下载附件
        download_service = get_download_service()
        attachment = download_service.generate_attachment(report)

        return {
            "content": markdown_content,
            "metadata": {
                "total_commits": report.total_commits,
                "start_date": since_date.isoformat(),
                "end_date": until_date.isoformat(),
                "projects": report.projects
            },
            "attachments": [attachment]
        }

    except Exception as e:
        logger.error(f"Error generating worklog: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成工作日志时出错: {str(e)}"
        )


@router.get("/tools")
async def list_tools(
    current_user_id: int = Depends(get_current_user_id)
) -> Dict[str, Any]:
    """列出可用的工具

    Args:
        current_user_id: 当前用户 ID

    Returns:
        可用工具列表
    """
    # 获取用户配置
    config = await db.get_one_by_field(UserConfigInDB, "user_id", current_user_id)

    if not config:
        return {
            "tools": [],
            "message": "请先配置 GitLab 或 GitHub"
        }

    try:
        from mcp_servers import MCPServerFactory
        servers = MCPServerFactory.create_all_servers(config)

        all_tools = []
        for platform, server in servers.items():
            tools = await server.get_tools()
            all_tools.extend(tools)

        return {
            "tools": all_tools,
            "count": len(all_tools)
        }

    except Exception as e:
        logger.error(f"Error listing tools: {str(e)}")
        return {
            "tools": [],
            "error": str(e)
        }


@router.get("/health")
async def chat_health() -> Dict[str, str]:
    """聊天服务健康检查"""
    return {
        "status": "healthy",
        "service": "chat",
        "timestamp": datetime.now().isoformat()
    }
