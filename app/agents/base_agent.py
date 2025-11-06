"""Agent基类模块 - 提供Agent的通用功能"""
import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.agents.agents import llm


class BaseAgent:
    """
    Agent基类，提供Agent的通用功能
    包括：提示词管理、模型调用、记忆机制、工具使用等
    """
    
    def __init__(self, agent_name: str):
        """
        初始化Agent
        
        Args:
            agent_name: Agent名称
        """
        self.agent_name = agent_name
        self.name = agent_name  # 添加name属性以确保子类可以访问
        self.memory = []  # 简单的记忆存储
        self.prompts = {}  # 提示词模板存储
        self.tools = {}  # 可用工具存储
    
    def add_memory(self, content: Dict[str, Any]):
        """
        添加记忆
        
        Args:
            content: 要存储的记忆内容，包含时间戳
        """
        memory_item = {
            "timestamp": datetime.now().isoformat(),
            **content
        }
        self.memory.append(memory_item)
    
    def get_memory(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        获取记忆
        
        Args:
            limit: 返回的记忆数量限制
        
        Returns:
            记忆列表
        """
        if limit:
            return self.memory[-limit:]
        return self.memory
    
    def add_prompt_template(self, key: str, template: str):
        """
        添加提示词模板
        
        Args:
            key: 模板标识符
            template: 提示词模板字符串
        """
        self.prompts[key] = template
    
    def get_prompt_template(self, key: str) -> Optional[str]:
        """
        获取提示词模板
        
        Args:
            key: 模板标识符
        
        Returns:
            提示词模板字符串，如果不存在则返回None
        """
        return self.prompts.get(key)
    
    def format_prompt(self, key: str, **kwargs) -> Optional[str]:
        """
        格式化提示词
        
        Args:
            key: 模板标识符
            **kwargs: 模板参数
        
        Returns:
            格式化后的提示词
        """
        template = self.get_prompt_template(key)
        if template:
            return template.format(**kwargs)
        return None
    
    def invoke_llm(self, prompt: str) -> str:
        """
        调用大语言模型
        
        Args:
            prompt: 提示词
        
        Returns:
            模型响应
        """
        response = llm.invoke(prompt)
        return response.strip()
    
    def register_tool(self, tool_name: str, tool_func):
        """
        注册工具
        
        Args:
            tool_name: 工具名称
            tool_func: 工具函数
        """
        self.tools[tool_name] = tool_func
    
    def use_tool(self, tool_name: str, **kwargs) -> Any:
        """
        使用工具
        
        Args:
            tool_name: 工具名称
            **kwargs: 工具参数
        
        Returns:
            工具执行结果
        """
        if tool_name in self.tools:
            result = self.tools[tool_name](**kwargs)
            return result
        raise ValueError(f"工具 {tool_name} 未注册")
    
    def plan(self, goal: str) -> List[Dict[str, Any]]:
        """
        根据目标生成执行计划
        
        Args:
            goal: 目标描述
        
        Returns:
            任务计划列表
        """
        # 构建规划提示词
        planning_prompt = f"""
        作为{self.agent_name}，请为以下目标生成一个执行计划：
        
        目标：{goal}
        
        请返回一个JSON格式的任务列表，每个任务包含：
        1. id: 任务ID
        2. description: 任务描述
        3. tool: 需要使用的工具名称（如果需要）
        4. tool_params: 工具参数（如果需要）
        5. priority: 优先级（高、中、低）
        6. expected_result: 预期结果
        """
        
        # 调用模型生成计划
        plan_json = self.invoke_llm(planning_prompt)
        
        # 解析JSON响应
        try:
            # 提取JSON部分
            start_idx = plan_json.find('{')
            end_idx = plan_json.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                plan_json = plan_json[start_idx:end_idx]
            plan = json.loads(plan_json)
            # 确保返回的是列表
            if isinstance(plan, dict) and 'tasks' in plan:
                return plan['tasks']
            elif isinstance(plan, list):
                return plan
            else:
                return [plan]
        except Exception as e:
            print(f"解析计划失败: {e}")
            # 返回默认计划
            return [{
                "id": "1",
                "description": "执行默认任务",
                "tool": None,
                "tool_params": {},
                "priority": "高",
                "expected_result": "完成基本任务"
            }]
    
    def execute_plan(self, plan: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        执行计划
        
        Args:
            plan: 任务计划列表
        
        Returns:
            执行结果
        """
        results = {}
        
        for task in plan:
            task_id = task.get('id', 'unknown')
            description = task.get('description', '')
            tool_name = task.get('tool')
            tool_params = task.get('tool_params', {})
            
            print(f"执行任务 {task_id}: {description}")
            
            try:
                if tool_name:
                    # 使用工具
                    result = self.use_tool(tool_name, **tool_params)
                else:
                    # 直接处理
                    result = self._process_task(task)
                
                results[task_id] = {
                    "success": True,
                    "result": result,
                    "description": description
                }
                
            except Exception as e:
                results[task_id] = {
                    "success": False,
                    "error": str(e),
                    "description": description
                }
                print(f"任务 {task_id} 执行失败: {e}")
        
        return results
    
    def _process_task(self, task: Dict[str, Any]) -> Any:
        """
        处理单个任务
        
        Args:
            task: 任务字典
            
        Returns:
            任务执行结果
        """
        # 支持多种参数命名方式
        tool_name = task.get("tool", task.get("工具名称"))
        params = task.get("params", task.get("tool_params", task.get("参数", {})))
        
        if tool_name and tool_name in self.tools:
            try:
                # 调用工具并传递参数
                result = self.use_tool(tool_name, **params)
                return result
            except Exception as e:
                # 捕获参数错误，返回友好的错误信息
                return f"工具调用失败: {str(e)}"
        else:
            # 直接执行（思考）
            prompt = task.get("description", task.get("描述", ""))
            return self.invoke_llm(prompt)
    
    def save_memory(self, filepath: str):
        """
        保存记忆到文件
        
        Args:
            filepath: 文件路径
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=2)
    
    def load_memory(self, filepath: str):
        """
        从文件加载记忆
        
        Args:
            filepath: 文件路径
        """
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                self.memory = json.load(f)