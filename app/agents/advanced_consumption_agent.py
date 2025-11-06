"""高级消费分析Agent - 支持自定义分析需求和自主工具调用"""
import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, date
from app.models.consumption import Consumption
from app.agents.base_agent import BaseAgent
from app.agents.consumption_mcp_tool import get_consumption_mcp_tool
from app.dao.consumption_dao import ConsumptionDAO


class AdvancedConsumptionAgent(BaseAgent):
    """
    高级消费分析Agent
    支持用户自定义分析需求、时间范围、自动规划和工具调用
    """
    
    def __init__(self):
        """
        初始化高级消费分析Agent
        """
        super().__init__("消费分析专家")
        
        # 初始化MCP工具
        self.mcp_tool = get_consumption_mcp_tool()
        
        # 添加提示词模板
        self._init_prompt_templates()
        
        # 注册工具
        self._register_tools()
        
        # 初始化DAO
        self.consumption_dao = ConsumptionDAO()
        
        # 初始化图表生成器
        from app.utils.chart_generator import get_chart_generator
        current_dir = os.path.dirname(os.path.abspath(__file__))
        workspace_dir = os.path.normpath(os.path.join(current_dir, '..', '..', 'workspace'))
        self.chart_generator = get_chart_generator(workspace_dir)
    
    def _init_prompt_templates(self):
        """
        初始化提示词模板
        """
        # 自定义分析提示词模板
        self.add_prompt_template(
            "custom_analysis",
            """
            请根据用户的分析需求和以下消费记录数据，进行个性化分析：
            
            用户分析需求：{analysis_needs}
            
            消费记录数据：
            {consumption_data}
            
            请提供详细的分析结果，包括：
            1. 针对用户需求的专项分析
            2. 数据洞察和趋势
            3. 具体建议和行动计划
            4. 可能的改进机会
            
            请使用清晰的结构和小标题，确保分析结果有针对性且实用。
            """
        )
        
        # 任务规划提示词模板
        self.add_prompt_template(
            "task_planning",
            """
            作为消费分析专家，请基于用户的分析需求生成详细的任务规划。
            
            用户需求：{analysis_needs}
            时间范围：从{start_date}到{end_date}
            
            可用工具信息：
            {tools_info}
            
            请规划一系列任务，帮助完成分析并生成最终报告。每个任务应该：
            1. 有明确的目标
            2. 调用上述工具列表中的一个工具
            3. 提供正确的工具参数格式
            4. 按照逻辑顺序排列
            
            请严格按照JSON格式输出任务规划，只包含任务数组。
            """
        )
        
        # 数据筛选提示词模板
        self.add_prompt_template(
            "data_filtering",
            """
            用户分析需求：{analysis_needs}
            
            基于用户需求，请确定：
            1. 是否需要特定类型的消费数据？（如特定类别、金额范围等）
            2. 是否需要添加额外的数据维度？
            3. 是否需要数据聚合方式？（如按日、周、月聚合）
            
            请以JSON格式返回筛选条件和聚合方式。
            """
        )
    
    def _register_tools(self):
        """
        注册Agent可用的工具
        """
        # 从MCP工具中获取工具信息
        self.tools_info = self._get_tools_info()
        
        # 注册实际的方法函数，而不是元数据字典
        self.register_tool("fetch_consumption_data", self.fetch_consumption_data)
        self.register_tool("filter_data", self.filter_data)
        self.register_tool("generate_charts", self.generate_charts)
        self.register_tool("analyze_data", self.analyze_data)
        self.register_tool("generate_suggestions", self.generate_suggestions)
        self.register_tool("market_research", self.market_research)
        self.register_tool("generate_report", self.generate_report)
    
    def _get_tools_info(self):
        """
        获取所有可用工具的详细信息，用于提示词模板
        """
        tools_info = []
        for tool_name, tool_func in self.mcp_tool.available_tools.items():
            # 获取工具函数的文档字符串
            doc = getattr(tool_func, '__doc__', '暂无描述') or '暂无描述'
            
            # 尝试获取参数信息，处理不同类型的工具函数
            params = []
            try:
                if hasattr(tool_func, '__code__'):
                    # 对于普通函数
                    params = list(tool_func.__code__.co_varnames[:tool_func.__code__.co_argcount])
                    # 移除self参数（如果存在）
                    if params and params[0] == 'self':
                        params = params[1:]
            except Exception:
                # 如果无法获取参数信息，提供默认参数描述
                if tool_name in ['数据采集工具', 'fetch_consumption_data']:
                    params = ['user_id', 'start_date', 'end_date']
                elif tool_name in ['数据过滤工具', 'filter_data']:
                    params = ['data', 'filters']
                elif tool_name in ['数据分析工具', 'analyze_data']:
                    params = ['consumptions', 'analysis_type']
                else:
                    params = []
            
            # 构建工具信息字典
            tool_info = {
                "name": tool_name,
                "description": doc.strip(),
                "parameters": params
            }
            tools_info.append(tool_info)
        
        return json.dumps(tools_info, ensure_ascii=False, indent=2)
    
    def plan(self, analysis_needs: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        为用户需求生成任务规划
        
        Args:
            analysis_needs: 用户的分析需求
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            任务规划列表
        """
        # 使用LLM生成任务规划
        prompt = self.format_prompt(
            "task_planning",
            analysis_needs=analysis_needs,
            start_date=start_date,
            end_date=end_date,
            tools_info=self.tools_info
        )
        
        # 调用LLM生成任务规划
        response = self.invoke_llm(prompt)
        
        try:
            # 解析JSON响应
            plan = json.loads(response)
            return plan
        except json.JSONDecodeError:
            # 如果解析失败，返回默认计划
            return []
            
    async def fetch_consumption_data(self, user_id: int, start_date: str, end_date: str) -> List[Consumption]:
        """
        获取消费数据（异步方法）
        
        Args:
            user_id: 用户ID
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
        
        Returns:
            消费记录列表
        """
        # 转换日期字符串为日期对象
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        # 从数据库获取数据（异步调用）
        # 使用正确的方法名get_by_date_range并使用await
        consumptions = await self.consumption_dao.get_by_date_range(user_id, start, end)
        
        # 添加到记忆
        self.add_memory({
            "action": "fetch_data",
            "user_id": user_id,
            "start_date": start_date,
            "end_date": end_date,
            "record_count": len(consumptions)
        })
        
        return consumptions
    
    def filter_data(self, consumptions: List[Consumption], filters: Dict[str, Any] = None) -> List[Consumption]:
        """
        筛选数据
        
        Args:
            consumptions: 原始消费记录
            filters: 筛选条件
        
        Returns:
            筛选后的消费记录
        """
        if not filters:
            return consumptions
        
        filtered = []
        for consumption in consumptions:
            match = True
            
            # 按类别筛选
            if "categories" in filters and consumption.category not in filters["categories"]:
                match = False
            
            # 按金额范围筛选
            if "min_amount" in filters and consumption.amount < filters["min_amount"]:
                match = False
            if "max_amount" in filters and consumption.amount > filters["max_amount"]:
                match = False
            
            # 按描述关键词筛选
            if "keywords" in filters:
                keywords_match = False
                for keyword in filters["keywords"]:
                    if keyword.lower() in consumption.description.lower():
                        keywords_match = True
                        break
                if not keywords_match:
                    match = False
            
            if match:
                filtered.append(consumption)
        
        return filtered
    
    def generate_charts(self, consumptions: List[Consumption]) -> Dict[str, str]:
        """
        生成图表
        
        Args:
            consumptions: 消费记录
        
        Returns:
            图表路径字典
        """
        chart_paths = self.chart_generator.generate_all_charts(consumptions)
        return chart_paths
    
    def analyze_data(self, consumptions: List[Consumption], analysis_needs: str) -> str:
        """
        分析数据
        
        Args:
            consumptions: 消费记录
            analysis_needs: 用户分析需求
        
        Returns:
            分析结果
        """
        # 格式化消费数据
        formatted_data = self._format_consumption_data(consumptions)
        
        # 生成分析提示词
        prompt = self.format_prompt(
            "custom_analysis",
            analysis_needs=analysis_needs,
            consumption_data=formatted_data
        )
        
        # 调用模型进行分析
        analysis_result = self.invoke_llm(prompt)
        
        return analysis_result
    
    def generate_report(self, analysis_result: str, chart_paths: Any, 
                       user_id: int, start_date: str, end_date: str) -> Dict[str, str]:
        """
        生成报告
        
        Args:
            analysis_result: 分析结果
            chart_paths: 图表路径（可以是列表或字典）
            user_id: 用户ID
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            报告文件路径
        """
        # 构建报告内容
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 基础信息部分
        markdown_content = f"""
# 消费分析报告

## 基本信息
- **用户ID**: {user_id}
- **分析周期**: {start_date} 至 {end_date}
- **生成时间**: {timestamp}

"""
        
        # 添加分析结果部分
        markdown_content += """
## 分析结果

"""
        
        # 添加图表部分
        if chart_paths:
            markdown_content += """
## 可视化图表

"""
            
            # 处理不同类型的chart_paths
            try:
                if isinstance(chart_paths, list):
                    # 如果是列表，使用默认图表名称
                    chart_types = ['消费类别分布', '消费趋势分析', '收支总览']
                    for i, chart_path in enumerate(chart_paths):
                        chart_type = chart_types[i] if i < len(chart_types) else f'图表{i+1}'
                        chart_filename = os.path.basename(chart_path)
                        # 确保图表引用路径包含charts前缀
                        markdown_content += f"""
### {chart_type}

![{chart_type}](charts/{chart_filename})

"""
                elif isinstance(chart_paths, dict):
                    # 如果是字典，使用键作为图表类型
                    for chart_type, chart_path in chart_paths.items():
                        chart_filename = os.path.basename(chart_path)
                        # 确保图表引用路径包含charts前缀
                        markdown_content += f"""
### {chart_type}

![{chart_type}](charts/{chart_filename})

"""
                else:
                    # 其他类型，添加警告
                    markdown_content += "图表数据格式不正确\n\n"
            except Exception as e:
                # 捕获任何处理图表时的错误
                markdown_content += f"处理图表时出错: {str(e)}\n\n"
        
        # 添加分析结果部分
        markdown_content += """
## 详细分析

"""
        markdown_content += analysis_result or "暂无分析结果"
        
        # 确保工作目录存在
        workspace_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'workspace')
        if not os.path.exists(workspace_dir):
            os.makedirs(workspace_dir)
        
        # 保存并转换为PDF，使用更精确的时间戳确保文件名唯一
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]  # 包含毫秒
        # 强制使用时间戳格式，确保每个文件都有唯一名称
        filename_prefix = f"consumption_analysis_{user_id}_{start_date}_{end_date}_{timestamp}"
        print(f"生成报告文件名前缀: {filename_prefix}")
        
        try:
            # 使用项目中现有的MCP工具来生成PDF
            from app.agents.mcp_tool import save_markdown_and_convert_to_pdf
            
            # 使用便捷函数保存Markdown并转换为PDF
            result = save_markdown_and_convert_to_pdf(markdown_content, filename_prefix)
            
            # 获取生成的文件路径
            markdown_path = result.get("md_path", "保存失败")
            pdf_path = result.get("pdf_path", "生成失败")
            
            print(f"Markdown文件已保存: {markdown_path}")
            print(f"PDF文件已生成: {pdf_path}")
            
        except Exception as e:
            print(f"生成报告失败: {e}")
            # 如果MCP工具失败，回退到简单的Markdown保存
            markdown_path = os.path.join(workspace_dir, f"{filename_prefix}.md")
            try:
                with open(markdown_path, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                print(f"回退到简单保存: {markdown_path}")
            except Exception:
                markdown_path = "保存失败"
            pdf_path = "生成失败"
        
        return {
            "markdown_path": markdown_path,
            "pdf_path": pdf_path
        }
    
    def generate_suggestions(self, analysis_result: str) -> str:
        """
        生成改善建议
        
        Args:
            analysis_result: 分析结果文本
            
        Returns:
            改善建议文本
        """
        # 基于分析结果生成建议
        prompt = f"""
        基于以下分析结果，生成具体的消费改善建议：
        
        {analysis_result}
        
        请提供3-5条具体、可操作的建议，帮助用户优化消费习惯。
        """
        
        suggestions = self.invoke_llm(prompt)
        
        # 添加到记忆
        self.add_memory({
            "action": "generate_suggestions",
            "suggestions": suggestions
        })
        
        return suggestions
    
    def communicate_result(self, result: Dict[str, Any]) -> str:
        """
        通信工具 - 将分析结果反馈给用户
        
        Args:
            result: 分析结果字典
            
        Returns:
            通信结果文本
        """
        # 格式化结果为用户友好的消息
        message = f"""
        尊敬的用户，您的消费分析已完成！
        
        分析概要：
        - 生成了详细的消费分析报告
        - 报告包含了针对您需求的专项分析
        - 提供了可视化图表帮助理解消费模式
        - 给出了个性化的改善建议
        
        您可以在以下位置查看完整报告：
        - Markdown版本: {result.get('markdown_path', '未生成')}
        - PDF版本: {result.get('pdf_path', '未生成')}
        
        如有任何问题，请随时咨询！
        """
        
        # 添加到记忆
        self.add_memory({
            "action": "communicate_result",
            "message": message
        })
        
        return message
    
    def market_research(self, category: str = None) -> Dict[str, Any]:
        """
        市场调研工具 - 提供行业标准或用户历史数据分析
        
        Args:
            category: 消费类别（可选）
            
        Returns:
            市场调研数据字典
        """
        # 模拟市场调研数据
        research_data = {
            "合理消费占比参考": {
                "食品餐饮": "25-30%",
                "住房缴费": "20-35%",
                "交通出行": "10-15%",
                "娱乐休闲": "5-10%",
                "购物消费": "10-20%",
                "医疗健康": "5-8%",
                "教育培训": "5-15%",
                "其他支出": "5-10%"
            },
            "季节性消费趋势": "冬季娱乐消费通常增加15-20%",
            "年度消费建议": "建议每月储蓄收入的20-30%"
        }
        
        # 如果指定了类别，只返回相关数据
        if category:
            result = {
                "category": category,
                "reasonable_ratio": research_data["合理消费占比参考"].get(category, "无特定参考值"),
                "industry_standard": research_data["合理消费占比参考"].get(category, "无特定参考值")
            }
        else:
            result = research_data
        
        # 添加到记忆
        self.add_memory({
            "action": "market_research",
            "category": category,
            "research_data": result
        })
        
        return result
    
    def _format_consumption_data(self, consumptions: List[Consumption]) -> str:
        """
        格式化消费数据
        
        Args:
            consumptions: 消费记录
        
        Returns:
            格式化的字符串
        """
        lines = []
        for consumption in consumptions:
            # 使用模型中实际存在的字段名
            line = f"交易时间: {consumption.transaction_time}, 类别: {consumption.category}, "
            line += f"金额: {consumption.amount}元, 交易类型: {consumption.transaction_type}, "
            line += f"商户名称: {consumption.merchant_name}"
            lines.append(line)
        
        return "\n".join(lines)
    
    async def analyze_by_custom_needs(self, user_id: int, start_date: str, end_date: str, 
                              analysis_needs: str) -> Dict[str, Any]:
        """
        根据用户自定义需求进行分析（异步方法）
        
        Args:
            user_id: 用户ID
            start_date: 开始日期
            end_date: 结束日期
            analysis_needs: 用户分析需求
        
        Returns:
            分析结果
        """
        # 生成分析计划
        plan = self.plan(analysis_needs, start_date, end_date)
        
        # 如果没有生成有效计划，使用默认计划
        if not plan:
            plan = [
                {
                    "id": "1",
                    "description": "获取消费数据",
                    "tool": "fetch_consumption_data",
                    "tool_params": {"user_id": user_id, "start_date": start_date, "end_date": end_date},
                    "priority": "高",
                    "expected_result": "获取指定时间范围内的消费记录"
                },
                {
                    "id": "2",
                    "description": "生成可视化图表",
                    "tool": "generate_charts",
                    "tool_params": {},
                    "priority": "中",
                    "expected_result": "生成消费类别分布、趋势和收支总览图"
                },
                {
                    "id": "3",
                    "description": "进行个性化分析",
                    "tool": "analyze_data",
                    "tool_params": {"analysis_needs": analysis_needs},
                    "priority": "高",
                    "expected_result": "根据用户需求生成详细分析"
                },
                {
                    "id": "4",
                    "description": "生成最终报告",
                    "tool": "generate_report",
                    "tool_params": {"user_id": user_id, "start_date": start_date, "end_date": end_date},
                    "priority": "高",
                    "expected_result": "生成包含分析和图表的Markdown和PDF报告"
                }
            ]
        
        # 存储中间结果
        intermediate_results = {}
        
        # 执行计划
        for task in plan:
            task_id = task.get('id')
            tool_name = task.get('tool')
            tool_params = task.get('tool_params', {})
            
            print(f"执行任务 {task_id}: {task.get('description')}")
            
            try:
                # 根据任务ID调整参数，使用之前的结果
                if task_id == "2":  # 生成图表需要消费数据
                    tool_params['consumptions'] = intermediate_results.get('1', {}).get('result', [])
                elif task_id == "3":  # 分析数据需要消费数据
                    tool_params['consumptions'] = intermediate_results.get('1', {}).get('result', [])
                elif task_id == "4":  # 生成报告需要分析结果和图表
                    # 安全获取分析结果
                    analysis_result = intermediate_results.get('3', {}).get('result', '')
                    # 安全获取图表路径，接受任何类型
                    chart_paths = intermediate_results.get('2', {}).get('result', [])
                    
                    tool_params['analysis_result'] = analysis_result
                    tool_params['chart_paths'] = chart_paths
                
                # 执行工具（处理异步和同步方法）
                if tool_name == "fetch_consumption_data":
                    # 直接调用异步方法
                    result = await getattr(self, tool_name)(**tool_params)
                else:
                    # 其他同步方法
                    result = getattr(self, tool_name)(**tool_params)
                
                # 存储结果
                intermediate_results[task_id] = {
                    "success": True,
                    "result": result
                }
                
            except Exception as e:
                intermediate_results[task_id] = {
                    "success": False,
                    "error": str(e)
                }
                print(f"任务 {task_id} 执行失败: {e}")
                # 继续执行其他任务
        
        # 准备最终结果，确保返回正确的结构
        final_result = {
            "plan": plan,
            "execution_results": intermediate_results,
            "report_paths": None
        }
        
        # 如果生成了报告，将其路径添加到结果中
        report_result = intermediate_results.get('4', {}).get('result')
        if report_result and isinstance(report_result, dict):
            final_result["report_paths"] = report_result
        
        # 返回最终结果
        final_result = {
            "plan": plan,
            "execution_results": intermediate_results,
            "report_paths": intermediate_results.get('4', {}).get('result', {})
        }
        
        return final_result