# 非诚勿宠宠物店全栈综合服务平台 (Pet Store System)

本项目是一个为宠物店量身定制的全栈商业系统。系统采用前后端分离架构，支持 PC 网页端与微信小程序双端访问，且双端均通过角色权限控制（RBAC）同时支持“顾客服务”与“内部管理”功能。

## 🛠 技术栈
- **后端 (backend):** Python 3.x + FastAPI + MySQL + SQLAlchemy
- **PC 网页端 (web-vue):** Vue 3 + Vite + TypeScript + Pinia + Vue Router
- **微信小程序端 (miniapp):** uni-app (Vue 3 语法)

## 📂 项目结构
- `/backend`: 提供统一的 RESTful API 数据服务与权限校验。
- `/web-vue`: 
  - **顾客视角:** 宠物店官网、PC端商品浏览。
  - **店员/店长视角:** 数据大屏、库存管理、订单处理、员工管理。
- `/miniapp`: 
  - **顾客视角:** 手机端服务预约、会员积分查看、在线商城。
  - **店员/店长视角:** 移动端扫码核销、订单即时提醒、快速状态修改。

## 🚀 本地开发与运行指南

### 1. 启动后端 (backend)
\`\`\`bash
cd backend
# 激活虚拟环境 (Windows)
.\venv\Scripts\activate
# 安装依赖
pip install -r requirements.txt
# 启动服务
uvicorn main:app --reload
\`\`\`

### 2. 启动 PC 网页端 (web-vue)
\`\`\`bash
cd web-vue
npm install
npm run dev
\`\`\`

### 3. 启动 小程序端 (miniapp)
- 使用 `HBuilderX` 导入 `/miniapp` 目录。
- 点击顶部菜单栏：`运行 -> 运行到小程序模拟器 -> 微信开发者工具`。

## 🤝 协作规范
1. 请勿直接在 `main` 分支开发，所有新功能请从 `dev` 分支拉取新的 `feature/xxx` 分支。
2. 提交代码前请确保已拉取最新代码，解决冲突后再发起 Pull Request。
