import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def process_nmr_data(file_path):
    """
    处理NMR原始数据
    - 将制表符分隔的数据读取为两列
    - 删除坐标为负数的行（删除开头的"-"数据）
    - 处理科学计数法格式的强度数据
    """
    
    # 读取CSV文件，使用制表符分隔
    df = pd.read_csv(file_path, sep='\t', header=None, names=['坐标', '强度值', '额外列'])
    
    # 删除可能的额外空列
    if '额外列' in df.columns:
        df = df.drop(['额外列'], axis=1)
    
    # 清理数据 - 去除空行
    df = df.dropna(subset=['坐标', '强度值'])
    
    # 转换坐标列为数值类型
    df['坐标'] = pd.to_numeric(df['坐标'], errors='coerce')
    df['强度值'] = pd.to_numeric(df['强度值'], errors='coerce')
    
    # 显示原始数据信息
    print("原始数据信息:")
    print(f"总行数: {len(df)}")
    print(f"坐标范围: {df['坐标'].min():.6f} 到 {df['坐标'].max():.6f}")
    print(f"负数坐标行数: {(df['坐标'] < 0).sum()}")
    print(f"正数坐标行数: {(df['坐标'] >= 0).sum()}")
    
    # 过滤掉坐标为负数的行（删除开头的"-"数据）
    filtered_data = df[df['坐标'] >= 0].copy()
    
    # 重置索引
    filtered_data = filtered_data.reset_index(drop=True)
    
    print(f"\n过滤后数据信息:")
    print(f"剩余行数: {len(filtered_data)}")
    print(f"坐标范围: {filtered_data['坐标'].min():.6f} 到 {filtered_data['坐标'].max():.6f}")
    print(f"强度范围: {filtered_data['强度值'].min():.2e} 到 {filtered_data['强度值'].max():.2e}")
    
    return filtered_data

def plot_nmr_spectrum(data, title="NMR Spectrum"):
    """
    绘制NMR谱图
    """
    plt.figure(figsize=(12, 6))
    plt.plot(data['坐标'], data['强度值'], linewidth=0.5)
    plt.xlabel('化学位移 (ppm)')
    plt.ylabel('强度')
    plt.title(title)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    return plt

def analyze_nmr_data(data):
    """
    分析NMR数据
    """
    print("数据分析:")
    print(f"数据点数: {len(data)}")
    print(f"坐标步长: {(data['坐标'].max() - data['坐标'].min()) / (len(data) - 1):.8f}")
    print(f"平均强度: {data['强度值'].mean():.2e}")
    print(f"强度标准差: {data['强度值'].std():.2e}")
    
    # 找到最大和最小强度对应的坐标
    max_intensity_coord = data.loc[data['强度值'].idxmax(), '坐标']
    min_intensity_coord = data.loc[data['强度值'].idxmin(), '坐标']
    
    print(f"最大强度位置: {max_intensity_coord:.6f} ppm")
    print(f"最小强度位置: {min_intensity_coord:.6f} ppm")

# 主处理函数
def main():
    # 处理数据
    processed_data = process_nmr_data('./data/Document3.csv')
    
    # 显示前几行数据
    print("\n处理后数据前10行:")
    print(processed_data.head(10))
    
    # 分析数据
    print("\n" + "="*50)
    analyze_nmr_data(processed_data)
    
    # 保存处理后的数据
    processed_data.to_csv('./data/processed_nmr_data.csv', index=False)
    print(f"\n数据已保存到 '/data/processed_nmr_data.csv'")
    
    # 绘制谱图（可选）
    try:
        plot_nmr_spectrum(processed_data, "处理后的NMR谱图")
        plt.savefig('./data/nmr_spectrum.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("谱图已保存到 '/data/nmr_spectrum.png'")
    except Exception as e:
        print(f"绘图时出现错误: {e}")
    
    return processed_data

# 使用示例
if __name__ == "__main__":
    # 运行主处理函数
    result = main()
    
    # 可以进一步处理结果
    print("\n处理完成!")
    print(f"最终数据形状: {result.shape}")