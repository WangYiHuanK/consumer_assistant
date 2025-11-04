import pandas as pd
import re

def clean_financial_data(df):
    """
    清洗财务数据的函数
    :param df: 从原始CSV文件读取的DataFrame
    :return: 清洗后的DataFrame
    """
    # 1. 列名标准化（不同平台的导出列名不同）
    df.columns = ['trade_time', 'type', 'amount', 'counterparty', 'category']
    
    # 2. 处理金额：去除货币符号，转换为浮点数
    df['amount'] = df['amount'].astype(str).str.replace('¥', '').str.replace(',', '').astype(float)
    
    # 3. 处理时间：转换为标准datetime对象
    df['trade_time'] = pd.to_datetime(df['trade_time'])
    
    # 4. 处理类型：统一收入/支出的标识（如“收入”、“支出”、“转账”）
    # 将类型映射为标准值：'income'（收入）, 'expense'（支出）, 'transfer'（转账忽略）
    type_mapping = {'收入': 'income', '支出': 'expense', '转账支出': 'expense', '转账收入': 'income'}
    df['type'] = df['type'].map(type_mapping)
    
    # 5. 处理商户名（对方户名）：去除空格等无关字符
    df['counterparty'] = df['counterparty'].astype(str).str.strip()
    
    # 6. 过滤无效数据：金额为0或空值的行
    df = df[(df['amount'] != 0) & (df['amount'].notna())]
    
    # 7. 重置索引
    df.reset_index(drop=True, inplace=True)
    
    return df

if __name__ == "__main__":
    # 读取原始CSV文件
    raw_df = pd.read_csv('your_raw_financial_data.csv')
    
    # 清洗数据
    cleaned_df = clean_financial_data(raw_df)
    
    # 查看清洗后的数据
    print(cleaned_df.head())
    print(cleaned_df.info())
