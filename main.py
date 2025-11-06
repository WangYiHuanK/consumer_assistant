"""
消费分析系统主入口
仅支持FastAPI服务
"""
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def ensure_directories():
    """
    确保必要的目录存在
    """
    required_dirs = [
        os.path.join(os.path.dirname(__file__), 'workspace'),
        os.path.join(os.path.dirname(__file__), 'workspace', 'charts'),
        os.path.join(os.path.dirname(__file__), 'logs')
    ]
    
    for directory in required_dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"创建目录: {directory}")

def run_fastapi_server():
    """
    运行FastAPI服务器
    """
    try:
        import uvicorn
        from app import app
        from app.settings.config import config
        
        print("\n启动FastAPI服务...")
        print(f"服务地址: http://{config.HOST}:{config.PORT}")
        print(f"API文档: http://{config.HOST}:{config.PORT}/docs")
        print(f"重新加载: {config.DEBUG}")
        
        uvicorn.run(
            "app:app",
            host=config.HOST,
            port=config.PORT,
            reload=config.DEBUG
        )
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请安装依赖: pip install fastapi uvicorn")

def main():
    """
    主函数 - 仅启动FastAPI服务
    """
    # 确保目录存在
    ensure_directories()
    # 启动FastAPI服务
    run_fastapi_server()

if __name__ == '__main__':
    main()