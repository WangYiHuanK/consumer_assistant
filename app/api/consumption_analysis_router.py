"""消费行为分析和任务规划相关API接口"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional, Dict, Any
from datetime import date, datetime, timedelta
from app.dao import ConsumptionDAO, UserDAO
from app.configs.response import success_response, error_response
from app.agents.consumption_analyzer import analyze_and_plan, execute_agent_task

# 创建消费行为分析相关的路由器
consumption_analysis_router = APIRouter(prefix="/analysis", tags=["analysis"])


@consumption_analysis_router.get("/user/{user_id}/consumption-patterns", response_model=dict)
async def get_consumption_analysis(
    user_id: int,
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
    transaction_type: Optional[str] = Query("支出", description="交易类型（收入/支出）")
) -> dict:
    """
    获取用户的消费行为分析和任务规划
    
    Args:
        user_id: 用户ID
        start_date: 开始日期
        end_date: 结束日期
        transaction_type: 交易类型（收入/支出）
    
    Returns:
        包含消费分析和任务规划的响应
    """
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
    
    # 获取消费记录
    consumptions = await ConsumptionDAO.get_by_date_range(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        transaction_type=transaction_type
    )
    
    if not consumptions:
        return error_response(
            code=4005,
            message="该时间范围内没有消费记录",
            status_code=404
        )
    
    # 分析消费行为并生成任务规划（启用文件保存功能）
    analysis_result = analyze_and_plan(user_id, consumptions, save_to_files=True)
    
    # 构建响应数据
    response_data = {
        "user_info": {
            "id": user.id,
            "name": user.name,
            "analysis_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
        },
        "analysis": analysis_result["analysis"],
        "task_plan": analysis_result["plan"],
        "consumption_count": analysis_result["consumption_count"],
        "generated_at": analysis_result["timestamp"]
    }
    
    # 如果结果包含文件路径信息，则添加到响应中
    if "md_file_path" in analysis_result:
        response_data["file_paths"] = {
            "markdown": analysis_result["md_file_path"],
            "pdf": analysis_result["pdf_file_path"],
            "workspace": analysis_result["workspace_dir"]
        }
    
    return success_response(
        message="获取消费行为分析成功",
        data=response_data
    )


@consumption_analysis_router.post("/execute-task", response_model=dict)
async def execute_task(
    task_id: str = Query(..., description="任务ID"),
    task_description: str = Query(..., description="任务描述")
) -> dict:
    """
    执行指定的任务
    
    Args:
        task_id: 任务ID
        task_description: 任务描述
    
    Returns:
        任务执行结果
    """
    try:
        # 执行任务
        result = execute_agent_task(task_id, task_description)
        
        return success_response(
            message="任务执行成功",
            data=result
        )
    except Exception as e:
        return error_response(
            code=5000,
            message=f"任务执行失败: {str(e)}",
            status_code=500
        )


@consumption_analysis_router.get("/user/{user_id}/recent-analysis", response_model=dict)
async def get_recent_consumption_analysis(
    user_id: int,
    days: int = Query(30, ge=1, le=365, description="过去天数")
) -> dict:
    """
    获取用户最近一段时间的消费行为分析
    
    Args:
        user_id: 用户ID
        days: 过去的天数（默认30天）
    
    Returns:
        包含消费分析和任务规划的响应
    """
    # 计算日期范围
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    # 调用已有的分析接口
    return await get_consumption_analysis(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        transaction_type="支出"
    )