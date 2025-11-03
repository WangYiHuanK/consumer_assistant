"""消费行为相关API接口"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import date
from app.models.consumption import (
    Consumption_Pydantic,
    ConsumptionCreate_Pydantic,
    ConsumptionUpdate_Pydantic
)
from app.dao import ConsumptionDAO, UserDAO
from app.configs import create_response, paginate_response

# 创建消费行为相关的路由器
consumption_router = APIRouter(prefix="/consumptions", tags=["consumptions"])


@consumption_router.post("/", response_model=dict)
async def create_consumption(consumption_data: ConsumptionCreate_Pydantic) -> dict:
    """创建消费记录"""
    # 验证用户是否存在
    user = await UserDAO.get_by_id(consumption_data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 创建消费记录
    consumption_dict = consumption_data.dict()
    consumption = await ConsumptionDAO.create(consumption_dict)
    
    # 转换为Pydantic模型输出
    consumption_pydantic = await Consumption_Pydantic.from_tortoise_orm(consumption)
    
    return create_response(
        success=True,
        message="消费记录创建成功",
        data=consumption_pydantic.dict()
    )


@consumption_router.get("/{consumption_id}", response_model=dict)
async def get_consumption(consumption_id: int) -> dict:
    """获取消费记录详情"""
    consumption = await ConsumptionDAO.get_by_id(consumption_id)
    if not consumption:
        raise HTTPException(status_code=404, detail="消费记录不存在")
    
    consumption_pydantic = await Consumption_Pydantic.from_tortoise_orm(consumption)
    
    return create_response(
        success=True,
        message="获取消费记录成功",
        data=consumption_pydantic.dict()
    )


@consumption_router.put("/{consumption_id}", response_model=dict)
async def update_consumption(
    consumption_id: int,
    consumption_update: ConsumptionUpdate_Pydantic
) -> dict:
    """更新消费记录"""
    # 构建更新数据（过滤掉None值）
    update_data = {k: v for k, v in consumption_update.dict().items() if v is not None}
    
    # 如果更新了用户ID，验证用户是否存在
    if "user_id" in update_data:
        user = await UserDAO.get_by_id(update_data["user_id"])
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
    
    # 更新消费记录
    updated_consumption = await ConsumptionDAO.update(consumption_id, update_data)
    if not updated_consumption:
        raise HTTPException(status_code=404, detail="消费记录不存在")
    
    consumption_pydantic = await Consumption_Pydantic.from_tortoise_orm(updated_consumption)
    
    return create_response(
        success=True,
        message="消费记录更新成功",
        data=consumption_pydantic.dict()
    )


@consumption_router.delete("/{consumption_id}", response_model=dict)
async def delete_consumption(consumption_id: int) -> dict:
    """删除消费记录（软删除）"""
    success = await ConsumptionDAO.delete(consumption_id)
    if not success:
        raise HTTPException(status_code=404, detail="消费记录不存在")
    
    return create_response(
        success=True,
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
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 获取消费记录列表
    consumptions, total = await ConsumptionDAO.get_by_user(user_id, page, page_size)
    
    # 转换为Pydantic模型
    consumptions_pydantic = []
    for consumption in consumptions:
        consumption_pydantic = await Consumption_Pydantic.from_tortoise_orm(consumption)
        consumptions_pydantic.append(consumption_pydantic.dict())
    
    # 构建分页响应
    pagination_data = paginate_response(
        page=page,
        page_size=page_size,
        total=total
    )
    
    return create_response(
        success=True,
        message="获取用户消费记录成功",
        data={
            "items": consumptions_pydantic,
            "pagination": pagination_data
        }
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
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 验证日期范围
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="开始日期不能晚于结束日期")
    
    # 获取统计数据
    statistics = await ConsumptionDAO.get_statistics_by_category(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        transaction_type=transaction_type
    )
    
    return create_response(
        success=True,
        message="获取消费统计数据成功",
        data=statistics
    )