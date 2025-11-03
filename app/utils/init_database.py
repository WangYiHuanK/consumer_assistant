"""数据库初始化脚本 - 根据模型创建数据库表结构"""
import asyncio
import sys
import os
from pathlib import Path
import asyncpg

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from tortoise import Tortoise, run_async
from app.database import DB_CONFIG, db_settings
from app.models import *  # 导入所有模型


async def create_database_if_not_exists():
    """
    如果数据库不存在，则创建数据库
    """
    try:
        print(f"检查数据库 '{db_settings.database_name}' 是否存在...")
        
        # 先尝试连接到postgres默认数据库
        conn = await asyncpg.connect(
            host=db_settings.database_host,
            port=db_settings.database_port,
            user=db_settings.database_user,
            password=db_settings.database_password,
            database='postgres'  # 使用默认的postgres数据库
        )
        
        # 检查数据库是否存在
        result = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1",
            db_settings.database_name
        )
        
        if not result:
            print(f"数据库 '{db_settings.database_name}' 不存在，正在创建...")
            await conn.execute(f"CREATE DATABASE {db_settings.database_name}")
            print(f"数据库 '{db_settings.database_name}' 创建成功！")
        else:
            print(f"数据库 '{db_settings.database_name}' 已存在")
        
        await conn.close()
        return True
    except Exception as e:
        print(f"创建数据库失败: {e}")
        return False

def init_db_schemas():
    """
    初始化数据库表结构
    这个函数将根据导入的模型创建或更新数据库表结构
    """
    async def _init_db():
        # 先检查并创建数据库
        await create_database_if_not_exists()
        
        print("正在连接数据库...")
        
        # 初始化Tortoise ORM
        await Tortoise.init(config=DB_CONFIG)
        
        # 创建或更新数据库表结构
        print("开始创建数据库表结构...")
        await Tortoise.generate_schemas()
        print("数据库表结构创建完成！")
        
        # 关闭连接
        await Tortoise.close_connections()
        print("数据库连接已关闭")
    
    try:
        # 运行异步初始化函数
        run_async(_init_db())
        print("数据库初始化成功！")
        return True
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def drop_and_recreate_db():
    """
    删除并重新创建数据库表结构（谨慎使用！）
    此操作会删除所有表并重新创建，会丢失所有数据
    """
    async def _drop_and_recreate():
        print("⚠️  警告：即将删除并重新创建数据库表结构！")
        print("此操作将丢失所有现有数据！")
        
        # 初始化Tortoise ORM
        await Tortoise.init(config=DB_CONFIG)
        
        # 删除所有表
        print("正在删除所有数据库表...")
        await Tortoise._drop_databases()
        print("所有表已删除")
        
        # 重新创建表结构
        print("正在重新创建数据库表结构...")
        await Tortoise.generate_schemas()
        print("数据库表结构重新创建完成！")
        
        # 关闭连接
        await Tortoise.close_connections()
        print("数据库连接已关闭")
    
    try:
        # 运行异步删除并重新创建函数
        run_async(_drop_and_recreate())
        print("数据库重建成功！")
        return True
    except Exception as e:
        print(f"数据库重建失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def check_db_connection():
    """
    检查数据库连接是否正常
    """
    try:
        print("正在测试数据库连接...")
        
        # 先尝试直接连接数据库
        conn = await asyncpg.connect(
            host=db_settings.database_host,
            port=db_settings.database_port,
            user=db_settings.database_user,
            password=db_settings.database_password,
            database=db_settings.database_name
        )
        await conn.fetchval("SELECT 1")
        await conn.close()
        
        print("数据库连接正常！")
        
        # 再测试Tortoise ORM连接
        await Tortoise.init(config=DB_CONFIG)
        await Tortoise.get_connection().execute_query("SELECT 1")
        print("Tortoise ORM连接正常！")
        await Tortoise.close_connections()
        
        return True
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return False


def list_models():
    """
    列出所有注册的模型
    """
    async def _list_models():
        await Tortoise.init(config=DB_CONFIG)
        
        print("\n已注册的数据库模型:")
        print("-" * 50)
        
        for model_name, model in Tortoise.apps["models"].items():
            print(f"模型名称: {model_name}")
            print(f"表名: {model._meta.db_table}")
            print(f"字段: {', '.join([f.name for f in model._meta.fields])}")
            print("-" * 50)
        
        await Tortoise.close_connections()
    
    run_async(_list_models())


if __name__ == "__main__":
    """
    命令行入口
    
    使用方式：
    python app/utils/init_database.py [command]
    
    命令：
    - create 或不提供参数: 创建或更新数据库表结构
    - drop   : 删除并重新创建数据库表结构（谨慎使用）
    - check  : 检查数据库连接
    - models : 列出所有注册的模型
    """
    
    # 获取命令行参数
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
    else:
        command = "create"  # 默认命令
    
    # 执行对应的命令
    if command == "create":
        init_db_schemas()
    elif command == "drop":
        # 再次确认
        confirm = input("⚠️  确认删除并重新创建数据库表结构？这将丢失所有数据！(yes/no): ")
        if confirm.lower() == "yes":
            drop_and_recreate_db()
        else:
            print("操作已取消")
    elif command == "check":
        run_async(check_db_connection())
    elif command == "models":
        list_models()
    else:
        print("未知命令")
        print("\n使用方式：")
        print("python app/utils/init_database.py [command]")
        print("\n命令：")
        print("- create 或不提供参数: 创建或更新数据库表结构")
        print("- drop   : 删除并重新创建数据库表结构（谨慎使用）")
        print("- check  : 检查数据库连接")
        print("- models : 列出所有注册的模型")