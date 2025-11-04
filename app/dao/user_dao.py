"""用户数据访问对象"""
from typing import List, Optional
from app.models.user import User


class UserDAO:
    """用户相关的数据库操作"""
    
    @staticmethod
    async def get_by_id(user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        return await User.get_or_none(id=user_id, is_deleted=False)
    
    @staticmethod
    async def get_by_phone(phone: str) -> Optional[User]:
        """根据手机号获取用户"""
        return await User.get_or_none(phone=phone, is_deleted=False)
    
    @staticmethod
    async def create(user_data: dict) -> User:
        """创建用户"""
        return await User.create(**user_data)
    
    @staticmethod
    async def update(user_id: int, update_data: dict) -> Optional[User]:
        """更新用户信息"""
        user = await User.get_or_none(id=user_id, is_deleted=False)
        if user:
            await user.update_from_dict(update_data)
            await user.save()
        return user
    
    @staticmethod
    async def delete(user_id: int) -> bool:
        """软删除用户"""
        user = await User.get_or_none(id=user_id, is_deleted=False)
        if user:
            await user.soft_delete()
            return True
        return False
    
    @staticmethod
    async def list_users(page: int = 1, page_size: int = 10) -> tuple[List[User], int]:
        """获取用户列表（分页）"""
        # 计算偏移量
        offset = (page - 1) * page_size
        
        # 查询总数
        total = await User.filter(is_deleted=False).count()
        
        # 查询分页数据
        users = await User.filter(is_deleted=False).offset(offset).limit(page_size).all()
        
        return users, total