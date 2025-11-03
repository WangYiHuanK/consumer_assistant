"""FastAPI应用初始化 - MVC架构"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入数据库配置和操作
from app.database import init_db, close_db, check_database_connection

# 导入API路由
from app.api import api_router


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


# 初始化FastAPI应用
app = FastAPI(
    title="Consumer Assistant API",
    description="智能消费分析助手应用 - FastAPI + Tortoise ORM架构",
    version="1.0.0",
    lifespan=lifespan  # 添加生命周期管理
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("ALLOW_ORIGINS", "*")],  # 从环境变量读取
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(api_router)

# 根路径
@app.get("/")
async def root():
    return {"message": "Consumer Assistant API", "status": "running"}

# 健康检查端点
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Consumer Assistant API"}

# 导入控制器以注册路由
from app.controllers import *

# 导入数据库配置
from app.database import check_database_connection

# 导入模型模块（目前为空）
import app.models