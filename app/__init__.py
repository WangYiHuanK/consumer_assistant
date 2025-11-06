"""FastAPI应用初始化 - MVC架构"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# 导入配置
from app.settings.config import config

# 导入数据库配置和操作
from app.database import init_db, close_db, check_database_connection

# 导入API路由和响应函数
from app.api import api_router
from app.settings.response import success_response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    print("正在检查数据库连接...")
    db_available = await check_database_connection()
    if not db_available:
        print("警告: 数据库连接失败")
    
    print("正在初始化数据库连接...")
    await init_db()
    print("数据库连接初始化完成")
    yield
    # 关闭时
    print("正在关闭数据库连接...")
    await close_db()
    print("数据库连接已关闭")


# 初始化FastAPI应用，启用API文档接口
fastapi_app = FastAPI(
    title=config.APP_NAME + " API",
    description="智能消费分析助手应用 - FastAPI + Tortoise ORM架构",
    version="1.0.0",
    lifespan=lifespan,  # 添加生命周期管理
    docs_url="/docs",  # Swagger UI文档地址
    redoc_url="/redoc",  # ReDoc文档地址
    debug=config.DEBUG
)

# 配置CORS
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=[config.ALLOW_ORIGINS],  # 从配置中读取
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
fastapi_app.include_router(api_router)

# 根路径
@fastapi_app.get("/")
async def root():
    return success_response(
        message="Consumer Assistant API 运行中",
        data={"status": "running"}
    )

# 健康检查端点
@fastapi_app.get("/health")
async def health_check():
    return success_response(
        message="服务健康状态正常",
        data={"status": "healthy", "service": "Consumer Assistant API"}
    )

# 控制器将通过单独的路由模块注册，避免循环导入

# 导入数据库配置
from app.database import check_database_connection

# 导入模型模块（目前为空）
import app.models

# 导出FastAPI应用实例
app = fastapi_app