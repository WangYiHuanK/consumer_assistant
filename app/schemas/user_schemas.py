"""用户数据验证和序列化模型"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """用户基础模型"""
    name: str = Field(..., max_length=50, description="姓名")
    gender: str = Field(default="未知", pattern="^(男|女|未知)$", description="性别")
    phone: str = Field(..., max_length=20, description="手机号")


class UserCreate(UserBase):
    """用户创建模型"""
    pass


class UserUpdate(BaseModel):
    """用户更新模型"""
    name: Optional[str] = Field(None, max_length=50, description="姓名")
    gender: Optional[str] = Field(None, pattern="^(男|女|未知)$", description="性别")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")


class User(UserBase):
    """用户响应模型"""
    id: int = Field(..., description="用户ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    is_deleted: bool = Field(..., description="是否删除")
    
    class Config:
        from_attributes = True  # Pydantic V2 语法，替代旧版的 orm_mode = True