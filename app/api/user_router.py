"""用户相关API接口"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.schemas.user_schemas import User, UserCreate, UserUpdate
from tortoise.contrib.pydantic import pydantic_model_creator
from app.models.user import User as UserModel
from app.dao import UserDAO
from app.settings.response import success_response, error_response, paginate_response

# 创建用户相关的路由器
user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.post("/", response_model=dict)
async def create_user(user_data: UserCreate) -> dict:
    """创建新用户"""
    # 检查手机号是否已存在
    existing_user = await UserDAO.get_by_phone(user_data.phone)
    if existing_user:
        return error_response(
            code=4001,
            message="手机号已被注册",
            status_code=400
        )
    
    # 创建用户
    user_dict = user_data.dict()
    user = await UserDAO.create(user_dict)
    
    # 手动构建响应数据，避免直接序列化datetime
    data = {
        "id": user.id,
        "name": user.name,
        "gender": user.gender,
        "phone": user.phone,
        "created_at": user.created_at.isoformat(),
        "updated_at": user.updated_at.isoformat(),
        "is_deleted": user.is_deleted
    }
    
    return success_response(
        message="用户创建成功",
        data=data
    )


@user_router.get("/{user_id}", response_model=dict)
async def get_user(user_id: int) -> dict:
    """获取用户详情"""
    user = await UserDAO.get_by_id(user_id)
    if not user:
        return error_response(
            code=4004,
            message="用户不存在",
            status_code=404
        )
    
    # 手动构建响应数据，避免直接序列化datetime
    data = {
        "id": user.id,
        "name": user.name,
        "gender": user.gender,
        "phone": user.phone,
        "created_at": user.created_at.isoformat(),
        "updated_at": user.updated_at.isoformat(),
        "is_deleted": user.is_deleted
    }
    
    return success_response(
        message="获取用户成功",
        data=data
    )


@user_router.put("/{user_id}", response_model=dict)
async def update_user(user_id: int, user_update: UserUpdate) -> dict:
    """更新用户信息"""
    # 构建更新数据（过滤掉None值）
    update_data = {k: v for k, v in user_update.dict().items() if v is not None}
    
    # 检查手机号是否已被其他用户使用
    if "phone" in update_data:
        existing_user = await UserDAO.get_by_phone(update_data["phone"])
        if existing_user and existing_user.id != user_id:
            return error_response(
            code=4002,
            message="手机号已被其他用户使用",
            status_code=400
        )
    
    # 更新用户
    updated_user = await UserDAO.update(user_id, update_data)
    if not updated_user:
        return error_response(
            code=4004,
            message="用户不存在",
            status_code=404
        )
    
    # 手动构建响应数据，避免直接序列化datetime
    data = {
        "id": updated_user.id,
        "name": updated_user.name,
        "gender": updated_user.gender,
        "phone": updated_user.phone,
        "created_at": updated_user.created_at.isoformat(),
        "updated_at": updated_user.updated_at.isoformat(),
        "is_deleted": updated_user.is_deleted
    }
    
    return success_response(
        message="用户更新成功",
        data=data
    )


@user_router.delete("/{user_id}", response_model=dict)
async def delete_user(user_id: int) -> dict:
    """删除用户（软删除）"""
    success = await UserDAO.delete(user_id)
    if not success:
        return error_response(
            code=4004,
            message="用户不存在",
            status_code=404
        )
    
    return success_response(
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
    
    # 手动构建响应数据列表，避免直接序列化datetime
    users_pydantic = []
    for user in users:
        user_data = {
            "id": user.id,
            "name": user.name,
            "gender": user.gender,
            "phone": user.phone,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat(),
            "is_deleted": user.is_deleted
        }
        users_pydantic.append(user_data)
    
    # 构建分页元数据
    pagination_info = paginate_response(
        page=page,
        page_size=page_size,
        total=total
    )
    
    return success_response(
        message="获取用户列表成功",
        data=users_pydantic,
        pagination=pagination_info
    )