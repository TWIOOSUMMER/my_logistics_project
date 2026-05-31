# 物流信息管理系统

基于 Django 构建的完整物流信息管理平台。

## 功能特性

- 📦 货物信息管理（增删改查）
- 📋 订单管理与跟踪
- 📊 运营数据可视化
- 🎨 主题切换（现代/复古/赛博朋克）
- 📈 数据统计与分析
- 📤 数据导入导出

## 技术栈

- **后端**：Django 5.0+
- **前端**：HTML5 + CSS3 + JavaScript
- **样式**：Bootstrap 5.3.0
- **图表**：Chart.js 4.4.0
- **数据库**：MySQL（推荐）或 SQLite

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/TWIOOSUMMER/my_logistics_project.git
cd my_logistics_project
```

### 2. 创建并激活虚拟环境

```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate # Linux/Mac
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置数据库

编辑 `logistics_project/settings.py` 或创建 `.env` 文件（参考 `.env.example`）。

### 5. 执行迁移

```bash
python manage.py migrate
```

### 6. 运行服务器

```bash
python manage.py runserver
```

访问 http://127.0.0.1:8000/

## 项目结构

```
my_logistics_project/
├── logistics/              # 主要应用
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── logistics_project/     # 项目配置
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── static/                # 静态文件
│   └── css/themes.css
├── templates/             # 模板文件
│   └── logistics/
├── manage.py
├── requirements.txt
├── .env.example
└── .gitignore
```

## 环境变量

参考 `.env.example` 配置：

```
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True
DB_ENGINE=django.db.backends.mysql
DB_NAME=django_db01
DB_USER=root
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=3306
```

## 作者
