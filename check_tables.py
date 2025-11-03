"""简单脚本用于检查数据库表是否创建成功"""
import asyncio
import asyncpg
from app.database import db_settings

async def check_tables():
    try:
        # 连接到数据库
        conn = await asyncpg.connect(
            host=db_settings.database_host,
            port=db_settings.database_port,
            user=db_settings.database_user,
            password=db_settings.database_password,
            database=db_settings.database_name
        )
        
        print(f"已成功连接到数据库: {db_settings.database_name}")
        
        # 查询所有表
        tables = await conn.fetch(
            "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
        )
        
        if tables:
            print("\n数据库中的表:")
            print("-" * 30)
            for table in tables:
                print(f"- {table['tablename']}")
                
                # 查询每个表的字段
                columns = await conn.fetch(
                    f"SELECT column_name, data_type FROM information_schema.columns "
                    f"WHERE table_name = '{table['tablename']}'"
                )
                print(f"  字段:")
                for col in columns:
                    print(f"    - {col['column_name']} ({col['data_type']})")
                print()
        else:
            print("数据库中没有表")
        
        await conn.close()
        return True
    except Exception as e:
        print(f"检查数据库表失败: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(check_tables())