# -*- coding: UTF-8 -*-
'''
rt_data.py
Receiver Transmitter Data 数据接收和发送器
auth: 简说Python-老表
'''

from flask import Flask, request
import hmac
import hashlib
import base64
import json
import requests
from fund_operation import response_data
from datetime import timedelta, datetime

# static_folder需要完整路径
app = Flask(__name__, static_folder='./IMG', static_url_path='/img')


# 消息数字签名计算核对
def check_sig(timestamp):
    app_secret = '你的 app_secret'
    app_secret_enc = app_secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, app_secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(app_secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = base64.b64encode(hmac_code).decode('utf-8')
    return sign


# 发送markdown消息
def send_md_msg(userid, title, message, webhook_url):
    data = {
        "msgtype": "markdown",
        "markdown": {
            "title":title,
            "text": message
        },
        '''
        "msgtype": "text",
        "text": {
            "content": message
        },
        '''
        "at": {
            "atUserIds": [
              userid
          ],
        }
    }
    # 利用requests发送post请求
    req = requests.post(webhook_url, json=data)


# 处理自动回复消息
def handle_info(req_data):
    # 解析用户发送消息 通讯webhook_url 
    text_info = req_data['text']['content'].strip()
    webhook_url = req_data['sessionWebhook']
    senderid = 'zjh820553471'
    # print('***************text_info：', text_info)
    if text_info == '福利':
        title = "【简说Python】今日福利"
        text = """### 福利介绍
你好，我是老表，和我一起学习Python、云服务器开发知识啦！\n
>![](https://img-blog.csdnimg.cn/246a90c55c4e46dca089731c5fd00833.png)
**[老表的个人博客，已上线](https://python-brief.com/)**\n
            """
        # 调用函数，发送markdown消息
        send_md_msg(senderid, title, text, webhook_url)
    
    # 基金相关解析
    if text_info[0] == 'F':
        # F基金编码 开始日期 结束日期
        fund_d = text_info.split()
        print('fund_d', fund_d)
        if len(fund_d) == 3:
            fund, start_d, end_d = fund_d
            r_img = response_data(fund, start_d, end_d)
            title = f"{fund}基金数据"
            text = f"""### {fund}基金数据
>![](http://你的机器ip:8083/img/{r_img})
\n**[老表的个人博客，已上线](https://python-brief.com/)**\n
            """
        elif len(fund_d) == 1 and len(fund_d[0]) == 7:
            fund = fund_d[0]
            # 设置日期间隔 后移一天
            delta = timedelta(-1)
            # 后移11天
            start_d = datetime.strftime(datetime.now()+delta*11, '%Y-%m-%d')
            # 后移1天
            end_d = datetime.strftime(datetime.now()+delta, '%Y-%m-%d')
            b_img, q_img = response_data(fund, start_d, end_d, flag=0)
            title = f"{fund}基金数据"
            text = f"""### {fund}基金数据近10天数据
- 数据表
![](http://你的ip:8083/img/{b_img})
- 趋势图
![](http://你的ip:8083/img/{q_img})
\n**[老表的个人博客，已上线](https://python-brief.com/)**\n
            """
            # print(text)
        else:
            title = f"基金查询输入格式错误"
            text = """### 基金查询输入格式错误
>正确格式：
- F基金代码 开始日期 结束日期，如：F005827 2022-01-02 2022-02-10
- F基金代码
**[老表的个人博客，已上线](https://python-brief.com/)**\n
            """
        # 调用函数，发送markdown消息
        send_md_msg(senderid, title, text, webhook_url)
       

@app.route("/", methods=["POST"])
def get_data():
    # 第一步验证：是否是post请求
    if request.method == "POST":
        # print(request.headers)
        # 签名验证 获取headers中的Timestamp和Sign
        timestamp = request.headers.get('Timestamp')
        sign = request.headers.get('Sign')
        # 第二步验证：签名是否有效
        if check_sig(timestamp) == sign:
            # 获取、处理数据 
            req_data = json.loads(str(request.data, 'utf-8'))
            # print(req_data)
            handle_info(req_data)
            print('验证通过')
            return 'hhh'
            
        print('验证不通过')
        return 'ppp'
        
    print('有get请求')
    return 'sss'
    

if __name__ == '__main__':
    # 默认端口是：8083
    app.run(host='0.0.0.0', port=8083)
