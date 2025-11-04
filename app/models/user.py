"""用户模型定义"""
from tortoise import fields
from .base import BaseModel


class User(BaseModel):
    """用户表模型"""
    name = fields.CharField(max_length=50, description="姓名")
    gender = fields.CharField(max_length=10, choices=["男", "女", "未知"], default="未知", description="性别")
    phone = fields.CharField(max_length=20, unique=True, index=True, description="手机号")
    
    class Meta:
        table = "users"
        description = "用户信息表"
    
    def __str__(self):
        """字符串表示"""
        return f"User(id={self.id}, name={self.name}, phone={self.phone})"

# 已迁移到 schemas 模块中定义
# 请使用 from app.schemas.user_schemas import User, UserCreate, UserUpdate