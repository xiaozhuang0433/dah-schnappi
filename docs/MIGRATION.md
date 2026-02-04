# 数据库迁移指南

## 从 DuckDB 迁移到 SQLite/PostgreSQL/MySQL

### 为什么要迁移？

**DuckDB** 是 OLAP（分析型）数据库，适合数据分析场景，不适合事务处理。

**你的项目需求**：
- ✅ 用户注册、登录（事务）
- ✅ 配置增删改查（事务）
- ✅ 聊天记录存储（事务）
- ✅ 多用户并发（事务）

**更适合的数据库**：
- **SQLite** - 嵌入式，适合开发/小规模
- **PostgreSQL** - 生产级，适合大规模
- **MySQL** - 生产级，广泛使用

---

## 数据库选择指南

### SQLite ⭐⭐⭐⭐
**最适合**：开发环境、中小规模应用

```env
DATABASE_IMPLEMENTATION=sqlite
SQLITE_PATH=data/dahschnappi.db
```

**优点**：
- ✅ 零配置，开箱即用
- ✅ 单文件，易于备份
- ✅ ACID 事务完整
- ✅ Python 内置支持
- ✅ 适合 < 1000 用户

**缺点**：
- ❌ 单写锁（并发受限）
- ❌ 不支持网络访问

---

### PostgreSQL ⭐⭐⭐⭐⭐
**最适合**：生产环境、大规模应用

```env
DATABASE_IMPLEMENTATION=postgresql
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DATABASE=dahschnappi
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-password
```

**优点**：
- ✅ 企业级事务支持
- ✅ 高并发读写
- ✅ 丰富的数据类型
- ✅ 完整的索引支持
- ✅ 适合 > 1000 用户

**缺点**：
- ❌ 需要额外部署
- ❌ 资源占用较大

---

### MySQL ⭐⭐⭐⭐
**最适合**：生产环境、传统企业应用

```env
DATABASE_IMPLEMENTATION=mysql
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=dahschnappi
MYSQL_USER=root
MYSQL_PASSWORD=your-password
MYSQL_CHARSET=utf8mb4
```

**优点**：
- ✅ 广泛使用，文档丰富
- ✅ 高性能
- ✅ 支持主从复制
- ✅ 适合 > 1000 用户

**缺点**：
- ❌ 需要额外部署
- ❌ 某些高级特性不如 PG

---

## 快速开始

### 开发环境（SQLite - 默认）

```bash
# 1. 安装依赖
cd src/backend
pip install -r requirements.txt

# 2. 配置环境
cp ../../.env.example ../../.env
# 编辑 .env，确保 DATABASE_IMPLEMENTATION=sqlite

# 3. 运行
python main.py
# 数据库会自动创建在 data/dahschnappi.db
```

### 生产环境（PostgreSQL）

#### 1. 安装 PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

**Windows:**
下载安装程序：https://www.postgresql.org/download/windows/

#### 2. 创建数据库和用户

```bash
# 切换到 postgres 用户
sudo -u postgres psql

# 在 PostgreSQL shell 中执行：
CREATE DATABASE dahschnappi;
CREATE USER dahschnappi WITH PASSWORD 'your-password';
GRANT ALL PRIVILEGES ON DATABASE dahschnappi TO dahschnappi;
\q
```

#### 3. 配置应用

```env
# .env
DATABASE_IMPLEMENTATION=postgresql
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DATABASE=dahschnappi
POSTGRES_USER=dahschnappi
POSTGRES_PASSWORD=your-password
```

#### 4. 运行应用

```bash
python main.py
# 表会自动创建
```

---

### 生产环境（MySQL）

#### 1. 安装 MySQL

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install mysql-server
sudo systemctl start mysql
```

**macOS:**
```bash
brew install mysql
brew services start mysql
```

**Windows:**
下载安装程序：https://dev.mysql.com/downloads/mysql/

#### 2. 创建数据库和用户

```bash
# 登录 MySQL
mysql -u root -p

# 在 MySQL shell 中执行：
CREATE DATABASE dahschnappi CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'dahschnappi'@'localhost' IDENTIFIED BY 'your-password';
GRANT ALL PRIVILEGES ON dahschnappi.* TO 'dahschnappi'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### 3. 配置应用

```env
# .env
DATABASE_IMPLEMENTATION=mysql
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=dahschnappi
MYSQL_USER=dahschnappi
MYSQL_PASSWORD=your-password
MYSQL_CHARSET=utf8mb4
```

#### 4. 运行应用

```bash
python main.py
# 表会自动创建
```

---

## Docker 部署

### 使用 SQLite（默认）

```bash
docker-compose up -d
```

### 使用 PostgreSQL

```yaml
# docker-compose.yml
services:
  backend:
    environment:
      - DATABASE_IMPLEMENTATION=postgresql
      - POSTGRES_HOST=postgres
      - POSTGRES_USER=dahschnappi
      - POSTGRES_PASSWORD=your-password
    depends_on:
      - postgres

  postgres:
    image: postgres:16-alpine
    environment:
      - POSTGRES_DB=dahschnappi
      - POSTGRES_USER=dahschnappi
      - POSTGRES_PASSWORD=your-password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### 使用 MySQL

```yaml
# docker-compose.yml
services:
  backend:
    environment:
      - DATABASE_IMPLEMENTATION=mysql
      - MYSQL_HOST=mysql
      - MYSQL_USER=dahschnappi
      - MYSQL_PASSWORD=your-password
    depends_on:
      - mysql

  mysql:
    image: mysql:8.0
    environment:
      - MYSQL_DATABASE=dahschnappi
      - MYSQL_USER=dahschnappi
      - MYSQL_PASSWORD=your-password
      - MYSQL_ROOT_PASSWORD=root-password
    volumes:
      - mysql_data:/var/lib/mysql

volumes:
  mysql_data:
```

---

## 表结构

所有数据库实现都自动创建相同的表结构：

### users 表
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,           -- SQLite: AUTOINCREMENT, PG: SERIAL, MySQL: AUTO_INCREMENT
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### user_configs 表
```sql
CREATE TABLE user_configs (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE,
    gitlab_url VARCHAR(255),
    gitlab_token VARCHAR(255),
    github_username VARCHAR(100),
    github_token VARCHAR(255),
    default_platform VARCHAR(20) DEFAULT 'gitlab',
    include_branches BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

---

## 数据迁移（如果有旧数据）

### 从 DuckDB 导出数据

```python
# export_from_duckdb.py
import duckdb
import json

# 连接 DuckDB
conn = duckdb.connect('data/worklog.db')

# 导出 users
users = conn.execute("SELECT * FROM users").fetchall()
with open('users.json', 'w') as f:
    json.dump([dict(row) for row in users], f)

# 导出 user_configs
configs = conn.execute("SELECT * FROM user_configs").fetchall()
with open('user_configs.json', 'w') as f:
    json.dump([dict(row) for row in configs], f)

conn.close()
```

### 导入到新数据库

```python
# import_to_new_db.py
from src.infrastructure.database import db
import json

# 连接新数据库
db.connect()

# 导入 users
with open('users.json', 'r') as f:
    users = json.load(f)
    for user in users:
        db.insert(User, user)

# 导入 user_configs
with open('user_configs.json', 'r') as f:
    configs = json.load(f)
    for config in configs:
        db.insert(UserConfig, config)

db.disconnect()
```

---

## 性能对比

| 数据库 | 读性能 | 写性能 | 并发 | 内存占用 |
|--------|--------|--------|------|----------|
| SQLite | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| PostgreSQL | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| MySQL | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## 常见问题

### Q: 如何切换数据库？
A: 修改 `.env` 中的 `DATABASE_IMPLEMENTATION` 即可，代码无需改动。

### Q: 数据会被迁移吗？
A: 不会自动迁移，需要手动导出/导入（见上方数据迁移部分）。

### Q: SQLite 够用吗？
A: 对于 < 1000 用户的应用，SQLite 完全够用。

### Q: PostgreSQL 和 MySQL 选哪个？
A: 推荐 PostgreSQL，功能更强大，社区更活跃。

---

## 🎉 完成！

现在你的应用支持三种数据库了：
- **SQLite** - 开发/小规模（默认）
- **PostgreSQL** - 生产环境
- **MySQL** - 生产环境

根据你的需求选择合适的数据库！🐊
