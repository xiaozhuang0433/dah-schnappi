<div align="center">

# 🐊 DahSchnappi

### AI 驱动的工作日志助手

**用 AI 解放你，告别繁琐的日报周报写作**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3-blue?logo=react)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3-blue?logo=typescript)](https://www.typescriptlang.org)
[![Python](https://img.shields.io/badge/Python-3.10+-yellow?logo=python)](https://www.python.org)
[![License](https://img.shields.io/badge/License-内部项目-red)](LICENSE)

**DahSchnappi** — 源自德语 "Schnappi"（小鳄鱼）🐊

[English](README.md) | [中文](README_CN.md)

</div>

---

## ✨ 核心特性

- 🤖 **AI 驱动**：利用大语言模型（Claude/OpenAI）自动生成工作日志
- 🔄 **Git 集成**：支持 GitLab/GitHub，用自然语言获取提交记录
- 🔐 **多用户支持**：每个用户独立配置和聊天历史隔离
- 🔒 **加密存储**：敏感 Token 使用 Fernet 对称加密存储
- 📱 **离线优先**：基于 IndexedDB 的聊天存储，支持离线访问
- 🎨 **现代界面**：React + TypeScript + Ant Design 打造精美 UI
- 🐳 **开箱即用**：Docker Compose 一键部署
- 🔌 **MCP 协议**：通过模型上下文协议扩展功能

---

## 🎯 产品愿景

> **从程序员到所有人** — DahSchnappi 致力于通过 AI 自动化，解放所有专业人士于繁琐的日报周报写作中。

**当前阶段**：基于 Git 提交记录生成工作日志（GitLab/GitHub）
**未来愿景**：支持所有工作类型 — 文档、演示、客户接待等

---

## 🚀 快速开始

### 前置要求

- Python 3.10+
- Node.js 18+
- Docker & Docker Compose（可选）

### 方式一：Docker 部署（推荐）

```bash
# 1. 克隆仓库
git clone <repo-url>
cd 工作日志

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 API 密钥

# 3. 使用 Docker Compose 部署
docker-compose up -d

# 4. 访问应用
# 前端：http://localhost:80
# 后端 API：http://localhost:8000
# API 文档：http://localhost:8000/docs
```

### 方式二：手动部署

**后端：**

```bash
# 创建虚拟环境
cd src/backend
python -m venv venv
source venv/bin/activate  # Windows：venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 运行
python main.py
```

**前端：**

```bash
# 安装依赖
cd src/frontend
npm install

# 运行开发服务器
npm run dev
```

---

## 📖 使用指南

### 1. 注册/登录

```bash
# 访问 http://localhost:80
# 点击"注册"创建新账户
# 或使用已有凭据登录
```

### 2. 配置 Git 平台

进入 **设置** → **Git 平台**：

- **GitLab**：输入 URL（如 `http://192.168.1.231`）和 Personal Access Token
- **GitHub**：输入用户名和 Personal Access Token

Token 会被加密并安全存储。

### 3. 生成工作日志

使用自然语言查询：

- "帮我获取本周的提交记录"
- "生成本月工作日志"
- "搜索包含 'bugfix' 的提交"

### 4. 下载导出

点击 **下载** 按钮导出为 Markdown 文件。

---

## 🏗️ 系统架构

### 架构概览

```
┌─────────────────────────────────────────────────────────┐
│                   React 前端                             │
│  - IndexedDB（用户隔离的聊天存储）                        │
│  - Zustand（状态管理）                                   │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP (JWT)
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   FastAPI 后端                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │  MCP 服务器（GitLab、GitHub、可扩展）            │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │  LLM 集成（Claude、OpenAI）                     │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │  用户管理（JWT 认证、加密配置）                  │   │
│  └─────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              DuckDB（用户数据与配置）                    │
│              内存缓存（基于 TTL）                        │
└─────────────────────────────────────────────────────────┘
```

### 技术栈

**后端：**
- FastAPI - 现代异步 Python Web 框架
- DuckDB - 嵌入式分析数据库
- MCP（模型上下文协议）- 可扩展工具调用
- Claude/OpenAI - 大语言模型集成
- JWT - 用户认证
- Fernet - 对称加密

**前端：**
- React 18 - UI 框架
- TypeScript - 类型安全
- Vite - 构建工具
- Ant Design - UI 组件库
- Dexie.js - IndexedDB 封装
- Zustand - 状态管理
- dayjs - 日期处理

---

## 📡 API 接口

### 认证接口

| 方法 | 端点 | 描述 |
|--------|----------|-------------|
| POST | `/api/auth/register` | 用户注册 |
| POST | `/api/auth/login` | 用户登录 |
| GET | `/api/auth/me` | 获取当前用户信息 |
| POST | `/api/auth/logout` | 用户登出 |

### 配置接口

| 方法 | 端点 | 描述 |
|--------|----------|-------------|
| GET | `/api/config` | 获取用户配置 |
| PUT | `/api/config` | 更新配置 |
| PATCH | `/api/config/gitlab` | 更新 GitLab 配置 |
| PATCH | `/api/config/github` | 更新 GitHub 配置 |
| DELETE | `/api/config` | 删除配置 |

### 聊天接口

| 方法 | 端点 | 描述 |
|--------|----------|-------------|
| POST | `/api/chat/message` | 发送聊天消息 |
| POST | `/api/chat/generate-worklog` | 直接生成工作日志 |
| GET | `/api/chat/tools` | 列出可用工具 |
| GET | `/api/chat/health` | 聊天服务健康检查 |

完整 API 文档请访问运行时的 `/docs` 页面。

---

## 🔧 配置说明

### 环境变量

```env
# ===== 必填项 =====
SECRET_KEY=your-secret-key-change-this
ENCRYPTION_KEY=your-encryption-key  # 生成方法：python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# ===== LLM 提供商（至少配置一个）=====
ANTHROPIC_API_KEY=your-anthropic-api-key  # Claude
OPENAI_API_KEY=your-openai-api-key        # OpenAI（可选）

# ===== 可选项 =====
LLM_PROVIDER=claude                       # claude | openai
LLM_MODEL=claude-sonnet-4-5-20250929      # 使用的模型
DATABASE_IMPLEMENTATION=duckdb            # duckdb | postgresql
CACHE_IMPLEMENTATION=memory               # memory | redis
```

### GitLab Token 配置

1. 进入 GitLab → 设置 → 访问令牌
2. 创建令牌，勾选 `read_api` 和 `read_repository` 权限
3. 复制令牌并粘贴到 DahSchnappi 设置中

### GitHub Token 配置

1. 进入 GitHub → 设置 → 开发者设置 → Personal access tokens
2. 生成新令牌（经典版），勾选 `repo` 权限
3. 复制令牌并粘贴到 DahSchnappi 设置中

---

## 📦 项目结构

```
工作日志/                         # Monorepo 根目录
├── src/
│   ├── backend/                # FastAPI 后端
│   │   ├── main.py             # 应用入口
│   │   ├── config/             # 配置
│   │   ├── infrastructure/     # 数据库和缓存抽象层
│   │   ├── core/               # 核心业务逻辑
│   │   ├── services/           # 服务层（聊天、配置、摘要）
│   │   ├── auth/               # JWT 认证
│   │   ├── api/                # API 路由
│   │   ├── llm/                # LLM 客户端（Claude、OpenAI）
│   │   ├── mcp_servers/        # MCP 服务器（GitLab、GitHub）
│   │   └── utils/              # 工具函数
│   │
│   └── frontend/               # React 前端
│       ├── src/
│       │   ├── db/             # IndexedDB 层
│       │   ├── store/          # Zustand 状态管理
│       │   ├── services/       # API 客户端
│       │   └── components/     # React 组件
│       └── package.json
│
├── tests/                      # 测试文件
├── data/                       # DuckDB 数据文件
├── logs/                       # 应用日志
├── docker-compose.yml          # Docker 编排
├── Dockerfile                  # 后端 Docker 镜像
├── .env.example                # 环境变量模板
├── DEPLOYMENT.md               # 部署指南
└── README.md                   # 本文件
```

---

## 🧪 测试

```bash
# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=src tests/

# 运行集成测试
pytest tests/integration/

# 运行特定测试文件
pytest tests/test_database.py
```

---

## 🚢 部署

### 生产环境检查清单

- [ ] 设置强密码 `SECRET_KEY` 和 `ENCRYPTION_KEY`
- [ ] 配置 LLM API 密钥（Claude/OpenAI）
- [ ] 启用 HTTPS
- [ ] 设置防火墙规则
- [ ] 配置数据备份
- [ ] 设置监控告警
- [ ] 审查 CORS 设置

详细部署说明请参考 [DEPLOYMENT.md](DEPLOYMENT.md)。

---

## 🔐 安全性

- **加密存储**：Git Token 使用 Fernet 加密
- **JWT 认证**：基于令牌的认证，可配置过期时间
- **用户隔离**：每个用户数据完全隔离
- **CORS 保护**：可配置的跨域策略
- **SQL 注入防护**：通过 ORM 参数化查询

---

## 🛣️ 发展路线图

### 当前已完成 ✅
- Git 提交记录获取（GitLab/GitHub）
- 自然语言工作日志生成
- 多用户支持与加密配置
- 离线优先的聊天存储

### 未来计划 🚧
- 更多 Git 平台（Gitea、Bitbucket）
- Jira 集成
- 文档分析（PDF、Word）
- 日历集成
- 自定义 LLM 微调
- 移动应用（React Native）

---

## 🤝 贡献

本项目当前为内部项目。如有问题或建议，请联系开发团队。

---

## 📄 许可证

内部项目，版权所有。

---

## 📞 获取支持

如有问题或疑问：
- 📧 邮箱：[support@example.com]
- 📚 文档：[DEPLOYMENT.md](DEPLOYMENT.md)
- 🐛 问题追踪：[GitHub Issues](https://github.com/xxx/issues)

---

<div align="center">

**用 ❤️ 打造，为你解放于繁琐的报表工作**

</div>
