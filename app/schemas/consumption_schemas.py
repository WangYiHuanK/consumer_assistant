"""消费记录数据验证和序列化模型"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from decimal import Decimal


class ConsumptionBase(BaseModel):
    """消费记录基础模型"""
    transaction_time: datetime = Field(..., description="交易时间")
    transaction_type: str = Field(..., pattern="^(收入|支出)$", description="交易类型")
    amount: Decimal = Field(..., ge=0, decimal_places=2, description="金额")
    merchant_name: str = Field(..., max_length=100, description="对方户名（商户/分类）")
    category: Optional[str] = Field(None, max_length=50, description="分类")


class ConsumptionCreate(ConsumptionBase):
    """消费记录创建模型"""
    user_id: int = Field(..., description="关联用户ID")
    
    @validator('amount')
    def validate_amount(cls, v):
        """验证金额是否有效"""
        if v <= 0:
            raise ValueError('金额必须大于0')
        return v


class ConsumptionUpdate(BaseModel):
    """消费记录更新模型"""
    transaction_time: Optional[datetime] = Field(None, description="交易时间")
    transaction_type: Optional[str] = Field(None, pattern="^(收入|支出)$", description="交易类型")
    amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2, description="金额")
    merchant_name: Optional[str] = Field(None, max_length=100, description="对方户名（商户/分类）")
    category: Optional[str] = Field(None, max_length=50, description="分类")
    user_id: Optional[int] = Field(None, description="关联用户ID")
    
    @validator('amount')
    def validate_amount(cls, v):
        """验证金额是否有效"""
        if v is not None and v <= 0:
            raise ValueError('金额必须大于0')
        return v


class Consumption(ConsumptionBase):
    """消费记录响应模型"""
    id: int = Field(..., description="消费记录ID")
    user_id: int = Field(..., description="关联用户ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    is_deleted: bool = Field(..., description="是否删除")
    
    class Config:
        from_attributes = True  # Pydantic V2 语法，替代旧版的 orm_mode = True