"""用户模型定义"""
from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
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


# Pydantic模型用于数据验证和序列化
User_Pydantic = pydantic_model_creator(User, name="User")
UserCreate_Pydantic = pydantic_model_creator(User, name="UserCreate", exclude_readonly=True)
UserUpdate_Pydantic = pydantic_model_creator(User, name="UserUpdate", exclude_readonly=True, exclude=["id", "created_at"])