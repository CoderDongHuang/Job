# 智析招聘 - 招聘数据分析与技能洞察系统

## 项目概述

智析招聘是一个基于大数据分析的招聘数据分析与技能洞察系统，通过分析招聘数据，为求职者提供技能趋势分析、薪资预测和职业发展建议。

## 功能特性

- **职位搜索与分析**：多维度职位搜索，智能匹配推荐
- **技能分析**：自动识别职位描述中的技能要求
- **薪资预测**：基于技能组合预测市场薪资水平
- **数据分析**：可视化展示招聘市场的各种趋势
- **个性化推荐**：为用户提供定制化的职业发展建议

## 技术栈

### 开发工具栈
- **版本控制**: Git (分布式版本控制系统，支持团队协作开发)
- **代码托管**: GitHub (代码托管平台，支持项目管理)

### 后端技术栈
- **Web框架**: FastAPI (高性能异步框架，自动生成API文档)
- **ORM工具**: SQLAlchemy (Python ORM工具，简化数据库操作)
- **服务器**: Uvicorn (ASGI服务器，支持异步处理)
- **数据库**: MySQL (关系型数据库，性能稳定，支持复杂查询)
- **数据处理**: Pandas、NumPy (数据分析和处理)

### 前端技术栈
- **框架**: Vue 3 (渐进式JavaScript框架，组合式API便于逻辑组织)
- **UI组件库**: Element Plus (基于Vue 3的UI组件库，提供丰富的界面元素)
- **图表库**: ECharts (数据可视化库，支持多种图表类型展示)
- **构建工具**: Vite (前端构建工具，支持热重载和快速开发)

## 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- MySQL 5.7+ (如果使用MySQL)

### 数据库设置
1. 使用提供的SQL文件创建MySQL数据库:
   ```bash
   mysql -u root -p < create_mysql_tables.sql
   ```

2. 或者手动创建数据库:
   ```sql
   CREATE DATABASE job_analysis CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

### 后端启动

```bash
# 安装Python依赖
pip install -r requirements.txt
# 如使用MySQL，还需安装:
pip install PyMySQL cryptography

# 设置数据库连接（可选，默认连接到本地MySQL的job_analysis数据库）
export DATABASE_URL="mysql+pymysql://username:password@localhost:3306/job_analysis"

# 初始化数据库表结构
python init_db.py

# 填充示例数据
python populate_data.py

# 启动后端服务
cd backend
uvicorn main:app --reload
```

### 前端启动

```bash
# 安装前端依赖
cd frontend
npm install

# 启动开发服务器
npm run dev
```

## API 接口

### 职位相关接口
- `GET /api/v1/jobs/` - 获取职位列表
- `POST /api/v1/jobs/` - 创建职位
- `GET /api/v1/jobs/{id}` - 获取指定职位
- `PUT /api/v1/jobs/{id}` - 更新职位
- `DELETE /api/v1/jobs/{id}` - 删除职位

### 技能分析接口
- `POST /api/v1/skills/analyze` - 分析技能
- `GET /api/v1/skills/trends` - 获取技能趋势
- `POST /api/v1/skills/extract` - 从文本提取技能

### 数据分析接口
- `GET /api/v1/analysis/salary` - 薪资分析
- `GET /api/v1/analysis/city` - 城市分析
- `GET /api/v1/analysis/experience` - 经验分析
- `GET /api/v1/analysis/industry` - 行业分析

## 项目结构

```
Job/
├── backend/                 # 后端代码
│   ├── api/                 # API路由
│   ├── models/              # 数据模型
│   ├── schemas/             # Pydantic模型
│   ├── database/            # 数据库配置
│   ├── utils/               # 工具函数
│   ├── core/                # 核心业务逻辑
│   └── main.py              # 主应用入口
├── frontend/                # 前端代码
│   ├── src/                 # 源代码
│   │   ├── views/           # 页面组件
│   │   ├── components/      # 通用组件
│   │   ├── router/          # 路由配置
│   │   └── assets/          # 静态资源
│   └── public/              # 静态文件
├── requirements.txt         # Python依赖
├── package.json             # Node.js依赖
└── init_db.py               # 数据库初始化脚本
```

## 部署

### 生产环境部署

```bash
# 构建前端
cd frontend
npm run build

# 启动后端服务
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 贡献指南

欢迎提交Issue和Pull Request来帮助改进这个项目。

## 许可证

本项目仅供学习交流使用。

## 联系方式

如有问题，请联系项目维护者。