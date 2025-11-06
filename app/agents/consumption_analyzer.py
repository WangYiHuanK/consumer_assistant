"""消费行为分析和任务规划模块"""
import os
from typing import List, Dict, Any
from datetime import date, datetime
from app.models.consumption import Consumption
from app.agents.agents import llm
from app.agents.mcp_tool import save_markdown_and_convert_to_pdf
from app.utils.chart_generator import get_chart_generator


# 消费分析提示词模板
CONSUMPTION_ANALYSIS_PROMPT = """
请根据以下消费记录数据，对用户的消费行为进行分析：

用户消费记录：
{consumption_data}

请提供以下内容：
1. 消费总览：总体消费趋势、主要支出类别
2. 消费习惯分析：是否存在冲动消费、消费偏好等
3. 消费建议：如何优化消费结构、节省开支等
4. 可能的消费问题：是否存在过度消费、不合理消费等

请使用简洁明了的语言进行分析，使用小标题分隔不同部分。
"""

# 任务规划提示词模板
TASK_PLANNING_PROMPT = """
基于以下消费分析结果，请生成一个消费优化的任务规划：

消费分析结果：
{analysis_result}

请规划一系列合理的步骤，帮助用户优化消费行为。每个步骤应该：
1. 清晰明确的目标
2. 具体可执行的行动
3. 预期达成的效果
4. 建议的时间框架

请按照优先级排序任务，每个任务分配一个唯一的ID，并说明哪些任务适合使用自动化工具或agent执行。
"""


def format_consumption_data(consumptions: List[Consumption]) -> str:
    """
    将消费记录数据格式化为适合大模型处理的字符串
    
    Args:
        consumptions: 消费记录列表
    
    Returns:
        格式化后的消费记录字符串
    """
    formatted_data = []
    
    for consumption in consumptions:
        # 格式化每条消费记录
        record = (f"- 日期: {consumption.transaction_time.strftime('%Y-%m-%d %H:%M:%S')}, "
                 f"类型: {consumption.transaction_type}, "
                 f"金额: {float(consumption.amount)}元, "
                 f"商户: {consumption.merchant_name}, "
                 f"分类: {consumption.category or '未分类'}")
        formatted_data.append(record)
    
    return "\n".join(formatted_data)


def analyze_consumption_patterns(consumptions: List[Consumption]) -> str:
    """
    使用大模型分析用户消费模式
    
    Args:
        consumptions: 消费记录列表
    
    Returns:
        消费分析结果
    """
    # 格式化消费数据
    formatted_data = format_consumption_data(consumptions)
    
    # 构建提示词
    prompt = CONSUMPTION_ANALYSIS_PROMPT.format(consumption_data=formatted_data)
    
    # 调用大模型
    analysis_result = llm.invoke(prompt)
    
    return analysis_result


def generate_task_plan(analysis_result: str) -> str:
    """
    使用大模型基于消费分析结果生成任务规划
    
    Args:
        analysis_result: 消费分析结果
    
    Returns:
        任务规划内容
    """
    # 构建提示词
    prompt = TASK_PLANNING_PROMPT.format(analysis_result=analysis_result)
    
    # 调用大模型
    task_plan = llm.invoke(prompt)
    
    return task_plan


def execute_agent_task(task_id: str, task_description: str) -> Dict[str, Any]:
    """
    执行agent任务（根据任务ID和描述执行相应操作）
    
    Args:
        task_id: 任务ID
        task_description: 任务描述
    
    Returns:
        任务执行结果
    """
    # 这里可以根据具体的任务ID实现不同的自动化操作
    # 目前返回一个模拟的执行结果
    return {
        "task_id": task_id,
        "status": "completed",
        "message": f"已执行任务: {task_description}",
        "timestamp": datetime.now().isoformat()
    }


def analyze_and_plan(user_id: int, consumptions: List[Consumption], save_to_files: bool = True) -> Dict[str, Any]:
    """
    综合分析消费数据并生成规划
    
    Args:
        user_id: 用户ID
        consumptions: 消费记录列表
        save_to_files: 是否保存分析结果为文件（Markdown和PDF）
    
    Returns:
        包含分析、规划和文件路径的字典
    """
    # 分析消费模式
    analysis = analyze_consumption_patterns(consumptions)
    
    # 生成任务规划
    plan = generate_task_plan(analysis)
    
    # 初始化图表相关内容
    chart_sections = ""
    chart_paths = []
    
    # 保存为文件（如果启用）
    if save_to_files:
        # 生成文件名前缀，包含用户ID和时间戳
        filename_prefix = f"user_{user_id}_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 使用MCP工具获取工作空间目录
        temp_file_paths = save_markdown_and_convert_to_pdf("", filename_prefix)
        workspace_dir = temp_file_paths["workspace_dir"]
        
        # 生成图表
        chart_generator = get_chart_generator(workspace_dir)
        chart_paths = chart_generator.generate_all_charts(consumptions)
        
        # 构建图表部分的Markdown内容，使用更清晰的文件路径处理
        chart_sections = "## 消费数据可视化\n\n"
        
        # 确保图表路径正确处理
        if chart_paths:
            # 固定使用'charts'作为文件夹名称，因为图表生成器总是在工作空间下创建charts子目录
            chart_folder_name = 'charts'
            
            # 添加消费类别分布图
            if len(chart_paths) > 0:
                chart_filename = os.path.basename(chart_paths[0])
                # 强制使用charts前缀的路径
                chart_path = f"charts/{chart_filename}"
                chart_sections += "### 消费类别分布\n\n"
                chart_sections += f"![消费类别分布]({chart_path})\n\n"
                print(f"使用图表路径: {chart_path}")
            
            # 添加消费趋势图
            if len(chart_paths) > 1:
                chart_filename = os.path.basename(chart_paths[1])
                # 强制使用charts前缀的路径
                chart_path = f"charts/{chart_filename}"
                chart_sections += "### 消费趋势分析\n\n"
                chart_sections += f"![消费趋势分析]({chart_path})\n\n"
                print(f"使用图表路径: {chart_path}")
            
            # 添加收支总览图
            if len(chart_paths) > 2:
                chart_filename = os.path.basename(chart_paths[2])
                # 强制使用charts前缀的路径
                chart_path = f"charts/{chart_filename}"
                chart_sections += "### 收支总览\n\n"
                chart_sections += f"![收支总览]({chart_path})\n\n"
                print(f"使用图表路径: {chart_path}")
    
    # 构建完整的分析报告Markdown内容
    full_report = f"""
# 用户消费行为分析报告

## 基本信息
- **用户ID**: {user_id}
- **分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **分析记录数**: {len(consumptions)}

{chart_sections}

## 消费行为分析
{analysis}

## 任务规划
{plan}
    """
    
    # 初始化结果字典
    result = {
        "user_id": user_id,
        "analysis": analysis,
        "plan": plan,
        "full_report": full_report,
        "timestamp": datetime.now().isoformat(),
        "consumption_count": len(consumptions)
    }
    
    # 保存为文件（如果启用）
    if save_to_files:
        # 使用MCP工具保存并转换文件
        file_paths = save_markdown_and_convert_to_pdf(full_report, filename_prefix)
        
        # 将文件路径添加到结果中
        result.update({
            "md_file_path": file_paths["md_path"],
            "pdf_file_path": file_paths["pdf_path"],
            "workspace_dir": file_paths["workspace_dir"],
            "chart_paths": chart_paths
        })
    
    return result