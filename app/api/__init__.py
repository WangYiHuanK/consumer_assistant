"""API路由模块"""
from fastapi import APIRouter
from .user_router import user_router
from .consumption_router import consumption_router

# 创建主API路由器
api_router = APIRouter()

# 注册各模块路由
api_router.include_router(user_router)
api_router.include_router(consumption_router)

__all__ = ["api_router"]