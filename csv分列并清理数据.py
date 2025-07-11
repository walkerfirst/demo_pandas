'''
手动用pandas将csv的一列分成两列,并清理特殊符号后转换为数字'''

import pandas as pd
import re

# 读取CSV文件
df = pd.read_csv('./data/Document.csv')

# 处理第一列
first_col_name = df.columns[0]
df['前7位'] = df[first_col_name].astype(str).str[:7]
df['剩余部分'] = df[first_col_name].astype(str).str[7:]
df_filtered = df[df['剩余部分'].str.contains(r'\+', na=False)]

# 处理第二列 - 更精确的方法
second_col_name = df_filtered.columns[1]
col_name3 = df_filtered.columns[2]

def clean_scientific_notation(value):
    """清理科学计数法格式的数据"""
    # 转换为字符串并去除首尾空格
    clean_str = str(value).strip()
    
    # 使用正则表达式匹配科学计数法格式
    # 匹配类似 -3.50628e+07 的格式
    pattern = r'^-?(\d+\.?\d*e[+-]?\d+)$'
    match = re.match(pattern, clean_str, re.IGNORECASE)
    
    if match:
        # 去除负号
        result = clean_str.replace('-', '')
        return float(result)
    else:
        # 如果不匹配科学计数法格式，尝试直接转换
        try:
            return float(clean_str.replace('-', ''))
        except:
            return None

# 应用处理函数
df_filtered['ppm'] = df_filtered[second_col_name].apply(clean_scientific_notation)
df_filtered['value'] = df_filtered[col_name3].apply(clean_scientific_notation)

# 显示结果
print("处理结果:")
print(df_filtered[['ppm', 'value', '前7位']].head())

# 保存结果
df_filtered.to_csv('./data/processed_data2.csv', index=False)