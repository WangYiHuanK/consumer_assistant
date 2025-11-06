"""动态图表生成器模块 - 允许大模型根据分析需求动态生成图表"""
import os
import json
import sys
import io
import contextlib
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt
from typing import List, Dict, Any, Optional
from datetime import datetime
import numpy as np
import pandas as pd
from app.models.consumption import Consumption
import traceback
# 导入LLM相关库
try:
    from langchain.llms import OpenAI
    from langchain.chat_models import ChatOpenAI
    from langchain.schema import HumanMessage, SystemMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    print("警告: langchain库不可用，将使用备用方法生成图表代码")
    LANGCHAIN_AVAILABLE = False

# 配置matplotlib字体支持中文
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'PingFang SC', 'Hiragino Sans GB', 'SimHei', 'WenQuanYi Micro Hei']
plt.rcParams['axes.unicode_minus'] = False  # 正常显示负号
plt.rcParams['savefig.facecolor'] = 'white'  # 确保保存的图片背景是白色

class DynamicChartGenerator:
    """
    动态图表生成器类，允许执行大模型生成的Python代码来创建自定义图表
    """
    
    def __init__(self, output_dir: str):
        """
        初始化动态图表生成器
        
        Args:
            output_dir: 图表保存目录
        """
        self.output_dir = output_dir
        self._ensure_output_dir_exists()
        self.llm = self._init_llm() if LANGCHAIN_AVAILABLE else None
    
    def _ensure_output_dir_exists(self):
        """确保输出目录存在"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"创建图表输出目录: {self.output_dir}")
    
    def _prepare_safe_execution_environment(self, consumptions: List[Consumption]) -> Dict[str, Any]:
        """
        准备安全的执行环境，提供必要的工具和数据
        
        Args:
            consumptions: 消费记录列表
            
        Returns:
            安全的执行环境字典
        """
        # 将消费数据转换为pandas DataFrame便于操作
        data = []
        for consumption in consumptions:
            data.append({
                'id': consumption.id,
                'user_id': getattr(consumption, 'user_id', None),
                'amount': float(consumption.amount),
                'category': consumption.category or '未分类',
                'description': getattr(consumption, 'description', '') or '',
                'transaction_time': consumption.transaction_time,
                'transaction_type': consumption.transaction_type or '支出',
                'payment_method': getattr(consumption, 'payment_method', '') or '其他',
                'merchant_name': consumption.merchant_name or '未知'
            })
        
        df = pd.DataFrame(data)
        df['transaction_date'] = pd.to_datetime(df['transaction_time']).dt.date
        df['transaction_month'] = pd.to_datetime(df['transaction_time']).dt.to_period('M')
        
        # 安全的执行环境，只提供必要的库和数据
        safe_env = {
            'os': os,
            'plt': plt,
            'np': np,
            'pd': pd,
            'datetime': datetime,
            'consumptions': consumptions,
            'df': df,
            'output_dir': self.output_dir,
            'chart_filename': '',  # 将由生成的代码设置
            'plt.figure': plt.figure,
            'plt.savefig': plt.savefig,
            'plt.close': plt.close,
            'plt.tight_layout': plt.tight_layout,
            '__builtins__': {
                'abs': abs,
                'all': all,
                'any': any,
                '__import__': __import__,  # 添加__import__函数以支持图表代码执行
                'bool': bool,
                'dict': dict,
                'float': float,
                'int': int,
                'len': len,
                'list': list,
                'max': max,
                'min': min,
                'range': range,
                'round': round,
                'sorted': sorted,
                'str': str,
                'sum': sum,
                'tuple': tuple,
                'zip': zip,
                'print': print,
                'Exception': Exception,
                'ValueError': ValueError,
                'KeyError': KeyError,
                'TypeError': TypeError,
            }
        }
        
        return safe_env
    
    def _extract_chart_filename(self, code: str) -> str:
        """
        从代码中提取图表文件名，如果没有则生成默认名称
        
        Args:
            code: Python代码字符串
            
        Returns:
            图表文件名
        """
        import re
        # 尝试从代码中提取文件名设置
        match = re.search(r'chart_filename\s*=\s*[\'"]([^\'"]*)[\'"]', code)
        if match:
            return match.group(1)
        
        # 生成默认文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"dynamic_chart_{timestamp}.png"
    
    def execute_chart_code(self, code: str, consumptions: List[Consumption]) -> str:
        """
        安全执行大模型生成的图表代码
        
        Args:
            code: Python代码字符串
            consumptions: 消费记录列表
            
        Returns:
            生成的图表文件路径
        """
        # 准备安全的执行环境
        env = self._prepare_safe_execution_environment(consumptions)
        
        # 提取或生成图表文件名
        chart_filename = self._extract_chart_filename(code)
        env['chart_filename'] = chart_filename
        chart_path = os.path.join(self.output_dir, chart_filename)
        
        # 执行代码，捕获输出和错误
        stdout = io.StringIO()
        stderr = io.StringIO()
        error_occurred = False
        
        try:
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                # 安全执行代码
                exec(code, env)
                
                # 如果代码没有保存图表，则自动保存
                if not os.path.exists(chart_path):
                    plt.savefig(chart_path)
                    print(f"自动保存图表到: {chart_path}")
        except Exception as e:
            error_occurred = True
            print(f"执行图表代码时出错: {str(e)}")
            print(traceback.format_exc())
        finally:
            # 确保关闭图表
            plt.close('all')
        
        # 获取执行输出
        stdout_content = stdout.getvalue()
        stderr_content = stderr.getvalue()
        
        if stdout_content:
            print(f"图表代码执行输出: {stdout_content}")
        if stderr_content:
            print(f"图表代码执行错误: {stderr_content}")
        
        # 检查图表是否成功生成
        if error_occurred or not os.path.exists(chart_path):
            # 生成一个错误提示图表
            plt.figure(figsize=(10, 6))
            plt.text(0.5, 0.5, f"图表生成失败\n错误: {str(e)[:100]}..." if error_occurred else "图表未生成", 
                    ha='center', va='center', fontsize=12, color='red')
            plt.axis('off')
            plt.savefig(chart_path)
            plt.close()
            print(f"已生成错误提示图表: {chart_path}")
        
        return chart_path
    
    def _init_llm(self):
        """
        初始化语言模型
        
        Returns:
            语言模型实例
        """
        try:
            # 尝试使用ChatOpenAI
            return ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.3)
        except Exception as e:
            print(f"初始化ChatOpenAI失败，尝试使用OpenAI: {str(e)}")
            try:
                # 回退到OpenAI
                return OpenAI(model_name="text-davinci-003", temperature=0.3)
            except Exception as e2:
                print(f"初始化OpenAI失败: {str(e2)}")
                return None
    
    def _generate_chart_code_with_llm(self, analysis_needs: str, sample_data: List[Dict[str, Any]]) -> str:
        """
        使用LLM生成图表代码
        
        Args:
            analysis_needs: 用户的分析需求
            sample_data: 示例数据
            
        Returns:
            生成的Python代码
        """
        prompt = self.generate_chart_code_prompt(analysis_needs, sample_data)
        
        try:
            # 根据LLM类型生成响应
            if hasattr(self.llm, 'model_name') and self.llm.model_name.startswith('gpt-'):
                # ChatOpenAI
                messages = [
                    SystemMessage(content="你是一位专业的数据可视化专家，擅长创建清晰、美观且信息丰富的图表。"),
                    HumanMessage(content=prompt)
                ]
                response = self.llm(messages)
                code = response.content
            else:
                # 传统OpenAI模型
                code = self.llm(prompt)
            
            # 清理代码（去除可能的代码块标记）
            import re
            code = re.sub(r'^```python\n|```$', '', code, flags=re.MULTILINE)
            return code
        except Exception as e:
            print(f"使用LLM生成图表代码失败: {str(e)}")
            # 返回默认图表代码
            return self._get_default_chart_code(analysis_needs)
    
    def _get_default_chart_code(self, analysis_needs: str) -> str:
        """
        获取默认图表代码
        
        Args:
            analysis_needs: 用户的分析需求
            
        Returns:
            默认的Python代码
        """
        chart_type = "category" if "类别" in analysis_needs or "分类" in analysis_needs else "trend"
        
        if chart_type == "category":
            return """
# 创建消费类别分布图
plt.figure(figsize=(12, 8))
category_counts = df['category'].value_counts()
category_amounts = df.groupby('category')['amount'].sum().sort_values(ascending=False)

# 创建饼图
plt.pie(category_amounts, labels=category_amounts.index, autopct='%1.1f%%', startangle=90)
plt.title('消费类别分布')
plt.axis('equal')  # 确保饼图是圆形的

# 设置文件名
chart_filename = f"chart_category_distribution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

# 保存图表
plt.tight_layout()
plt.savefig(os.path.join(output_dir, chart_filename))
plt.close()
            """
        else:
            return """
# 创建消费趋势图
plt.figure(figsize=(12, 6))

# 按日期分组并计算每日总消费
daily_spending = df.groupby('transaction_date')['amount'].sum().reset_index()

# 绘制趋势线
plt.plot(daily_spending['transaction_date'], daily_spending['amount'], marker='o', linestyle='-', color='#1f77b4')
plt.title('消费趋势分析')
plt.xlabel('日期')
plt.ylabel('消费金额')
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)

# 设置文件名
chart_filename = f"chart_spending_trend_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

# 保存图表
plt.tight_layout()
plt.savefig(os.path.join(output_dir, chart_filename))
plt.close()
            """
    
    def generate_charts_by_needs(self, consumptions: List[Consumption], analysis_needs: str) -> Dict[str, str]:
        """
        根据用户的分析需求动态生成图表
        
        Args:
            consumptions: 消费记录列表
            analysis_needs: 用户的分析需求
            
        Returns:
            图表路径字典
        """
        print(f"根据分析需求生成图表: {analysis_needs}")
        
        # 如果没有数据，创建空图表
        if not consumptions:
            print("警告：没有消费数据，创建空数据集默认图表")
            return self._create_empty_data_chart()
        
        # 准备示例数据（用于提示词）
        sample_data = []
        for consumption in consumptions[:3]:  # 只取前3条作为示例
            sample_data.append({
                'amount': consumption.amount,
                'category': consumption.category,
                'transaction_time': consumption.transaction_time.isoformat() if consumption.transaction_time else '',
                'merchant_name': consumption.merchant_name
            })
        
        # 生成图表代码
        if LANGCHAIN_AVAILABLE and self.llm:
            chart_code = self._generate_chart_code_with_llm(analysis_needs, sample_data)
        else:
            # 使用备用方法
            chart_code = self._get_default_chart_code(analysis_needs)
        
        print(f"生成的图表代码:\n{chart_code}")
        
        # 执行图表代码
        chart_path = self.execute_chart_code(chart_code, consumptions)
        
        # 返回图表路径字典
        return {'main_chart': chart_path}
    
    def _create_empty_data_chart(self) -> Dict[str, str]:
        """
        创建空数据图表
        
        Returns:
            图表路径字典
        """
        plt.figure(figsize=(10, 6))
        plt.text(0.5, 0.5, '没有可用的消费数据', ha='center', va='center', fontsize=14, color='#666666')
        plt.title('无数据可视化', fontsize=16)
        plt.axis('off')
        
        # 保存图表
        chart_filename = f"chart_no_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        chart_path = os.path.join(self.output_dir, chart_filename)
        plt.savefig(chart_path)
        plt.close()
        
        return {'empty_data_chart': chart_path}
    
    def generate_chart_code_prompt(self, analysis_needs: str, sample_data: List[Dict[str, Any]]) -> str:
        """
        生成用于让大模型创建图表代码的提示词
        
        Args:
            analysis_needs: 用户的分析需求
            sample_data: 示例数据（用于让模型了解数据结构）
            
        Returns:
            提示词字符串
        """
        return f"""
作为Python数据可视化专家，请根据用户的分析需求，生成用于创建相关图表的Python代码。

用户分析需求: {analysis_needs}

可用的数据结构:
- df: pandas DataFrame，包含消费记录数据
- consumptions: 原始消费记录对象列表

数据字段说明:
- df包含以下列: id, user_id, amount(金额), category(类别), description(描述), transaction_time(交易时间), 
  'transaction_type(交易类型: 收入/支出), payment_method(支付方式), merchant_name(商家), transaction_date(交易日期), transaction_month(交易月份)

代码要求:
1. 只生成完整的Python代码，不要添加其他解释
2. 确保代码能够安全执行，不要引入外部依赖
3. 创建与用户分析需求直接相关的可视化图表
4. 设置有意义的标题、标签和图例
5. 使用美观的配色方案
6. 指定图表文件名，格式为: chart_<图表类型>_<时间戳>.png
7. 必须保存图表到环境变量中的output_dir目录
8. 代码示例结构:
```python
# 创建图表
plt.figure(figsize=(10, 6))
# 绘制图表的代码...
plt.title('有意义的标题')
plt.xlabel('X轴标签')
plt.ylabel('Y轴标签')
plt.legend()

# 设置文件名
chart_filename = f"chart_<图表类型>_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

# 保存图表
plt.tight_layout()
plt.savefig(os.path.join(output_dir, chart_filename))
plt.close()
```

请生成与用户需求{analysis_needs}最相关的图表代码。
"""


# 创建全局动态图表生成器实例函数
def get_dynamic_chart_generator(workspace_dir: str) -> DynamicChartGenerator:
    """
    获取动态图表生成器实例
    
    Args:
        workspace_dir: 工作空间目录
    
    Returns:
        动态图表生成器实例
    """
    charts_dir = os.path.join(workspace_dir, 'charts')
    return DynamicChartGenerator(charts_dir)