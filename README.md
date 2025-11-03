# Consumer Assistant API

智能消费分析助手 - 使用FastAPI框架和MVC架构构建的现代化Web应用。

## 项目结构

```
consumer_assistant/
├── app/
│   ├── __init__.py          # FastAPI应用初始化
│   ├── controllers/         # 控制器（路由和业务逻辑）
│   ├── models/              # 数据模型
│   ├── views/               # 视图层（响应格式化）
│   ├── static/              # 静态资源
│   └── templates/           # HTML模板
├── main.py                  # 应用入口点
├── requirements.txt         # 项目依赖
├── .env                     # 环境变量
└── README.md                # 项目说明
```

## 技术栈

- **FastAPI**: 现代、快速的Web框架
- **Pydantic**: 数据验证和设置管理
- **Uvicorn**: ASGI服务器
- **Python-dotenv**: 环境变量管理

## 安装和运行

### 1. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # 在Windows上使用 venv\Scripts\activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 运行应用

```bash
python main.py
```

或者直接使用uvicorn：

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### 4. 访问API文档

启动后，可以访问以下地址：
- API文档：http://localhost:8000/docs
- 备用文档：http://localhost:8000/redoc
- 健康检查：http://localhost:8000/health

## API端点

- `GET /`: 欢迎信息
- `GET /health`: 健康检查

## 环境变量

应用使用以下环境变量（在.env文件中配置）：

- `APP_NAME`: 应用名称
- `DEBUG`: 调试模式
- `HOST`: 服务器主机
- `PORT`: 服务器端口

## 开发指南

### 添加新路由

在`app/controllers/`目录下创建新的控制器文件，然后在`__init__.py`中注册路由。

### 添加新模型

在`app/models/`目录下创建新的数据模型文件，然后在`__init__.py`中导入并添加到`__all__`列表中。
