#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File: lenovo_sing.py(联想商城签到)
Author: marigold233,AlanZhao
Date: 2023/5/27 11:05
cron: 39 43 16 * * *
new Env('联想商城签到');
"""

import base64
import logging
import os
import random
import re
import sys
from sys import exit

import requests
import toml
from requests.utils import cookiejar_from_dict, dict_from_cookiejar

USER_AGENT = [
    "Mozilla/5.0 (Linux; U; Android 13; zh-CN; RMX3700 Build/SKQ1.221119.001) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/100.0.4896.58 Quark/6.3.6.322 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.37(0x1800252e) NetType/WIFI Language/zh_CN"
]


# 加载通知服务
def load_send():
    cur_path = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(cur_path)
    if os.path.exists(cur_path + "/sendNotify.py"):
        try:
            from sendNotify import send
            return send
        except Exception as e:
            print(f"加载通知服务失败：{e}")
            return None
    else:
        print("加载通知服务失败")
        return None

def login(username, password):
    def get_cookie():
        session.headers = {
            "user-agent": ua,
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        }
        session.get(url="https://reg.lenovo.com.cn/auth/rebuildleid")
        session.get(
            url="https://reg.lenovo.com.cn/auth/v1/login?ticket=5e9b6d3d-4500-47fc-b32b-f2b4a1230fd3&ru=https%3A%2F%2Fmclub.lenovo.com.cn%2F"
        )
        # data = f"account={username}&password={base64.b64encode(str(password).encode()).decode()}\
        #     &ps=1&ticket=e40e7004-4c8a-4963-8564-31271a8337d8&codeid=&code=&slide=v2&applicationPlatform=2&shopId=\
        #         1&os=web&deviceId=BxnNiVCexepYh4FaJo6chcLkHIQIJw7zoOJCvzhQKPmJFaxzzJymRE3qKHa8c2GK0amhOqgpDQK7Us0d3vCAzcg==&t=1686133421129&websiteCode=10000001&websiteName=%25E5%2595%2586%25E5%259F%258E%25E\
        #                 7%25AB%2599&forwardPageUrl=https%253A%252F%252Fmclub.lenovo.com.cn%252F"
        data = f"account={username}&password={base64.b64encode(str(password).encode()).decode()}\
                    &ps=1&ticket=5e9b6d3d-4500-47fc-b32b-f2b4a1230fd3&codeid=&code=&slide=v2&applicationPlatform=2&shopId=\
                        1&os=web&deviceId=BIT%2F8ZTwWmvKpMsz3bQspIZRY9o9hK1Ce3zKIt5js7WSUgGQNnwvYmjcRjVHvJbQ00fe3T2wxgjZAVSd\
                            OYl8rrQ%3D%3D&t=1655187183738&websiteCode=10000001&websiteName=%25E5%2595%2586%25E5%259F%258E%25E\
                                7%25AB%2599&forwardPageUrl=https%253A%252F%252Fmclub.lenovo.com.cn%252F"
        login_response = session.post(
            url="https://reg.lenovo.com.cn/auth/v2/doLogin", data=data
        )
        if login_response.json().get("ret") == "1":
            logger(f"{username}账号或密码错误")
            return None
        ck_dict = dict_from_cookiejar(session.cookies)
        config["cookies"][username] = f"{ck_dict}"
        toml.dump(config, open(config_file, "w"))
        session.cookies = cookiejar_from_dict(ck_dict)
        return session

    session = requests.Session()
    session.headers = {
        "user-agent": ua,
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }
    if cookie_dict := config.get("cookies").get(username):
        session.cookies = cookiejar_from_dict(eval(cookie_dict))
        ledou = session.post(
            "https://i.lenovo.com.cn/info/uledou.jhtml",
            data={"sts": "b044d754-bda2-4f56-9fea-dcf3aecfe782"},
        )
        try:
            int(ledou.text)
        except ValueError:
            logger(f"{username} ck有错，重新获取ck并保存")
            session = get_cookie()
            return session
        logger(f"{username} ck没有错")
        return session
    else:
        logger(f"{username} ck为空，重新获取ck并保存")
        session = get_cookie()
        return session


def sign(session):
    res = session.get(url="https://mclub.lenovo.com.cn/signlist/")
    token = re.findall('token\s=\s"(.*?)"', res.text)[0]
    data = f"_token={token}&memberSource=1"
    headers = {
        "Host": "mclub.lenovo.com.cn",
        "pragma": "no-cache",
        "cache-control": "no-cache",
        "accept": "application/json, text/javascript, */*; q=0.01",
        "origin": "https://mclub.lenovo.com.cn",
        "x-requested-with": "XMLHttpRequest",
        "user-agent": ua
        + "/lenovoofficialapp/16554342219868859_10128085590/newversion/versioncode-1000080/",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "referer": "https://mclub.lenovo.com.cn/signlist?pmf_group=in-push&pmf_medium=app&pmf_source=Z00025783T000",
        "accept-language": "zh-CN,en-US;q=0.8",
    }
    sign_response = session.post(
        "https://mclub.lenovo.com.cn/signadd", data=data, headers=headers
    )
    sign_days = (
        session.get(url="https://mclub.lenovo.com.cn/getsignincal")
        .json()
        .get("signinCal")
        .get("continueCount")
    )
    sign_user_info = session.get("https://mclub.lenovo.com.cn/signuserinfo")
    try: 
        serviceAmount = sign_user_info.json().get("serviceAmount")
        ledou = sign_user_info.json().get("ledou")
    except Exception as e:
        logger(sign_user_info.headers["content-type"])
        logger(sign_user_info.status_code)
        logger(e)
        serviceAmount, ledou = None, None
    session.close()
    if sign_response.json().get("success"):
        return f"\U00002705账号{username}签到成功, \U0001F4C6连续签到{sign_days}天, \U0001F954共有乐豆{ledou}个, \U0001F4C5共有延保{serviceAmount}天\n"
    else:
        return f"\U0001F6AB账号{username}今天已经签到, \U0001F4C6连续签到{sign_days}天, \U0001F954共有乐豆{ledou}个, \U0001F4C5共有延保{serviceAmount}天\n"


def main():
    global logger, config_file, config, ua, username
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s: %(message)s"
    )
    logger = logging.getLogger(__name__).info
    config_file = r"config.toml"
    config = toml.load(config_file)
    account = config.get("account")
    if not account:
        exit(1)
    if not (ua := config.get("browser").get("ua")):
        ua = random.choice(USER_AGENT)
        config["browser"]["ua"] = ua
    send_notify = load_send()
    title = "联想签到: \n"
    contents = ""
    for username, password in account.items():
        session = login(username, password)
        if not session:
            continue
        contents += sign(session)
    send_notify(title, contents)


if __name__ == "__main__":
    main()
