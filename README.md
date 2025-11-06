# Consumer Assistant API

智能消费分析助手 - 一个基于FastAPI框架构建的现代化Web应用，提供消费数据分析、个性化报告生成和动态图表展示功能。

## 项目功能

- **消费数据管理**：支持消费记录的增删改查操作
- **智能消费分析**：基于MCP工具进行多维度消费数据分析
- **个性化报告生成**：根据用户需求自动生成详细的消费分析报告
- **动态图表生成**：支持根据分析需求智能生成多种类型的可视化图表
- **用户管理**：提供用户注册、登录和信息管理功能

## 项目结构

```
consumer_assistant/
├── app/
│   ├── __init__.py              # FastAPI应用初始化
│   ├── agents/                  # 智能代理模块
│   │   ├── advanced_consumption_agent.py  # 高级消费分析代理
│   │   └── consumption_mcp_tool.py        # 消费分析MCP工具
│   ├── api/                     # API路由模块
│   │   ├── consumption_analysis_router.py # 消费分析路由
│   │   ├── consumption_router.py          # 消费管理路由
│   │   └── user_router.py                 # 用户管理路由
│   ├── controllers/             # 控制器（业务逻辑）
│   ├── dao/                     # 数据访问对象
│   │   ├── consumption_dao.py   # 消费数据访问
│   │   └── user_dao.py          # 用户数据访问
│   ├── models/                  # 数据模型
│   │   ├── consumption.py       # 消费模型
│   │   └── user.py              # 用户模型
│   ├── schemas/                 # 数据验证模式
│   ├── settings/                # 应用配置
│   ├── static/                  # 静态资源
│   ├── templates/               # HTML模板
│   └── utils/                   # 工具函数
│       ├── chart_generator.py   # 图表生成器
│       └── dynamic_chart_generator.py  # 动态图表生成器
├── main.py                      # 应用入口点
├── requirements.txt             # 项目依赖
├── .gitignore                   # Git忽略文件
├── test_dynamic_chart.py        # 动态图表测试脚本
└── README.md                    # 项目说明
```

## 技术栈

- **FastAPI**: 现代、快速的Web框架
- **Pydantic**: 数据验证和设置管理
- **SQLAlchemy**: ORM数据库交互
- **Matplotlib/Seaborn**: 数据可视化
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

### 3. 数据库初始化

确保数据库已正确配置，然后运行初始化脚本：

```bash
python -m app.utils.init_database
```

### 4. 运行应用

```bash
python main.py
```

或者直接使用uvicorn：

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### 5. 访问API文档

启动后，可以访问以下地址：
- API文档：http://localhost:8000/docs
- 备用文档：http://localhost:8000/redoc
- 健康检查：http://localhost:8000/health

## API端点

### 用户管理
- `POST /api/users`: 创建新用户
- `GET /api/users/{user_id}`: 获取用户信息
- `PUT /api/users/{user_id}`: 更新用户信息

### 消费管理
- `POST /api/consumptions`: 创建消费记录
- `GET /api/consumptions`: 获取消费记录列表
- `GET /api/consumptions/{consumption_id}`: 获取单个消费记录
- `PUT /api/consumptions/{consumption_id}`: 更新消费记录
- `DELETE /api/consumptions/{consumption_id}`: 删除消费记录

### 消费分析
- `POST /api/analysis/custom`: 自定义消费分析
- `POST /api/analysis/report`: 生成消费分析报告

## 使用示例

### 1. 生成消费分析报告

```bash
curl -X POST "http://localhost:8000/api/analysis/report" \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": 1,
       "start_date": "2024-01-01",
       "end_date": "2024-01-31",
       "analysis_needs": ["餐饮消费分布", "最近一周消费趋势", "不同类别消费金额比较"]
     }'
```

### 2. 创建消费记录

```bash
curl -X POST "http://localhost:8000/api/consumptions" \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": 1,
       "amount": 128.50,
       "category": "餐饮",
       "description": "午餐",
       "transaction_time": "2024-01-15T12:30:00"
     }'
```

## 环境变量配置

应用使用以下环境变量（在.env文件中配置）：

```
# 数据库配置
DATABASE_URL="sqlite:///./consumer_assistant.db"

# 应用配置
APP_NAME="Consumer Assistant"
DEBUG=True
HOST="0.0.0.0"
PORT=8000

# 安全配置
SECRET_KEY="your-secret-key-here"
```

## 测试

### 运行动态图表生成测试

```bash
python test_dynamic_chart.py
```

## 开发指南

### 添加新的API路由

1. 在`app/api/`目录下创建新的路由文件
2. 在`app/__init__.py`中注册新路由

### 添加新的数据分析功能

1. 在`app/agents/`目录下扩展现有代理或创建新代理
2. 更新`consumption_mcp_tool.py`添加新的分析能力

### 添加新的图表类型

1. 扩展`dynamic_chart_generator.py`中的图表生成功能
2. 在`chart_generator.py`中添加新的图表模板

## 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启 Pull Request
