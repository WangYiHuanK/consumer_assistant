"""消费行为模型定义"""
from tortoise import fields

from datetime import datetime, date
from .base import BaseModel


class Consumption(BaseModel):
    """消费行为表模型"""
    user = fields.ForeignKeyField("models.User", related_name="consumptions", description="关联用户")
    transaction_time = fields.DatetimeField(index=True, description="交易时间")
    transaction_type = fields.CharField(
        max_length=10, 
        choices=["收入", "支出"], 
        default="支出", 
        index=True,
        description="交易类型"
    )
    amount = fields.DecimalField(max_digits=10, decimal_places=2, index=True, description="金额")
    merchant_name = fields.CharField(max_length=100, description="对方户名（商户/分类）")
    category = fields.CharField(max_length=50, null=True, index=True, description="分类")
    
    class Meta:
        table = "consumptions"
        description = "消费行为记录表"
    
    def __str__(self):
        """字符串表示"""
        return f"Consumption(id={self.id}, user_id={self.user_id}, type={self.transaction_type}, amount={self.amount})"


# 已迁移到 schemas 模块中定义
# 请使用 from app.schemas.consumption_schemas import Consumption, ConsumptionCreate, ConsumptionUpdate