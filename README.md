# 项目管家 (Project Manager)

个人项目管理微信小程序 — 轻量级的项目进度追踪工具。

**上线地址**: [https://pm.maengyi.top](https://pm.maengyi.top)

---

## 功能特性

- **项目看板** — 创建/编辑/删除项目，支持四种状态：进行中、暂停、已完成、已取消
- **多级任务树** — 无限层级子任务分解，父任务进度自动汇总子任务进度
- **甘特图** — 传统图表模式和简约时间轴模式，手机上也能看清
- **进度追踪** — 手动更新任务进度 0-100%，自动加权汇总项目总进度
- **逾期提醒** — 自动标记已过截止日期的任务
- **只看模式** — 分享链接给他人，访客只读不可编辑
- **统计概览** — 总览所有项目的进度和逾期情况

## 技术栈

| 层 | 技术 |
|---|---|
| **前端** | 微信小程序原生 (WXML / WXSS / JavaScript) |
| **后端** | Python Flask + Gunicorn |
| **数据库** | PostgreSQL |
| **部署** | Nginx + HTTPS (Let's Encrypt) on 阿里云 |

## 项目结构

```
project-manager/
├── backend/                  # Flask 后端
│   ├── app.py                # 应用入口 + 配置
│   ├── models.py             # 数据模型 (Project, Task)
│   ├── requirements.txt      # Python 依赖
│   ├── .env                  # 数据库配置 (不上传到 Git)
│   └── routes/
│       ├── projects.py       # 项目 CRUD API
│       ├── tasks.py          # 任务 CRUD + 树形结构 API
│       └── stats.py          # 统计 API
├── miniprogram/              # 微信小程序前端
│   ├── app.js / app.json     # 小程序全局配置
│   ├── pages/
│   │   ├── index/            # 首页 — 项目列表
│   │   ├── project/          # 项目详情 — 任务树 + 甘特图
│   │   ├── task/             # 任务编辑
│   │   ├── share/            # 只看模式分享页
│   │   └── stats/            # 统计概览
│   ├── components/           # 公共组件
│   └── utils/
│       └── api.js            # API 封装
├── start_pm.py               # 生产环境启动脚本 (Gunicorn)
├── pm_manager.conf           # Nginx 配置
└── .gitignore
```

## 快速部署

### 前置条件

- Python 3.11+
- PostgreSQL
- Nginx
- 域名 + SSL 证书 (Let's Encrypt)

### 1. 后端部署

```bash
# 安装依赖
cd backend
pip install -r requirements.txt

# 配置环境变量 (示例)
cat > .env << EOF
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=project_manager
DB_USER=pm_user
DB_PASS=your_password
SECRET_KEY=your-secret-key
EOF

# 启动 (开发)
python app.py

# 启动 (生产)
python3.11 start_pm.py
```

### 2. 数据库初始化

PostgreSQL 数据库会自动创建表结构：
```sql
CREATE DATABASE project_manager;
CREATE USER pm_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE project_manager TO pm_user;
```

### 3. Nginx 配置

将 `pm_manager.conf` 中的 `server_name` 修改为你的域名，证书路径改为你的 SSL 证书路径，然后：
```bash
sudo ln -s /etc/nginx/sites-available/pm_manager.conf /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

### 4. 小程序配置

在微信开发者工具中：
1. 打开 `miniprogram/` 目录
2. 修改 `project.config.json` 中的 `appid` 为你的微信小程序 AppID
3. 修改 `app.js` 中的 `baseUrl` 为你的后端域名
4. 在微信公众平台 → 开发 → 开发设置中配置服务器域名

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/projects | 项目列表 |
| POST | /api/projects | 创建项目 |
| GET | /api/projects/:id | 项目详情 (含任务树) |
| PUT | /api/projects/:id | 更新项目 |
| DELETE | /api/projects/:id | 删除项目 |
| GET | /api/projects/:id/share | 获取分享数据 |
| GET | /api/tasks/tree/:projectId | 任务树数据 |
| GET | /api/tasks/gantt/:projectId | 甘特图数据 |
| POST | /api/tasks | 创建任务 |
| PUT | /api/tasks/:id | 更新任务 |
| DELETE | /api/tasks/:id | 删除任务 |
| GET | /api/stats/overview | 统计概览 |
| GET | /api/health | 健康检查 |

## 数据模型

### Project
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| name | String(200) | 项目名称 |
| description | Text | 项目描述 |
| status | String(20) | active/paused/completed/cancelled |
| start_date | Date | 开始日期 |
| end_date | Date | 结束日期 |
| progress | (计算) | 子任务进度加权平均 |
| overdue_count | (计算) | 逾期任务数 |

### Task
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| project_id | Integer | 所属项目 (FK) |
| parent_id | Integer | 父任务 (FK, 自引用) |
| title | String(300) | 任务标题 |
| status | String(20) | todo/in_progress/completed/cancelled |
| priority | Integer | 0=P0 ~ 3=P3 |
| progress | Integer | 进度 0-100 |
| start_date | Date | 开始日期 |
| deadline | Date | 截止日期 |
| assignee | String(100) | 负责人 |
| remark | Text | 每日备注 |
| sort_order | Integer | 排序序号 |
| progress | (计算) | 有子任务时自动汇总 |

## 许可

MIT License
