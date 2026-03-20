# 飞书项目进度管理机器人

一个基于飞书开放平台的智能项目管理机器人，通过群聊交互方式自动收集、记录和更新项目进度，集成 AI 解析能力，生成项目报表，提升团队协作效率。

## 功能特性

- **日报记录**：@机器人提交日报，自动存储并 AI 解析
- **进度自动更新**：AI 匹配日报内容与项目任务，自动更新完成度
- **周报生成**：一键汇总本周所有日报，生成结构化周报
- **进度查询**：随时查询项目整体进度、模块进度、个人进度
- **历史查询**：按日期/成员/模块查询历史日报
- **任务提醒**：截止前 3 天/1 天自动提醒，逾期每日提醒
- **风险预警**：自动检测连续无日报、任务风险等异常情况
- **Web 管理界面**：可视化管理项目、任务、日报、统计数据

## 技术栈

| 层次 | 技术 |
|------|------|
| 后端 | Python 3.11 + FastAPI + SQLAlchemy |
| 数据库 | PostgreSQL 15 |
| 缓存 | Redis 7 |
| AI | 硅基流动 API（Qwen2.5-7B-Instruct） |
| 前端 | React 18 + Ant Design 5 |
| 部署 | Docker + Docker Compose + Nginx |

## 快速开始

### 前置要求

- Docker 24+
- Docker Compose 2.20+
- 飞书企业自建应用（App ID + App Secret）
- 硅基流动 API Key

### 1. 克隆项目

```bash
git clone https://github.com/Deep-Octopus/feishu-project-bot.git
cd feishu-project-bot
```

### 2. 配置环境变量

```bash
cp .env.example .env
vim .env  # 填入实际配置
```

必填项：
```env
FEISHU_APP_ID=cli_xxxxxxxxxxxxxxxx
FEISHU_APP_SECRET=your_app_secret
FEISHU_VERIFICATION_TOKEN=your_token
FEISHU_ENCRYPT_KEY=your_encrypt_key
SILICONFLOW_API_KEY=sk-xxxxxxxx
DB_PASSWORD=your_strong_password
```

### 3. 启动服务

```bash
docker-compose up -d
```

### 4. 配置飞书回调地址

在飞书开放平台 → 事件订阅 → 请求地址配置：

```
http://your-server-ip/api/v1/feishu/callback
```

### 5. 访问管理界面

打开浏览器访问 `http://your-server-ip`

## 机器人命令

在飞书群内 @机器人 发送以下命令：

| 命令 | 功能 | 示例 |
|------|------|------|
| `【初始化】` | 初始化项目 | `@机器人 【初始化】` |
| `【日报】` | 提交日报 | `@机器人 【日报】今天完成了XX功能` |
| `【周报】` | 生成周报 | `@机器人 【周报】` |
| `【进度】` | 查询进度 | `@机器人 【进度】` 或 `@机器人 【进度】用户模块` |
| `【历史】` | 查询历史 | `@机器人 【历史】2024-03-01` 或 `@机器人 【历史】@张三 最近7天` |
| `【统计】` | 数据统计 | `@机器人 【统计】本月` |
| `【帮助】` | 查看帮助 | `@机器人 【帮助】` |

## 项目结构

```
auto_project/
├── backend/                 # 后端服务（FastAPI）
│   ├── app/
│   │   ├── api/            # API 路由
│   │   ├── core/           # 核心配置（数据库、Redis、设置）
│   │   ├── models/         # SQLAlchemy 数据模型
│   │   ├── services/       # 业务逻辑服务
│   │   ├── utils/          # 工具函数（消息卡片构建）
│   │   └── main.py         # FastAPI 入口
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # Web 管理界面（React）
│   ├── src/
│   │   ├── api/            # API 调用封装
│   │   ├── pages/          # 页面组件
│   │   └── App.jsx
│   ├── package.json
│   └── Dockerfile
├── config/                 # 配置文件
│   ├── config.example.yaml
│   └── nginx.conf
├── scripts/
│   ├── init_db.sql         # 数据库初始化
│   └── deploy.sh           # 部署脚本
├── .env.example
├── docker-compose.yml
└── README.md
```

## API 文档

启动服务后访问：`http://your-server-ip:8000/docs`

主要接口：

- `POST /api/v1/feishu/callback` — 飞书事件回调
- `GET/POST /api/v1/projects/` — 项目管理
- `GET/POST /api/v1/tasks/` — 任务管理
- `GET /api/v1/reports/` — 日报查询
- `GET /api/v1/statistics/overview` — 项目进度概览
- `GET /api/v1/statistics/stats` — 统计数据
- `GET /api/v1/config/` — 系统配置

## 部署说明

### 生产环境部署

```bash
# 1. 服务器安装 Docker
curl -fsSL https://get.docker.com | sh

# 2. 配置环境变量
cp .env.example .env && vim .env

# 3. 启动
docker-compose up -d

# 4. 查看日志
docker-compose logs -f backend
```

### 更新部署

```bash
bash scripts/deploy.sh
```

### 数据备份

```bash
docker-compose exec postgres pg_dump -U postgres feishu_bot > backup_$(date +%Y%m%d).sql
```

## 开发环境

### 后端

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

## 开源协议

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request。
