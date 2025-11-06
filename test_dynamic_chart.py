#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试动态图表生成器
"""
import os
import sys
from datetime import datetime, timedelta
from app.models.consumption import Consumption
from app.utils.dynamic_chart_generator import get_dynamic_chart_generator

def create_sample_consumptions():
    """创建示例消费数据"""
    sample_data = [
        {"category": "餐饮", "amount": 150.5, "transaction_time": datetime.now() - timedelta(days=1), "merchant": "海底捞"},
        {"category": "购物", "amount": 599.0, "transaction_time": datetime.now() - timedelta(days=2), "merchant": "京东"},
        {"category": "交通", "amount": 50.0, "transaction_time": datetime.now() - timedelta(days=3), "merchant": "地铁"},
        {"category": "餐饮", "amount": 88.8, "transaction_time": datetime.now() - timedelta(days=4), "merchant": "星巴克"},
        {"category": "娱乐", "amount": 200.0, "transaction_time": datetime.now() - timedelta(days=5), "merchant": "电影院"},
        {"category": "购物", "amount": 1299.0, "transaction_time": datetime.now() - timedelta(days=6), "merchant": "淘宝"},
        {"category": "餐饮", "amount": 66.6, "transaction_time": datetime.now() - timedelta(days=7), "merchant": "麦当劳"},
    ]
    
    consumptions = []
    for i, data in enumerate(sample_data):
        # 创建一个简单的消费数据对象，只包含必要的字段
        consumption = type('Consumption', (), {
            'id': i+1,
            'user_id': 1,
            'amount': data["amount"],
            'category': data["category"],
            'transaction_time': data["transaction_time"],
            'transaction_type': "支出",
            'merchant_name': data["merchant"]
        })()
        consumptions.append(consumption)
    
    return consumptions

def main():
    """主函数"""
    print("===== 测试动态图表生成器 =====")
    
    # 获取工作目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.join(current_dir, "workspace")
    
    # 初始化动态图表生成器
    dynamic_chart_generator = get_dynamic_chart_generator(workspace_dir)
    
    # 创建示例数据
    consumptions = create_sample_consumptions()
    print(f"创建了 {len(consumptions)} 条示例消费数据")
    
    # 测试不同的分析需求
    test_needs = [
        "分析餐饮消费的分布情况",
        "分析最近一周的消费趋势",
        "比较不同类别的消费金额"
    ]
    
    for i, need in enumerate(test_needs):
        print(f"\n=== 测试 {i+1}: {need} ===")
        try:
            # 生成图表
            chart_paths = dynamic_chart_generator.generate_charts_by_needs(consumptions, need)
            print(f"生成的图表路径: {chart_paths}")
            
            # 检查图表文件是否存在
            for chart_name, chart_path in chart_paths.items():
                if os.path.exists(chart_path):
                    print(f"✓ 图表 {chart_name} 已成功生成: {os.path.basename(chart_path)}")
                else:
                    print(f"✗ 图表 {chart_name} 生成失败: {chart_path}")
        except Exception as e:
            print(f"生成图表时出错: {str(e)}")
    
    print("\n===== 测试完成 =====")

if __name__ == "__main__":
    main()