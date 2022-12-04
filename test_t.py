# 随便绘制一个饼图
import matplotlib.pyplot as plt

fig1 = plt.figure()  # 先创建一个图像对象
plt.pie([0.5, 0.3, 0.2],  # 值
        labels=['我', '你', '它'],  # 标签
        explode=(0, 0.2, 0),  # （爆裂）距离
        autopct='%1.1f%%',   # 显示百分数格式
        shadow=True)  # 是否显示阴影
plt.savefig(f'./FD/IMG/test.png')