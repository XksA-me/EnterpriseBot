# -*- coding: UTF-8 -*-
# 导入需要的模块
import pandas as pd
import dataframe_image as dfi
import matplotlib.pyplot as plt
import os


plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
import matplotlib
matplotlib.rcParams['font.sans-serif']=['SimHei']   # 用黑体显示中文
matplotlib.rcParams['axes.unicode_minus']=False     # 正常显示负号
 

# 获取指定基金 指定日期段 净值数据
def get_fund_data(fund, start_d, end_d):
    fund_df = pd.read_csv(f'./FD/DATA/{fund}_data.csv')
    result_df = fund_df.query(f"'{start_d}'<=净值日期<='{end_d}'")
    return result_df
    
# 将dtaframe表格转变成图片
def df_to_img(fund_df, fund, start_d, end_d, flag=1):
    if fund_df.shape[0] <=1:
        dfi.export(fund_df, f'./FD/IMG/{fund}_{start_d}_{end_d}_data.png')
        return 
    # print(fund_df)
    # 格式化表格 凸显最大最小值
    fund_df = fund_df.style.highlight_max(subset=['单位净值'], color='red')\
         .highlight_min(subset=['单位净值'], color='green')\
         .format({'日增长率': '{:}%', '单位净值': '{:.5}'})
    if flag==0:
        dfi.export(fund_df, f'./FD/IMG/{fund}_{start_d}_{end_d}_b.png')
    else:
        dfi.export(fund_df, f'./FD/IMG/{fund}_{start_d}_{end_d}_data.png')
    
    
# 绘制基金单位净值走势图
def draw_fund_line(fund_df, fund, start_d, end_d, flag=1):
    plt.rcParams['figure.figsize'] = (8.0, 4.0) # 设置figure_size尺寸
    plt.rcParams['savefig.dpi'] = 300 #保存图片分辨率
    plt.rcParams['figure.dpi'] = 300 #分辨率

    # 不显示右、上边框
    ax=plt.gca() 
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')

    # 设置坐标网格
    plt.grid(axis="y", color='gray')  

    # 计算最大值 最小值坐标 并标注到图中
    fund_max = fund_df.loc[fund_df['单位净值'].idxmax()]
    fund_min = fund_df.loc[fund_df['单位净值'].idxmin()]

    ax.annotate(f'({fund_max[0]},{fund_max[1]})', xy=(fund_max[0], fund_max[1]), color='red')
    ax.annotate(f'({fund_min[0]},{fund_min[1]})', xy=(fund_min[0], fund_min[1]), color='green')

    # 画图
    # 基金单位净值走势图
    # 净值日期
    # 单位净值
    plt.plot(fund_df['净值日期'],fund_df['单位净值'], color="c")
    plt.title('基金单位净值走势图')
    plt.xticks(rotation=30)
    plt.xlabel('净值日期')
    plt.ylabel('单位净值')
    if flag == 0:
        plt.savefig(f'./FD/IMG/{fund}_{start_d}_{end_d}_q.png')
    else:
        plt.savefig(f'./FD/IMG/{fund}_{start_d}_{end_d}_data.png')


# 返回数据
def response_data(fund, start_d, end_d, flag=1):
    if flag == 1:
        # 本地查看 查询结果是否已存在
        imgs = os.listdir('./FD/IMG/')
        if f'{fund}_{start_d}_{end_d}_data.png' in imgs:
            return f'{fund}_{start_d}_{end_d}_data.png'
        
        # 获取数据
        fund_df = get_fund_data(fund, start_d, end_d)
        
        # 如果数据量小于等于30条，就返回原始数据图
        if fund_df.shape[0]<= 30:
            df_to_img(fund_df, fund, start_d, end_d)
        else:
            # 否则返回数据趋势图
            fund_df = fund_df.sort_values(by=['净值日期'])
            draw_fund_line(fund_df, fund, start_d, end_d)
        return f'{fund}_{start_d}_{end_d}_data.png'
    else:
        # 获取数据
        fund_df = get_fund_data(fund, start_d, end_d)
        # 基金近10天数据表
        df_to_img(fund_df, fund, start_d, end_d, flag=0)
        # 基金近10天趋势图
        fund_df = fund_df.sort_values(by=['净值日期'])
        draw_fund_line(fund_df, fund, start_d, end_d, flag=0)
        return f'{fund}_{start_d}_{end_d}_b.png', f'{fund}_{start_d}_{end_d}_q.png'




