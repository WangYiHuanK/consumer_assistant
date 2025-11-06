"""消费分析MCP工具 - 为模型提供标准化的工具接口"""
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from app.models.consumption import Consumption
from app.dao.consumption_dao import ConsumptionDAO
from app.utils.chart_generator import get_chart_generator
from app.agents.mcp_tool import MCPTool


class ConsumptionMCPTool(MCPTool):
    """
    消费分析模型控制程序工具类，为大语言模型提供标准化的工具接口
    """
    
    def __init__(self, workspace_dir: Optional[str] = None):
        """
        初始化消费分析MCP工具
        
        Args:
            workspace_dir: 工作空间目录路径
        """
        # 如果未提供工作目录，使用默认路径
        if workspace_dir is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            workspace_dir = os.path.normpath(os.path.join(current_dir, '..', '..', 'workspace'))
            # 创建工作目录（如果不存在）
            os.makedirs(workspace_dir, exist_ok=True)
        
        super().__init__(workspace_dir)
        
        # 初始化DAO和图表生成器，确保正确导入依赖
        from app.utils.chart_generator import get_chart_generator
        self.consumption_dao = ConsumptionDAO()
        self.chart_generator = get_chart_generator(workspace_dir)
        
        # 注册所有可用工具
        self.available_tools = {
            "fetch_consumption_data": {
                "name": "fetch_consumption_data",
                "description": "获取指定用户和时间范围的消费数据",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "integer",
                            "description": "用户ID"
                        },
                        "start_date": {
                            "type": "string",
                            "description": "开始日期，格式：YYYY-MM-DD"
                        },
                        "end_date": {
                            "type": "string",
                            "description": "结束日期，格式：YYYY-MM-DD"
                        }
                    },
                    "required": ["user_id", "start_date", "end_date"]
                }
            },
            "filter_data": {
                "name": "filter_data",
                "description": "根据条件筛选消费数据",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "consumptions": {
                            "type": "array",
                            "description": "消费数据列表"
                        },
                        "filters": {
                            "type": "object",
                            "description": "筛选条件，如{\"category\": \"食品餐饮\"}"
                        }
                    },
                    "required": ["consumptions"]
                }
            },
            "generate_charts": {
                "name": "generate_charts",
                "description": "生成消费数据的可视化图表",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "consumptions": {
                            "type": "array",
                            "description": "消费数据列表"
                        }
                    },
                    "required": ["consumptions"]
                }
            },
            "analyze_data": {
                "name": "analyze_data",
                "description": "根据用户需求分析消费数据",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "consumptions": {
                            "type": "array",
                            "description": "消费数据列表"
                        },
                        "analysis_needs": {
                            "type": "string",
                            "description": "用户的分析需求"
                        }
                    },
                    "required": ["consumptions", "analysis_needs"]
                }
            },
            "generate_suggestions": {
                "name": "generate_suggestions",
                "description": "基于分析结果生成改善建议",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "analysis_result": {
                            "type": "string",
                            "description": "分析结果文本"
                        }
                    },
                    "required": ["analysis_result"]
                }
            },
            "market_research": {
                "name": "market_research",
                "description": "获取市场调研数据和行业标准",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": "消费类别（可选）"
                        }
                    }
                }
            },
            "generate_report": {
                "name": "generate_report",
                "description": "生成分析报告并转换为PDF",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "analysis_result": {
                            "type": "string",
                            "description": "分析结果文本"
                        },
                        "chart_paths": {
                            "type": "object",
                            "description": "图表路径字典"
                        },
                        "user_id": {
                            "type": "integer",
                            "description": "用户ID"
                        },
                        "start_date": {
                            "type": "string",
                            "description": "开始日期"
                        },
                        "end_date": {
                            "type": "string",
                            "description": "结束日期"
                        }
                    },
                    "required": ["analysis_result", "chart_paths", "user_id", "start_date", "end_date"]
                }
            }
        }
    
    def get_available_tools(self) -> Dict[str, Any]:
        """
        获取所有可用工具的信息
        
        Returns:
            工具信息字典
        """
        return self.available_tools
    
    def fetch_consumption_data(self, user_id: int, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        获取消费数据
        
        Args:
            user_id: 用户ID
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
        
        Returns:
            消费记录列表（字典格式）
        """
        try:
            # 转换日期字符串为日期对象
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
            
            # 从数据库获取数据
            consumptions = self.consumption_dao.get_by_user_and_date_range(user_id, start, end)
            
            # 转换为字典格式
            result = []
            for item in consumptions:
                result.append({
                    "id": item.id,
                    "user_id": item.user_id,
                    "amount": float(item.amount),
                    "category": item.category,
                    "description": item.description,
                    "transaction_time": item.transaction_time.isoformat() if item.transaction_time else None,
                    "created_at": item.created_at.isoformat() if item.created_at else None
                })
            
            return result
        except Exception as e:
            return {"error": str(e)}
    
    def filter_data(self, consumptions: List[Dict[str, Any]], filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        筛选消费数据
        
        Args:
            consumptions: 消费数据列表
            filters: 筛选条件
        
        Returns:
            筛选后的消费数据列表
        """
        try:
            if not filters:
                return consumptions
            
            filtered_data = []
            for item in consumptions:
                match = True
                for key, value in filters.items():
                    if key in item and item[key] != value:
                        match = False
                        break
                if match:
                    filtered_data.append(item)
            
            return filtered_data
        except Exception as e:
            return {"error": str(e)}
    
    def generate_charts(self, consumptions: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        生成图表
        
        Args:
            consumptions: 消费数据列表
        
        Returns:
            图表路径字典
        """
        try:
            # 转换回模型对象格式以便图表生成器使用
            consumption_objects = []
            for item in consumptions:
                consumption = Consumption(
                    id=item.get("id"),
                    user_id=item.get("user_id"),
                    amount=item.get("amount"),
                    category=item.get("category"),
                    description=item.get("description")
                )
                if item.get("transaction_time"):
                    consumption.transaction_time = datetime.fromisoformat(item.get("transaction_time"))
                if item.get("created_at"):
                    consumption.created_at = datetime.fromisoformat(item.get("created_at"))
                consumption_objects.append(consumption)
            
            return self.chart_generator.generate_consumption_charts(consumption_objects)
        except Exception as e:
            return {"error": str(e)}
    
    def analyze_data(self, consumptions: List[Dict[str, Any]], analysis_needs: str) -> str:
        """
        分析数据
        
        Args:
            consumptions: 消费数据列表
            analysis_needs: 分析需求
        
        Returns:
            分析结果文本
        """
        try:
            # 这里可以添加更复杂的分析逻辑
            # 目前返回数据摘要作为示例
            total_amount = sum(item.get("amount", 0) for item in consumptions)
            category_summary = {}
            
            for item in consumptions:
                category = item.get("category", "其他")
                if category not in category_summary:
                    category_summary[category] = 0
                category_summary[category] += item.get("amount", 0)
            
            analysis = f"""
            # 消费数据分析结果
            
            ## 基本统计
            - 总消费金额: {total_amount:.2f}元
            - 消费记录数: {len(consumptions)}条
            
            ## 分类统计
            """
            
            for category, amount in category_summary.items():
                percentage = (amount / total_amount * 100) if total_amount > 0 else 0
                analysis += f"- {category}: {amount:.2f}元 ({percentage:.1f}%)\n"
            
            analysis += f"\n## 用户需求分析\n根据您的需求 '{analysis_needs}'，系统已完成相关数据的整理和统计。"
            
            return analysis
        except Exception as e:
            return f"分析失败: {str(e)}"
    
    def generate_suggestions(self, analysis_result: str) -> str:
        """
        生成建议
        
        Args:
            analysis_result: 分析结果
        
        Returns:
            建议文本
        """
        return "根据分析结果，建议您：\n1. 定期检查消费记录，了解消费习惯\n2. 设定合理的消费预算\n3. 优先保障必要支出，控制非必要开支"
    
    def market_research(self, category: str = None) -> Dict[str, Any]:
        """
        市场调研
        
        Args:
            category: 消费类别
        
        Returns:
            市场调研数据
        """
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
            }
        }
        
        if category:
            return {
                "category": category,
                "reasonable_ratio": research_data["合理消费占比参考"].get(category, "无特定参考值")
            }
        
        return research_data
    
    def generate_report(self, analysis_result: str, chart_paths: Dict[str, str], 
                       user_id: int, start_date: str, end_date: str) -> Dict[str, str]:
        """
        生成报告
        
        Args:
            analysis_result: 分析结果
            chart_paths: 图表路径
            user_id: 用户ID
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            报告文件路径
        """
        try:
            # 构建报告内容
            report_content = f"""# 消费分析报告

## 基本信息
- **用户ID**: {user_id}
- **分析周期**: {start_date} 至 {end_date}
- **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 分析结果
{analysis_result}

## 可视化图表
"""
            
            # 添加图表
            for chart_name, chart_path in chart_paths.items():
                if os.path.exists(chart_path):
                    report_content += f"\n### {chart_name}\n![{chart_name}]({chart_path})\n"
            
            # 保存报告
            filename_prefix = f"consumption_analysis_{user_id}_{start_date}_{end_date}"
            result = self.convert_and_save(report_content, filename_prefix)
            
            return result
        except Exception as e:
            return {"error": str(e)}


# 创建全局MCP工具实例
consumption_mcp_tool = ConsumptionMCPTool()


def get_consumption_mcp_tool() -> ConsumptionMCPTool:
    """
    获取消费分析MCP工具实例
    
    Returns:
        ConsumptionMCPTool实例
    """
    return consumption_mcp_tool