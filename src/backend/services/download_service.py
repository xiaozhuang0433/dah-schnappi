"""
Download Service

下载服务，处理工作日志文件的生成和下载。
"""
import base64
import uuid
from typing import Dict, Any
from datetime import datetime
from pathlib import Path

from ..summary_service import get_summary_service
from ..core.models import WorkLogReport
from ..utils.logger import get_logger


logger = get_logger(__name__)


class DownloadService:
    """下载服务

    生成工作日志文件并准备下载。
    """

    def __init__(self):
        """初始化服务"""
        self.summary_service = get_summary_service()

    def generate_markdown_file(
        self,
        report: WorkLogReport,
        filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """生成 Markdown 文件

        Args:
            report: 工作日志报告
            filename: 文件名（可选）

        Returns:
            包含文件信息的字典
        """
        # 生成 Markdown 内容
        markdown_content = self.summary_service.format_markdown(report)

        # 生成文件名
        if filename is None:
            start_str = report.start_date.strftime("%Y%m%d")
            end_str = report.end_date.strftime("%Y%m%d")
            filename = f"worklog_{start_str}_to_{end_str}.md"

        return {
            "type": "markdown",
            "filename": filename,
            "content": markdown_content,
            "size": len(markdown_content.encode('utf-8')),
            "created_at": datetime.now().isoformat()
        }

    def encode_content(self, content: str) -> str:
        """将内容编码为 Base64

        Args:
            content: 原始内容

        Returns:
            Base64 编码的内容
        """
        content_bytes = content.encode('utf-8')
        return base64.b64encode(content_bytes).decode('ascii')

    def prepare_download(
        self,
        report: WorkLogReport,
        filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """准备下载

        生成文件并编码为 Base64。

        Args:
            report: 工作日志报告
            filename: 文件名（可选）

        Returns:
            包含文件信息的字典，content 为 Base64 编码
        """
        # 生成文件
        file_info = self.generate_markdown_file(report, filename)

        # 编码内容
        file_info["content"] = self.encode_content(file_info["content"])

        return file_info

    def prepare_download_from_markdown(
        self,
        markdown: str,
        filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """从 Markdown 内容准备下载

        Args:
            markdown: Markdown 内容
            filename: 文件名（可选）

        Returns:
            包含文件信息的字典
        """
        if filename is None:
            today = datetime.now().strftime("%Y%m%d")
            filename = f"worklog_{today}.md"

        return {
            "type": "markdown",
            "filename": filename,
            "content": self.encode_content(markdown),
            "size": len(markdown.encode('utf-8')),
            "created_at": datetime.now().isoformat()
        }

    def save_to_file(
        self,
        content: str,
        filepath: str
    ) -> None:
        """保存内容到文件

        Args:
            content: 文件内容
            filepath: 文件路径
        """
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Saved work log to: {filepath}")

    def save_report_to_file(
        self,
        report: WorkLogReport,
        filepath: str
    ) -> None:
        """保存报告到文件

        Args:
            report: 工作日志报告
            filepath: 文件路径
        """
        markdown_content = self.summary_service.format_markdown(report)
        self.save_to_file(markdown_content, filepath)

    def generate_attachment(
        self,
        report: WorkLogReport,
        filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """生成附件对象（用于 API 响应）

        Args:
            report: 工作日志报告
            filename: 文件名（可选）

        Returns:
            附件对象
        """
        file_info = self.prepare_download(report, filename)

        return {
            "type": file_info["type"],
            "filename": file_info["filename"],
            "content": file_info["content"],  # Base64 编码
            "size": file_info["size"]
        }


# 全局单例
_download_service: Optional[DownloadService] = None


def get_download_service() -> DownloadService:
    """获取下载服务实例"""
    global _download_service
    if _download_service is None:
        _download_service = DownloadService()
    return _download_service
