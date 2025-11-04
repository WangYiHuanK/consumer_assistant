"""消费行为相关API接口"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import date
from app.schemas.consumption_schemas import Consumption, ConsumptionCreate, ConsumptionUpdate
from app.models.consumption import Consumption as ConsumptionModel
from app.dao import ConsumptionDAO, UserDAO
from app.configs.response import success_response, error_response, paginate_response

# 创建消费行为相关的路由器
consumption_router = APIRouter(prefix="/consumptions", tags=["consumptions"])


@consumption_router.post("/", response_model=dict)
async def create_consumption(consumption_data: ConsumptionCreate) -> dict:
    """创建消费记录"""
    # 验证用户是否存在
    user = await UserDAO.get_by_id(consumption_data.user_id)
    if not user:
        return error_response(
            code=4004,
            message="用户不存在",
            status_code=404
        )
    
    # 创建消费记录
    consumption_dict = consumption_data.dict()
    consumption = await ConsumptionDAO.create(consumption_dict)
    
    # 手动构建响应数据，避免直接序列化datetime
    data = {
        "id": consumption.id,
        "user_id": consumption.user_id,
        "transaction_time": consumption.transaction_time.isoformat(),
        "transaction_type": consumption.transaction_type,
        "amount": float(consumption.amount),
        "merchant_name": consumption.merchant_name,
        "category": consumption.category,
        "created_at": consumption.created_at.isoformat(),
        "updated_at": consumption.updated_at.isoformat(),
        "is_deleted": consumption.is_deleted
    }
    
    return success_response(
        message="消费记录创建成功",
        data=data
    )


@consumption_router.get("/{consumption_id}", response_model=dict)
async def get_consumption(consumption_id: int) -> dict:
    """获取消费记录详情"""
    consumption = await ConsumptionDAO.get_by_id(consumption_id)
    if not consumption:
        return error_response(
            code=4004,
            message="消费记录不存在",
            status_code=404
        )
    
    # 手动构建响应数据，避免直接序列化datetime
    data = {
        "id": consumption.id,
        "user_id": consumption.user_id,
        "transaction_time": consumption.transaction_time.isoformat(),
        "transaction_type": consumption.transaction_type,
        "amount": float(consumption.amount),
        "merchant_name": consumption.merchant_name,
        "category": consumption.category,
        "created_at": consumption.created_at.isoformat(),
        "updated_at": consumption.updated_at.isoformat(),
        "is_deleted": consumption.is_deleted
    }
    
    return success_response(
        message="获取消费记录成功",
        data=data
    )


@consumption_router.put("/{consumption_id}", response_model=dict)
async def update_consumption(
    consumption_id: int,
    consumption_update: ConsumptionUpdate
) -> dict:
    """更新消费记录"""
    # 构建更新数据（过滤掉None值）
    update_data = {k: v for k, v in consumption_update.dict().items() if v is not None}
    
    # 如果更新了用户ID，验证用户是否存在
    if "user_id" in update_data:
        user = await UserDAO.get_by_id(update_data["user_id"])
        if not user:
            return error_response(
            code=4004,
            message="用户不存在",
            status_code=404
        )
    
    # 更新消费记录
    updated_consumption = await ConsumptionDAO.update(consumption_id, update_data)
    if not updated_consumption:
        return error_response(
            code=4004,
            message="消费记录不存在",
            status_code=404
        )
    
    # 手动构建响应数据，避免直接序列化datetime
    data = {
        "id": updated_consumption.id,
        "user_id": updated_consumption.user_id,
        "transaction_time": updated_consumption.transaction_time.isoformat(),
        "transaction_type": updated_consumption.transaction_type,
        "amount": float(updated_consumption.amount),
        "merchant_name": updated_consumption.merchant_name,
        "category": updated_consumption.category,
        "created_at": updated_consumption.created_at.isoformat(),
        "updated_at": updated_consumption.updated_at.isoformat(),
        "is_deleted": updated_consumption.is_deleted
    }
    
    return success_response(
        message="消费记录更新成功",
        data=data
    )


@consumption_router.delete("/{consumption_id}", response_model=dict)
async def delete_consumption(consumption_id: int) -> dict:
    """删除消费记录（软删除）"""
    success = await ConsumptionDAO.delete(consumption_id)
    if not success:
        raise HTTPException(status_code=404, detail="消费记录不存在")
    
    return success_response(
        message="消费记录删除成功",
        data=None
    )


@consumption_router.get("/user/{user_id}", response_model=dict)
async def get_user_consumptions(
    user_id: int,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量")
) -> dict:
    """获取用户的消费记录列表"""
    # 验证用户是否存在
    user = await UserDAO.get_by_id(user_id)
    if not user:
        return error_response(
            code=4004,
            message="用户不存在",
            status_code=404
        )
    
    # 获取消费记录列表
    consumptions, total = await ConsumptionDAO.get_by_user(user_id, page, page_size)
    
    # 手动构建响应数据列表，避免直接序列化datetime
    consumptions_pydantic = []
    for consumption in consumptions:
        consumption_data = {
            "id": consumption.id,
            "user_id": consumption.user_id,
            "transaction_time": consumption.transaction_time.isoformat(),
            "transaction_type": consumption.transaction_type,
            "amount": float(consumption.amount),
            "merchant_name": consumption.merchant_name,
            "category": consumption.category,
            "created_at": consumption.created_at.isoformat(),
            "updated_at": consumption.updated_at.isoformat(),
            "is_deleted": consumption.is_deleted
        }
        consumptions_pydantic.append(consumption_data)
    
    # 构建分页元数据
    pagination_info = paginate_response(
        page=page,
        page_size=page_size,
        total=total
    )
    
    return success_response(
        message="获取用户消费记录成功",
        data=consumptions_pydantic,
        pagination=pagination_info
    )


@consumption_router.get("/user/{user_id}/statistics", response_model=dict)
async def get_user_consumption_statistics(
    user_id: int,
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
    transaction_type: str = Query("支出", description="交易类型（收入/支出）")
) -> dict:
    """获取用户的消费统计数据"""
    # 验证用户是否存在
    user = await UserDAO.get_by_id(user_id)
    if not user:
        return error_response(
            code=4004,
            message="用户不存在",
            status_code=404
        )
    
    # 验证日期范围
    if start_date > end_date:
        return error_response(
            code=4003,
            message="开始日期不能晚于结束日期",
            status_code=400
        )
    
    # 获取统计数据
    statistics = await ConsumptionDAO.get_statistics_by_category(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        transaction_type=transaction_type
    )
    
    return success_response(
        message="获取消费统计数据成功",
        data=statistics
    )