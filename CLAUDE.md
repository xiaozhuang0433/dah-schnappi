# 工作日志系统说明

## ⚠️ 项目标识 - 永久记录

**项目名称（必须严格遵守）：**

```
英文: DahSchnappi
发音: dah-schnappi
来源: 德语 "Schnappi"（小鳄鱼）
Emoji: 🐊
```

**重要提醒：**
- ✅ 正确：DahSchnappi / dahschnappi
- ❌ 错误：DasSchnappi / dasschnappi / WorkScribe / OpenSchnappi / 任何其他变体

**所有引用项目名称的地方必须使用 "DahSchnappi"，不得擅自修改或更替。**

---

## 📁 目录结构

```
DahSchnappi/                     # 根目录
├── README.md                   # 项目说明（英文）
├── README_CN.md                # 项目说明（中文）
├── CLAUDE.md                   # 本文档，AI协作规约
├── docker-compose.yml          # Docker 编排配置
├── docs/                       # 📚 项目文档目录
│   ├── DEPLOYMENT.md           # 部署指南
│   ├── MIGRATION.md            # 数据迁移指南
│   └── template.md             # 月度工作日志模板
├── src/                        # 源代码目录
│   ├── backend/                # FastAPI 后端
│   │   ├── .env.example        # 后端环境变量模板
│   │   ├── Dockerfile          # 后端 Docker 镜像
│   │   ├── requirements.txt    # Python 依赖
│   │   └── main.py             # 应用入口
│   └── frontend/               # React 前端
└── work_report/                # 工作日志目录（仅工作日志系统使用）
    ├── YYYY-MM.md              # 当前活跃的月度日志
    └── archive/                # 归档目录
```

### 📚 文档目录规约

**根目录保留的文档：**
- ✅ `README.md` - 项目主说明（英文）
- ✅ `README_CN.md` - 项目主说明（中文）
- ✅ `CLAUDE.md` - AI协作规约（必读）

**其他所有文档统一放在 `docs/` 目录：**
- 部署指南、API文档、开发指南等
- 模板文件、示例文件
- 所有非README的技术文档

**遵循原则：**
1. 根目录保持简洁，只放核心说明文档
2. 详细文档统一管理在 `docs/` 下
3. 新增文档时自觉放入 `docs/`，除非是README类文件

### 🔐 环境变量文件规约

**后端专属配置：**
- ✅ `src/backend/.env.example` - 后端配置模板（唯一位置）
- ✅ `src/backend/.env` - 实际配置（手动创建，不提交）

**使用方式：**
```bash
# 手动运行
cd src/backend
cp .env.example .env
vim .env  # 编辑配置
python main.py

# Docker 运行
# 环境变量在 docker-compose.yml 中配置，或通过 .env 文件传入
docker-compose up -d
```

**注意：**
- ⚠️ `.env` 已在 `.gitignore` 中排除，不提交敏感信息
- ✅ `.env.example` 可以提交，作为配置模板

## 🎯 核心逻辑

### 1. 活跃日志 vs 归档日志

- **活跃日志**：直接放在 `work_report/` 根目录下，文件名格式 `YYYY-MM.md`
  - 参与年度分析
  - 用于生成PPT和统计数据
  - Claude 会读取这些文件来回答你的问题

- **归档日志**：移入 `work_report/archive/` 目录
  - 不再参与分析
  - 仅作为历史记录保存
  - 减少文件读取负担，提高分析效率

### 2. 归档时机

建议在以下情况将日志归档：
- ✅ 月度总结已完成，无需再修改
- ✅ 该月度数据已用于年度汇报
- ✅ 该项目/阶段已结束

### 3. 归档操作

**手动归档（推荐）**：
```bash
# Windows
move work_report\2025-06.md work_report\archive\

# Linux/Mac
mv work_report/2025-06.md work_report/archive/
```

**批量归档**：
```bash
# 归档去年的所有日志
move work_report\2025-*.md work_report\archive\
```

## 📝 工作日志填写规范

### 文件命名
- 格式：`YYYY-MM.md`
- 示例：`2026-01.md`、`2026-02.md`

### 日期格式
- Markdown标题：`## YYYY-MM-DD 星期X 天气图标`
- 保持一致性，便于脚本提取

### 内容分类
每个日报建议包含：
- ✅ **今日完成**：已完成的事项（使用 `- [x]` 标记）
- 🔄 **进行中**：进行中的事项（使用 `- [ ]` 标记）
- ⚠️ **遇到的问题**：问题和挑战
- 💡 **思考与总结**：技术思考、经验总结

### 月末必填
- 📊 月度统计数据
- 📝 月末总结
- 下月计划

## 🔧 辅助脚本使用

### Git提交记录获取

- **GitLab**: `src/fetch_commits_gitlab.py`
- **GitHub**: `src/fetch_commits_github.py`（待创建）

功能：
- 从 GitLab/GitHub API 获取提交记录
- 根据提交信息生成工作日志草稿
- 自动关联 Commit ID 到工作日志

**使用示例（GitLab）**：
```bash
cd src
python fetch_commits_gitlab.py
```

### 统计报告生成

位于 `src/generate_report.py`，功能：
- 扫描所有活跃日志文件
- 生成月度/年度统计数据
- 输出 Excel/JSON 格式报告
- 为年度PPT提供数据支持

**使用示例**：
```bash
cd src
python generate_report.py --year 2026 --format excel
```

## 🤖 与 Claude 的协作

### 常用指令示例

**1. 询问本月工作统计**
> "帮我统计一下2026年1月完成了多少任务"

**2. 生成月度总结**
> "根据我的工作日志，生成2026年1月的月度总结"

**3. 提取年度数据**
> "提取2026年所有工作日志中的关键数据，用于年度汇报"

**4. 根据Git记录补充日志**
> "用 src/fetch_commits_gitlab.py 获取本周的Git提交，帮我补充工作日志"

**5. 生成PPT大纲**
> "基于2026年的工作日志，生成年度汇报PPT的大纲结构"

### Claude 的工作范围

- ✅ 读取 `work_report/*.md`（活跃日志）
- ✅ 不读取 `work_report/archive/*`（归档日志）
- ✅ 读取和执行 `src/*.py` 脚本
- ✅ 帮助填写和优化工作日志
- ✅ 生成统计数据和汇报材料

## 📊 数据统计维度

系统可以自动提取以下数据：

### 工作量统计
- 每月完成任务数
- 每月代码提交次数
- 每月Bug修复数
- 每月工作天数

### 分类统计
- 按任务类型（开发/测试/文档/会议）
- 按项目分类
- 按技术栈分类

### 时间趋势
- 月度工作量趋势图
- 任务完成率变化
- 技术学习时间占比

### 质量指标
- Bug数量趋势
- 复现问题数量
- 技术债务积累

## 🎨 PPT 生成建议

### 年度汇报结构

1. **年度概览**（1-2页）
   - 年度核心数据
   - 关键成果时间线

2. **月度回顾**（6-12页）
   - 按季度或重要月份分组
   - 每月核心成果1-2个

3. **项目成果**（4-8页）
   - 重要项目详细介绍
   - 技术亮点和价值

4. **数据可视化**（3-5页）
   - 工作量趋势图
   - 技术栈分布
   - 成果对比

5. **个人成长**（2-3页）
   - 技术能力提升
   - 经验总结
   - 遇到的挑战与解决

6. **下年度规划**（1-2页）

### 转换工具

**Marp（推荐）**：
```bash
# 安装
npm install -g @marp-team/marp-cli

# 使用（在日志文件中添加 marp: true）
marp work_report/2026-01.md -o 2026-01.pptx
```

**Pandoc**：
```bash
pandoc work_report/2026-01.md -o output.pptx
```

## 📌 注意事项

1. **定期归档**：建议每季度或每半年归档一次旧日志
2. **备份重要**：定期备份整个 `work_report` 目录
3. **版本控制**：建议将此目录加入 Git 私有仓库
4. **隐私保护**：避免记录敏感信息（密码、密钥等）
5. **保持更新**：每天填写，不要积累太多未记录的工作

## 🔄 更新日志

- 2026-01-30：创建系统，定义基础结构和规范
