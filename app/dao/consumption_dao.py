"""消费行为数据访问对象"""
from typing import List, Optional
from datetime import datetime, date
from tortoise.expressions import Q
from app.models.consumption import Consumption


class ConsumptionDAO:
    """消费行为相关的数据库操作"""
    
    @staticmethod
    async def get_by_id(consumption_id: int) -> Optional[Consumption]:
        """根据ID获取消费记录"""
        return await Consumption.get_or_none(id=consumption_id, is_deleted=False)
    
    @staticmethod
    async def create(consumption_data: dict) -> Consumption:
        """创建消费记录"""
        return await Consumption.create(**consumption_data)
    
    @staticmethod
    async def update(consumption_id: int, update_data: dict) -> Optional[Consumption]:
        """更新消费记录"""
        consumption = await Consumption.get_or_none(id=consumption_id, is_deleted=False)
        if consumption:
            await consumption.update_from_dict(update_data)
            await consumption.save()
        return consumption
    
    @staticmethod
    async def delete(consumption_id: int) -> bool:
        """软删除消费记录"""
        consumption = await Consumption.get_or_none(id=consumption_id, is_deleted=False)
        if consumption:
            await consumption.soft_delete()
            return True
        return False
    
    @staticmethod
    async def get_by_user(user_id: int, page: int = 1, page_size: int = 20) -> tuple[List[Consumption], int]:
        """获取用户的消费记录列表"""
        offset = (page - 1) * page_size
        
        # 查询总数
        total = await Consumption.filter(user_id=user_id, is_deleted=False).count()
        
        # 查询分页数据，按交易时间倒序
        consumptions = await Consumption.filter(user_id=user_id, is_deleted=False)\
            .order_by("-transaction_time")\
            .offset(offset)\
            .limit(page_size)\
            .all()
        
        return consumptions, total
    
    @staticmethod
    async def get_by_date_range(
        user_id: int,
        start_date: date,
        end_date: date,
        transaction_type: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[Consumption]:
        """按日期范围查询消费记录"""
        # 构建查询条件
        conditions = Q(user_id=user_id) & Q(is_deleted=False)
        
        # 添加日期范围条件
        conditions &= Q(transaction_time__gte=datetime.combine(start_date, datetime.min.time()))
        conditions &= Q(transaction_time__lte=datetime.combine(end_date, datetime.max.time()))
        
        # 添加交易类型条件（如果提供）
        if transaction_type:
            conditions &= Q(transaction_type=transaction_type)
        
        # 添加分类条件（如果提供）
        if category:
            conditions &= Q(category=category)
        
        # 执行查询
        return await Consumption.filter(conditions).order_by("-transaction_time").all()
    
    @staticmethod
    async def get_statistics_by_category(
        user_id: int,
        start_date: date,
        end_date: date,
        transaction_type: str = "支出"
    ) -> dict:
        """获取按分类统计的消费数据"""
        # 查询指定条件的所有记录
        records = await ConsumptionDAO.get_by_date_range(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            transaction_type=transaction_type
        )
        
        # 按分类统计
        stats = {}
        total = 0
        
        for record in records:
            category_name = record.category or "未分类"
            if category_name not in stats:
                stats[category_name] = {
                    "amount": 0,
                    "count": 0
                }
            
            stats[category_name]["amount"] += float(record.amount)
            stats[category_name]["count"] += 1
            total += float(record.amount)
        
        # 计算百分比
        for category_name in stats:
            stats[category_name]["percentage"] = (
                (stats[category_name]["amount"] / total * 100) if total > 0 else 0
            )
        
        return {
            "by_category": stats,
            "total_amount": total,
            "total_count": len(records)
        }