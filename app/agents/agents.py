from langchain_ollama import OllamaLLM
import os
from app.settings.config import config

# 初始化本地部署的大模型（使用Ollama部署的qwen2.5:7b）
llm = OllamaLLM(
    model=config.LLM_MODEL,  # 从配置中获取模型名称
    base_url=config.LLM_BASE_URL,  # 从配置中获取API地址
    temperature=config.LLM_TEMPERATURE  # 从配置中获取温度参数
)

# 分类提示词模板
classification_prompt = """
请将以下商户名分类到给定的类别中，直接返回类别名称，不要添加任何其他解释或内容。

可用类别：{categories}
商户名：{counterparty}
"""

# 示例分类列表（根据实际业务需求调整）
CATEGORIES = ["餐饮美食", "购物零售", "交通出行", "娱乐休闲", "医疗健康", "教育培训", "生活服务", "其他"]

def classify_transaction(counterparty_name, categories_list):
    """
    使用大模型对单条交易记录进行分类
    :param counterparty_name: 商户名
    :param categories_list: 分类列表
    :return: 分类字符串
    """
    # 1. 格式化提示词
    prompt = classification_prompt.format(
        categories=", ".join(categories_list),
        counterparty=counterparty_name
    )
    
    # 2. 调用大模型 - OllamaLLM直接返回字符串
    response = llm.invoke(prompt)
    
    # 3. 处理响应，确保返回结果在预定义的分类中
    # 由于OllamaLLM直接返回字符串，不需要访问.content属性
    predicted_category = response.strip()
    
    # 4. 做一个简单的后处理：如果模型返回了不在列表中的分类，则归为"其他"
    if predicted_category not in categories_list:
        predicted_category = "其他"
        
    return predicted_category

# 测试单条分类
# result = classify_transaction("苹果官方商店", CATEGORIES)
# print(result) # 应该输出：购物零售