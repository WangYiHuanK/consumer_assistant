"""数据库配置和连接管理"""
import os
from contextlib import asynccontextmanager
from tortoise import Tortoise
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """数据库配置设置"""
    database_url: str = os.getenv("DATABASE_URL", "postgres://postgres:qwer1234@localhost:5432/consumer_assistant_db")
    database_type: str = os.getenv("DATABASE_TYPE", "postgres")
    database_host: str = os.getenv("DATABASE_HOST", "localhost")
    database_port: int = int(os.getenv("DATABASE_PORT", "5432"))
    database_user: str = os.getenv("DATABASE_USER", "postgres")
    database_password: str = os.getenv("DATABASE_PASSWORD", "qwer1234")
    database_name: str = os.getenv("DATABASE_NAME", "consumer_assistant_db")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"  # 允许额外的环境变量


# 全局数据库设置实例
db_settings = DatabaseSettings()


def get_tortoise_config() -> dict:
    """获取Tortoise ORM配置"""
    return {
        "connections": {
            "default": db_settings.database_url
        },
        "apps": {
            "models": {
                "models": [
                    "app.models",
                    "app.models.base",
                    "app.models.user",
                    "app.models.consumption"
                ],
                "default_connection": "default"
            }
        },
        "generate_schemas": True,  # 自动生成数据库表结构（开发环境）
        "add_exception_handlers": True
    }


# 数据库配置常量，供脚本使用
DB_CONFIG = get_tortoise_config()


async def init_db():
    """初始化数据库连接"""
    await Tortoise.init(config=get_tortoise_config())
    print("数据库连接已初始化")


async def close_db():
    """关闭数据库连接"""
    await Tortoise.close_connections()
    print("数据库连接已关闭")


@asynccontextmanager
async def get_db():
    """数据库连接上下文管理器"""
    try:
        yield Tortoise
    finally:
        await close_db()


async def check_database_connection():
    """检查数据库连接"""
    try:
        # 尝试连接数据库
        await init_db()
        print(f"数据库 {db_settings.database_name} 连接成功")
        return True
    except Exception as e:
        print(f"数据库连接错误: {e}")
        print("请确保PostgreSQL服务正在运行，且数据库已创建")
        return False