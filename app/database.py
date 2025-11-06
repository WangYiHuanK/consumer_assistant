"""数据库配置和连接管理"""
from contextlib import asynccontextmanager
from tortoise import Tortoise, connections
from tortoise.exceptions import OperationalError
import asyncio

# 导入配置
from app.settings.config import config

# 使用全局配置作为数据库设置
db_settings = config


# 全局数据库连接状态
_db_initialized = False


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
    global _db_initialized
    
    # 检查是否已经初始化
    if _db_initialized:
        print("数据库连接已经初始化")
        return
    
    try:
        # 初始化Tortoise ORM
        await Tortoise.init(config=get_tortoise_config())
        
        # 生成数据库表结构
        await Tortoise.generate_schemas()
        
        # 验证连接
        await connections.get("default").execute_query("SELECT 1")
        
        _db_initialized = True
        print("数据库连接已成功初始化")
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        raise


async def close_db():
    """关闭数据库连接"""
    global _db_initialized
    try:
        await Tortoise.close_connections()
        _db_initialized = False
        print("数据库连接已关闭")
    except Exception as e:
        print(f"关闭数据库连接时出错: {e}")


@asynccontextmanager
async def get_db():
    """数据库连接上下文管理器"""
    # 确保数据库已初始化
    if not _db_initialized:
        await init_db()
    
    try:
        yield Tortoise
    except Exception as e:
        print(f"数据库操作错误: {e}")
        raise
    finally:
        # 不要在这里关闭连接，让应用生命周期管理处理
        pass


async def ensure_db_connection():
    """确保数据库连接已建立，如果没有则初始化"""
    global _db_initialized
    if not _db_initialized:
        await init_db()


async def check_database_connection():
    """检查数据库连接"""
    try:
        # 尝试连接数据库
        await init_db()
        print(f"数据库 {db_settings.DATABASE_NAME} 连接成功")
        return True
    except OperationalError as e:
        print(f"数据库操作错误: {e}")
        print("请确保PostgreSQL服务正在运行，且数据库已创建")
        return False
    except Exception as e:
        print(f"数据库连接错误: {e}")
        return False