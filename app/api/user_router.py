"""用户相关API接口"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models.user import User_Pydantic, UserCreate_Pydantic, UserUpdate_Pydantic
from app.dao import UserDAO
from app.configs import create_response, paginate_response

# 创建用户相关的路由器
user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.post("/", response_model=dict)
async def create_user(user_data: UserCreate_Pydantic) -> dict:
    """创建新用户"""
    # 检查手机号是否已存在
    existing_user = await UserDAO.get_by_phone(user_data.phone)
    if existing_user:
        raise HTTPException(status_code=400, detail="手机号已被注册")
    
    # 创建用户
    user_dict = user_data.dict()
    user = await UserDAO.create(user_dict)
    
    # 转换为Pydantic模型输出
    user_pydantic = await User_Pydantic.from_tortoise_orm(user)
    
    return create_response(
        success=True,
        message="用户创建成功",
        data=user_pydantic.dict()
    )


@user_router.get("/{user_id}", response_model=dict)
async def get_user(user_id: int) -> dict:
    """获取用户详情"""
    user = await UserDAO.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    user_pydantic = await User_Pydantic.from_tortoise_orm(user)
    
    return create_response(
        success=True,
        message="获取用户成功",
        data=user_pydantic.dict()
    )


@user_router.put("/{user_id}", response_model=dict)
async def update_user(user_id: int, user_update: UserUpdate_Pydantic) -> dict:
    """更新用户信息"""
    # 构建更新数据（过滤掉None值）
    update_data = {k: v for k, v in user_update.dict().items() if v is not None}
    
    # 检查手机号是否已被其他用户使用
    if "phone" in update_data:
        existing_user = await UserDAO.get_by_phone(update_data["phone"])
        if existing_user and existing_user.id != user_id:
            raise HTTPException(status_code=400, detail="手机号已被其他用户使用")
    
    # 更新用户
    updated_user = await UserDAO.update(user_id, update_data)
    if not updated_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    user_pydantic = await User_Pydantic.from_tortoise_orm(updated_user)
    
    return create_response(
        success=True,
        message="用户更新成功",
        data=user_pydantic.dict()
    )


@user_router.delete("/{user_id}", response_model=dict)
async def delete_user(user_id: int) -> dict:
    """删除用户（软删除）"""
    success = await UserDAO.delete(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return create_response(
        success=True,
        message="用户删除成功",
        data=None
    )


@user_router.get("/", response_model=dict)
async def list_users(page: int = 1, page_size: int = 10) -> dict:
    """获取用户列表（分页）"""
    # 参数验证
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 10
    
    # 获取用户列表
    users, total = await UserDAO.list_users(page, page_size)
    
    # 转换为Pydantic模型
    users_pydantic = []
    for user in users:
        user_pydantic = await User_Pydantic.from_tortoise_orm(user)
        users_pydantic.append(user_pydantic.dict())
    
    # 构建分页响应
    pagination_data = paginate_response(
        page=page,
        page_size=page_size,
        total=total
    )
    
    return create_response(
        success=True,
        message="获取用户列表成功",
        data={
            "items": users_pydantic,
            "pagination": pagination_data
        }
    )