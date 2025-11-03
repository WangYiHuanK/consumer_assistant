"""基础模型类定义"""
from tortoise import models, fields
from datetime import datetime


class BaseModel(models.Model):
    """所有模型的基类，包含通用字段"""
    id = fields.IntField(pk=True, index=True, description="主键ID")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")
    is_deleted = fields.BooleanField(default=False, index=True, description="是否删除")
    
    class Meta:
        abstract = True  # 抽象类，不会创建实际的表
    
    def soft_delete(self):
        """软删除方法"""
        self.is_deleted = True
        return self.save()
    
    def __str__(self):
        """字符串表示"""
        return f"{self.__class__.__name__}(id={self.id})"