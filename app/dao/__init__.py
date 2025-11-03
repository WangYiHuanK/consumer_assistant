"""数据访问对象(DAO)模块"""
# DAO负责处理所有ORM操作，作为控制器和数据库之间的中间层
from .user_dao import UserDAO
from .consumption_dao import ConsumptionDAO

__all__ = ["UserDAO", "ConsumptionDAO"]