"""数据库配置和连接管理"""
from contextlib import asynccontextmanager
from tortoise import Tortoise

# 导入配置
from app.configs.config import config

# 使用全局配置作为数据库设置
db_settings = config


def get_tortoise_config() -> dict:
    """获取Tortoise ORM配置"""
    return {
        "connections": {
            "default": db_settings.DATABASE_URL
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
        print(f"数据库 {db_settings.DATABASE_NAME} 连接成功")
        return True
    except Exception as e:
        print(f"数据库连接错误: {e}")
        print("请确保PostgreSQL服务正在运行，且数据库已创建")
        return False