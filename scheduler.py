# -*- coding: UTF-8 -*-
from apscheduler.schedulers.blocking import BlockingScheduler
import akshare as ak
import time 
import random
# 钉钉群机器人
from dingding_bot import warning_bot


'''
auth: 简说Python-老表
'''


# 定时任务：每天早上3点获取所有关注的基金历史数据，存储到本地
def get_all():
    try:
        # 从文件读取 自己关注的基金代码列表
        with open('./FD/funds.txt') as f:
            funds = [i.strip() for i in f.readlines()]
        # 遍历 一个个更新数据
        for fund in funds:
            fund_df = ak.fund_open_fund_info_em(fund, indicator='单位净值走势')
            fund_df = fund_df.sort_values(by=['净值日期'], ascending=False)
            fund_df.to_csv(f"./FD/DATA/F{fund}_data.csv", index=False)
            # print(f"./FD/DATA/F{fund}_data.csv")
            time.sleep(random.randint(1,5))
        return '【正常】基金数据更新完成'
    except Exception as e:
        r = f"【错误信息】{e}"
        return r

'''
每天早上3:00 更新基金数据
'''
def every_day_three():
    r = get_all()
    warning_bot(r, '基金数据更新')
    

# 选择BlockingScheduler调度器
sched = BlockingScheduler(timezone='Asia/Shanghai')

# every_day_three 每天早上3点运行一次
sched.add_job(every_day_three, 'cron', hour=3)

# 启动定时任务
sched.start()