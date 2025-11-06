"""消费行为分析和任务规划相关API接口"""
from fastapi import APIRouter, Query, HTTPException, Body
from typing import Optional, Dict, Any
from datetime import date, datetime, timedelta
from app.dao import ConsumptionDAO, UserDAO
from app.settings.response import success_response, error_response
from app.agents.consumption_analyzer import analyze_and_plan, execute_agent_task
from app.agents.advanced_consumption_agent import AdvancedConsumptionAgent

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


@consumption_analysis_router.post("/user/{user_id}/custom-analysis", response_model=dict)
async def custom_consumption_analysis(
    user_id: int,
    start_date: str = Body(..., description="开始日期，格式YYYY-MM-DD", example="2024-01-01"),
    end_date: str = Body(..., description="结束日期，格式YYYY-MM-DD", example="2024-12-31"),
    analysis_needs: str = Body(..., description="分析需求描述", example="分析我的饮食消费模式，找出省钱机会")
) -> dict:
    """
    根据用户自定义需求进行消费分析
    
    Args:
        user_id: 用户ID
        start_date: 开始日期，格式YYYY-MM-DD
        end_date: 结束日期，格式YYYY-MM-DD
        analysis_needs: 详细的分析需求描述
    
    Returns:
        包含分析结果和报告路径的响应
    """
    try:
        # 验证用户是否存在
        user = await UserDAO.get_by_id(user_id)
        if not user:
            return error_response(
                code=4004,
                message="用户不存在"
            )
        
        # 验证日期格式和范围
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            return error_response(
                code=4001,
                message="日期格式错误，请使用YYYY-MM-DD格式"
            )
        
        if start > end:
            return error_response(
                code=4002,
                message="开始日期不能晚于结束日期"
            )
        
        if end > date.today():
            return error_response(
                code=4003,
                message="结束日期不能超过当前日期"
            )
        
        # 限制最大时间范围为一年
        max_range = timedelta(days=365)
        if end - start > max_range:
            return error_response(
                code=4004,
                message="分析时间范围不能超过一年"
            )
        
        print(f"\n开始执行自定义消费分析:")
        print(f"用户ID: {user_id}")
        print(f"时间范围: {start_date} 至 {end_date}")
        print(f"分析需求: {analysis_needs}")
        
        # 创建高级消费分析Agent并执行分析
        agent = AdvancedConsumptionAgent()
        results = await agent.analyze_by_custom_needs(user_id, start_date, end_date, analysis_needs)
        
        # 构建响应数据
        response_data = {
            "user_info": {
                "id": user.id,
                "name": user.name
            },
            "analysis_params": {
                "start_date": start_date,
                "end_date": end_date,
                "analysis_needs": analysis_needs
            },
            "execution_plan": {
                "task_count": len(results.get('plan', [])),
                "execution_status": {
                    task_id: "成功" if task_result['success'] else "失败" 
                    for task_id, task_result in results.get('execution_results', {}).items()
                }
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # 添加报告路径信息
        report_paths = results.get('report_paths', {})
        if report_paths:
            response_data["report_files"] = {
                "markdown_path": report_paths.get('markdown_path', ""),
                "pdf_path": report_paths.get('pdf_path', "")
            }
        
        # 添加失败任务的错误信息
        failed_tasks = {}
        for task_id, task_result in results.get('execution_results', {}).items():
            if not task_result['success']:
                failed_tasks[task_id] = task_result.get('error', '未知错误')
        
        if failed_tasks:
            response_data["failed_tasks"] = failed_tasks
        
        return success_response(
            message="自定义消费分析完成",
            data=response_data
        )
        
    except Exception as e:
        print(f"自定义分析执行错误: {e}")
        return error_response(
            code=5000,
            message=f"分析执行失败: {str(e)}"
        )