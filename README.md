<div align="center">

# 🐊 DahSchnappi

### AI-Powered Work Log Assistant

**Liberate yourself from tedious daily/weekly report writing**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3-blue?logo=react)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3-blue?logo=typescript)](https://www.typescriptlang.org)
[![Python](https://img.shields.io/badge/Python-3.10+-yellow?logo=python)](https://www.python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**DahSchnappi** — From German "Schnappi" (little crocodile) 🐊

[English](README.md) | [中文](README_CN.md)

</div>

---

## ✨ Features

- 🤖 **AI-Powered**: Leverage LLMs (Claude/OpenAI) to generate work logs automatically
- 🔄 **Git Integration**: Fetch commits from GitLab/GitHub with natural language queries
- 🔐 **Multi-User Support**: Isolated configurations and chat history per user
- 🔒 **Encrypted Storage**: Sensitive tokens encrypted with Fernet symmetric encryption
- 📱 **Offline-First**: IndexedDB-based chat storage with offline support
- 🎨 **Modern UI**: Beautiful React + TypeScript + Ant Design interface
- 🐳 **Docker Ready**: One-command deployment with Docker Compose
- 🔌 **MCP Protocol**: Extensible via Model Context Protocol servers

---

## 🎯 Vision

> **From programmers to everyone** — DahSchnappi aims to liberate all professionals from tedious daily/weekly report writing through AI automation.

**Current**: Git commit-based work log generation (GitLab/GitHub)
**Future**: All types of work — documents, presentations, customer interactions, and more

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Docker & Docker Compose (optional)

### Option 1: Docker Deployment (Recommended)

```bash
# 1. Clone the repository
git clone <repo-url>
cd 工作日志

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 3. Deploy with Docker Compose
docker-compose up -d

# 4. Access the application
# Frontend: http://localhost:80
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Manual Setup

**Backend:**

```bash
# Create virtual environment
cd src/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run
python main.py
```

**Frontend:**

```bash
# Install dependencies
cd src/frontend
npm install

# Run dev server
npm run dev
```

---

## 📖 Usage

### 1. Register/Login

```bash
# Access http://localhost:80
# Click "Register" to create an account
# Or login with existing credentials
```

### 2. Configure Git Platform

Navigate to **Settings** → **Git Platform**:

- **GitLab**: Enter URL (e.g., `http://192.168.1.231`) and Personal Access Token
- **GitHub**: Enter username and Personal Access Token

Tokens are encrypted and stored securely.

### 3. Generate Work Log

Use natural language queries:

- "帮我获取本周的提交记录" (Help me get this week's commits)
- "生成本月工作日志" (Generate this month's work log)
- "搜索包含 'bugfix' 的提交" (Search commits containing 'bugfix')

### 4. Download

Click the **Download** button to export as Markdown file.

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────┐
│                   React Frontend                         │
│  - IndexedDB (user-isolated chat storage)               │
│  - Zustand (state management)                           │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP (JWT)
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   FastAPI Backend                        │
│  ┌─────────────────────────────────────────────────┐   │
│  │  MCP Servers (GitLab, GitHub, Extensible)       │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │  LLM Integration (Claude, OpenAI)               │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │  User Management (JWT, Encrypted Config)        │   │
│  └─────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              DuckDB (User Data & Configs)               │
│              Memory Cache (TTL-based)                   │
└─────────────────────────────────────────────────────────┘
```

### Tech Stack

**Backend:**
- FastAPI - Modern async Python web framework
- DuckDB - Embedded analytical database
- MCP (Model Context Protocol) - Extensible tool calling
- Claude/OpenAI - LLM integration
- JWT - Authentication
- Fernet - Symmetric encryption

**Frontend:**
- React 18 - UI framework
- TypeScript - Type safety
- Vite - Build tool
- Ant Design - UI components
- Dexie.js - IndexedDB wrapper
- Zustand - State management
- dayjs - Date utilities

---

## 📡 API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | User registration |
| POST | `/api/auth/login` | User login |
| GET | `/api/auth/me` | Get current user info |
| POST | `/api/auth/logout` | User logout |

### Configuration

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/config` | Get user configuration |
| PUT | `/api/config` | Update configuration |
| PATCH | `/api/config/gitlab` | Update GitLab config |
| PATCH | `/api/config/github` | Update GitHub config |
| DELETE | `/api/config` | Delete configuration |

### Chat

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat/message` | Send chat message |
| POST | `/api/chat/generate-worklog` | Generate work log directly |
| GET | `/api/chat/tools` | List available tools |
| GET | `/api/chat/health` | Chat service health check |

For full API documentation, visit `/docs` when running.

---

## 🔧 Configuration

### Environment Variables

```env
# ===== Required =====
SECRET_KEY=your-secret-key-change-this
ENCRYPTION_KEY=your-encryption-key  # Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# ===== LLM Providers (at least one required) =====
ANTHROPIC_API_KEY=your-anthropic-api-key  # For Claude
OPENAI_API_KEY=your-openai-api-key        # For OpenAI (optional)

# ===== Optional =====
LLM_PROVIDER=claude                       # claude | openai
LLM_MODEL=claude-sonnet-4-5-20250929      # Model to use
DATABASE_IMPLEMENTATION=duckdb            # duckdb | postgresql
CACHE_IMPLEMENTATION=memory               # memory | redis
```

### GitLab Token Setup

1. Go to GitLab → Settings → Access Tokens
2. Create token with `read_api` and `read_repository` scopes
3. Copy token and paste into DahSchnappi settings

### GitHub Token Setup

1. Go to GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token (classic) with `repo` scope
3. Copy token and paste into DahSchnappi settings

---

## 📦 Project Structure

```
工作日志/                         # Monorepo root
├── src/
│   ├── backend/                # FastAPI Backend
│   │   ├── main.py             # Application entry
│   │   ├── config/             # Configuration
│   │   ├── infrastructure/     # Database & Cache abstraction
│   │   ├── core/               # Business logic
│   │   ├── services/           # Services (chat, config, summary)
│   │   ├── auth/               # JWT Authentication
│   │   ├── api/                # API routes
│   │   ├── llm/                # LLM clients (Claude, OpenAI)
│   │   ├── mcp_servers/        # MCP Servers (GitLab, GitHub)
│   │   └── utils/              # Utilities
│   │
│   └── frontend/               # React Frontend
│       ├── src/
│       │   ├── db/             # IndexedDB layer
│       │   ├── store/          # Zustand stores
│       │   ├── services/       # API client
│       │   └── components/     # React components
│       └── package.json
│
├── tests/                      # Test files
├── data/                       # DuckDB data files
├── logs/                       # Application logs
├── docker-compose.yml          # Docker orchestration
├── Dockerfile                  # Backend Docker image
├── .env.example                # Environment template
├── DEPLOYMENT.md               # Deployment guide
└── README.md                   # This file
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run integration tests
pytest tests/integration/

# Run specific test file
pytest tests/test_database.py
```

---

## 🚢 Deployment

### Production Checklist

- [ ] Set strong `SECRET_KEY` and `ENCRYPTION_KEY`
- [ ] Configure LLM API keys (Claude/OpenAI)
- [ ] Enable HTTPS
- [ ] Set up firewall rules
- [ ] Configure backups
- [ ] Set up monitoring
- [ ] Review CORS settings

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

---

## 🔐 Security

- **Encrypted Storage**: Git tokens encrypted with Fernet
- **JWT Authentication**: Token-based auth with configurable expiration
- **User Isolation**: Complete data separation per user
- **CORS Protection**: Configurable cross-origin policies
- **SQL Injection Prevention**: Parameterized queries via ORM

---

## 🛣️ Roadmap

### Current ✅
- Git commit fetching (GitLab/GitHub)
- Natural language work log generation
- Multi-user support with encrypted configs
- Offline-first chat storage

### Future 🚧
- More Git platforms (Gitea, Bitbucket)
- Jira integration
- Document analysis (PDF, Word)
- Calendar integration
- Custom LLM fine-tuning
- Mobile app (React Native)

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 Support

For issues or questions:
- 📧 Email: [support@example.com]
- 📚 Documentation: [DEPLOYMENT.md](DEPLOYMENT.md)
- 🐛 Issue Tracker: [GitHub Issues](https://github.com/xiaozhuang0433/dah-schnappi/issues)

---

<div align="center">

**Made with ❤️ to liberate you from tedious reports**

</div>
