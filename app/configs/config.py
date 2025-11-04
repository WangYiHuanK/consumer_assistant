"""配置管理模块"""
import os
from typing import Optional
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()


class Config:
    """配置类，从环境变量中读取配置"""
    
    # 应用配置
    APP_NAME: str = os.getenv("APP_NAME", "Consumer Assistant")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # 服务器配置
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # 数据库配置
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgres://postgres:qwer1234@localhost:5432/consumer_assistant_db")
    DATABASE_TYPE: str = os.getenv("DATABASE_TYPE", "postgres")
    DATABASE_HOST: str = os.getenv("DATABASE_HOST", "localhost")
    DATABASE_PORT: int = int(os.getenv("DATABASE_PORT", "5432"))
    DATABASE_USER: str = os.getenv("DATABASE_USER", "postgres")
    DATABASE_PASSWORD: str = os.getenv("DATABASE_PASSWORD", "qwer1234")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "consumer_assistant_db")
    
    # CORS配置
    ALLOW_ORIGINS: str = os.getenv("ALLOW_ORIGINS", "*")
    
    # 大模型配置
    LLM_MODEL: str = os.getenv("LLM_MODEL", "qwen2.5:7b")
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "http://localhost:11434")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.0"))


# 创建全局配置实例
config = Config()