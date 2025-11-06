"""图表生成工具模块 - 用于生成消费数据的可视化图表"""
import os
import json
from typing import List, Dict, Any
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端

# 更可靠的字体配置方法，尝试多种中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'PingFang SC', 'Hiragino Sans GB', 'SimHei', 'WenQuanYi Micro Hei']
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
plt.rcParams['savefig.facecolor'] = 'white'  # 确保保存的图片背景是白色

from app.models.consumption import Consumption


class ChartGenerator:
    """
    图表生成器类，提供生成各类消费数据可视化图表的功能
    """
    
    def __init__(self, output_dir: str):
        """
        初始化图表生成器
        
        Args:
            output_dir: 图表保存目录
        """
        self.output_dir = output_dir
        self._ensure_output_dir_exists()
    
    def _ensure_output_dir_exists(self):
        """
        确保输出目录存在
        """
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"创建图表输出目录: {self.output_dir}")
    
    def generate_category_chart(self, consumptions: List[Consumption]) -> str:
        """
        生成消费类别分布图
        
        Args:
            consumptions: 消费记录列表
        
        Returns:
            生成的图表文件路径
        """
        # 统计各类别消费金额
        category_amounts = {}
        for consumption in consumptions:
            category = consumption.category or '未分类'
            if category not in category_amounts:
                category_amounts[category] = 0
            category_amounts[category] += float(consumption.amount)
        
        # 创建饼图
        plt.figure(figsize=(10, 6))
        plt.pie(
            category_amounts.values(),
            labels=category_amounts.keys(),
            autopct='%1.1f%%',
            startangle=90,
            shadow=True
        )
        plt.axis('equal')
        plt.title('消费类别分布', fontsize=14, fontweight='bold')
        
        # 保存图表
        chart_path = os.path.join(self.output_dir, f'category_chart_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
        plt.tight_layout()
        plt.savefig(chart_path)
        plt.close()
        
        print(f"消费类别分布图已生成: {chart_path}")
        return chart_path
    
    def generate_time_series_chart(self, consumptions: List[Consumption]) -> str:
        """
        生成消费趋势时间序列图
        
        Args:
            consumptions: 消费记录列表
        
        Returns:
            生成的图表文件路径
        """
        # 按日期分组统计消费金额
        daily_amounts = {}
        for consumption in consumptions:
            date_str = consumption.transaction_time.strftime('%Y-%m-%d')
            if date_str not in daily_amounts:
                daily_amounts[date_str] = 0
            daily_amounts[date_str] += float(consumption.amount)
        
        # 按日期排序
        sorted_dates = sorted(daily_amounts.keys())
        sorted_amounts = [daily_amounts[date] for date in sorted_dates]
        
        # 创建折线图
        plt.figure(figsize=(12, 6))
        plt.plot(sorted_dates, sorted_amounts, marker='o', linestyle='-', color='#3498db')
        plt.title('每日消费趋势', fontsize=14, fontweight='bold')
        plt.xlabel('日期', fontsize=12)
        plt.ylabel('消费金额(元)', fontsize=12)
        plt.xticks(rotation=45)
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # 保存图表
        chart_path = os.path.join(self.output_dir, f'time_series_chart_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
        plt.tight_layout()
        plt.savefig(chart_path)
        plt.close()
        
        print(f"消费趋势图已生成: {chart_path}")
        return chart_path
    
    def generate_income_expense_chart(self, consumptions: List[Consumption]) -> str:
        """
        生成收入支出对比图
        
        Args:
            consumptions: 消费记录列表
        
        Returns:
            生成的图表文件路径
        """
        # 统计收入和支出总额
        total_income = 0
        total_expense = 0
        
        for consumption in consumptions:
            amount = float(consumption.amount)
            if consumption.transaction_type == '收入':
                total_income += amount
            else:
                total_expense += amount
        
        # 创建柱状图，使用稍大的图表尺寸
        plt.figure(figsize=(10, 7))
        
        # 设置子图边距，避免标签被截断
        plt.subplots_adjust(bottom=0.15, top=0.9, left=0.1, right=0.9)
        
        plt.bar(['收入', '支出'], [total_income, total_expense], color=['#2ecc71', '#e74c3c'])
        plt.title('收支总览', fontsize=14, fontweight='bold')
        plt.ylabel('金额(元)', fontsize=12)
        
        # 在柱状图上显示具体数值，并调整位置避免超出图表范围
        max_value = max(total_income, total_expense)
        for i, v in enumerate([total_income, total_expense]):
            # 根据最大值动态调整文本位置，避免超出图表范围
            text_offset = max_value * 0.02  # 使用百分比而不是固定值
            plt.text(i, v + text_offset, f'{v:.2f}', ha='center')
        
        # 保存图表，不使用tight_layout，而是使用自定义的subplots_adjust
        chart_path = os.path.join(self.output_dir, f'income_expense_chart_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
        plt.savefig(chart_path)
        plt.close()
        
        print(f"收支总览图已生成: {chart_path}")
        return chart_path
    
    def generate_all_charts(self, consumptions: List[Consumption]) -> List[str]:
        """
        生成所有类型的图表
        
        Args:
            consumptions: 消费记录列表
        
        Returns:
            生成的图表文件路径列表
        """
        chart_paths = []
        
        # 生成各类图表
        chart_paths.append(self.generate_category_chart(consumptions))
        chart_paths.append(self.generate_time_series_chart(consumptions))
        chart_paths.append(self.generate_income_expense_chart(consumptions))
        
        return chart_paths


# 创建全局图表生成器实例函数
def get_chart_generator(workspace_dir: str) -> ChartGenerator:
    """
    获取图表生成器实例
    
    Args:
        workspace_dir: 工作空间目录
    
    Returns:
        图表生成器实例
    """
    # 在工作空间中创建一个专门用于保存图表的目录
    charts_dir = os.path.join(workspace_dir, 'charts')
    return ChartGenerator(charts_dir)