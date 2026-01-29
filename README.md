# AI漫画编辑器

基于Flask后端和React前端的AI漫画编辑器，集成Midjourney API，支持角色一致性保证和多用户协作。

## 项目特性

- 🎨 **智能漫画编辑**: 基于AI的漫画创作工具
- 👥 **多用户协作**: 实时协作编辑功能
- 🎭 **角色一致性**: 角色模板管理和一致性保证
- 🤖 **Midjourney集成**: 集成Midjourney API进行图片生成
- 📱 **响应式设计**: 支持桌面和移动设备
- 🔐 **用户认证**: JWT认证和权限管理

## 技术栈

### 后端
- **Flask**: Web框架
- **SQLAlchemy**: ORM
- **Flask-JWT-Extended**: JWT认证
- **PostgreSQL**: 数据库
- **Redis**: 缓存
- **Docker**: 容器化

### 前端
- **React**: UI框架
- **Redux Toolkit**: 状态管理
- **Ant Design**: UI组件库
- **React Router**: 路由管理
- **Axios**: HTTP客户端

## 快速开始

### 环境要求

- Docker和Docker Compose
- Node.js 18+ (开发环境)
- Python 3.11+ (开发环境)

### 使用Docker Compose (推荐)

1. 克隆项目
```bash
git clone <repository-url>
cd ComicGenerator
```

2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，填入实际配置
```

3. 启动服务
```bash
docker-compose up -d
```

4. 访问应用
- 前端: http://localhost
- 后端API: http://localhost:5000
- API文档: http://localhost:5000/api/health

### 本地开发

#### 后端设置

```bash
cd backend
pip install -r requirements.txt
python manage.py create
python manage.py sample
python run.py
```

#### 前端设置

```bash
cd frontend
npm install
npm start
```

## API文档

### 认证接口

- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/auth/me` - 获取当前用户信息

### 项目管理

- `GET /api/projects` - 获取项目列表
- `POST /api/projects` - 创建项目
- `GET /api/projects/{id}` - 获取项目详情
- `PUT /api/projects/{id}` - 更新项目
- `DELETE /api/projects/{id}` - 删除项目

### 角色管理

- `GET /api/characters` - 获取角色模板
- `POST /api/characters` - 创建角色模板
- `PUT /api/characters/{id}` - 更新角色模板
- `DELETE /api/characters/{id}` - 删除角色模板

### 漫画编辑

- `GET /api/comics/project/{project_id}` - 获取项目漫画
- `POST /api/comics` - 创建漫画图片
- `PUT /api/comics/{id}` - 更新漫画图片
- `DELETE /api/comics/{id}` - 删除漫画图片

## 数据库结构

### 用户表 (users)
- id: 主键
- username: 用户名
- email: 邮箱
- password_hash: 密码哈希
- created_at: 创建时间

### 项目表 (projects)
- id: 主键
- name: 项目名称
- description: 项目描述
- owner_id: 所有者ID
- created_at: 创建时间
- updated_at: 更新时间

### 角色模板表 (character_templates)
- id: 主键
- name: 角色名称
- description: 角色描述
- features: 角色特征 (JSON)
- reference_images: 参考图片 (JSON)
- owner_id: 所有者ID
- created_at: 创建时间

### 漫画图片表 (comic_images)
- id: 主键
- project_id: 项目ID
- character_template_id: 角色模板ID
- prompt: 生成提示词
- image_url: 图片URL
- midjourney_task_id: Midjourney任务ID
- status: 状态 (pending, processing, completed, failed)
- position_x: X坐标
- position_y: Y坐标
- width: 宽度
- height: 高度
- layer_order: 图层顺序
- created_at: 创建时间

## 部署

### 生产环境部署

1. 配置生产环境变量
2. 使用生产数据库
3. 设置正确的密钥
4. 配置反向代理 (Nginx)
5. 设置HTTPS
6. 配置监控和日志

### Docker部署

```bash
# 构建生产镜像
docker-compose -f docker-compose.prod.yml build

# 启动生产服务
docker-compose -f docker-compose.prod.yml up -d
```

## 开发指南

### 代码规范

- 后端遵循PEP 8
- 前端使用ESLint和Prettier
- 提交前运行测试

### 测试

```bash
# 后端测试
cd backend
pytest

# 前端测试
cd frontend
npm test
```

### 数据库迁移

```bash
cd backend
flask db migrate -m "描述"
flask db upgrade
```

## 贡献

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证

MIT License

## 支持

如有问题，请创建Issue或联系开发团队。