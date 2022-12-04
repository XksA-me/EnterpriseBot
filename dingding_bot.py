# -*- coding: UTF-8 -*-
from time import time
import hmac
import hashlib
import base64
import urllib.parse
import requests


'''
钉钉机器人相关设置
auth: 简说Python-老表
'''



'''
钉钉机器人数字签名计算
'''
def get_digest():
    timestamp = str(round(time() * 1000))
    secret = '你的 secret'
    secret_enc = secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    # print(timestamp)
    # print(sign)
    return f"&timestamp={timestamp}&sign={sign}"


# 发送消息
def warning_bot(message, title):
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
        "atMobiles": [
            "15797265957" # 要@对象的手机号
        ],
        "isAtAll": True # 是否要@所有人
        }
    }
    # 机器人链接地址，发post请求 向钉钉机器人传递指令
    webhook_url = '你的 webhook_url'
    # 利用requests发送post请求
    req = requests.post(webhook_url+get_digest(), json=data)
    # print(req.status_code)
    return