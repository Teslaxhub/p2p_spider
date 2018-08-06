#!-*- coding:utf-8 -*-
"""
债转标自动投
拍拍贷债权自动投标需要代收余额达40万才可以
这里投资规则使用官方默认规则:
    即:先按折让比例从大到小，再按债转金额从小到大
"""
import re
import logging
import time
import random
import requests

TIMEOUT = 5
sleep_interval = random.randint(60, 60*10)

logging.basicConfig(
    filename='ppd.log',
    format='[%(levelname)s %(asctime)s] %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger(__name__)



ck = ""
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:35.0) Gecko/20100101 Firefox/35.0",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Content-Type": "application/json; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://invdebt.ppdai.com/buy/list?monthGroup=1%2C&rate=9&category=1&sortType=6&levels=%2C&currentLevels=%2CAA%2C&lastDueDays=&overDueDays=&isShowMore=&minAmount=&maxAmount=&minPastDueDay=&maxPastDueDay=&minPastDueNumber=&maxPastDueNumber=&minAllowanceRadio=&maxAllowanceRadio=&special=",
    "Content-Length": "290",
    "Cookie": ck,
    "Connection": "keep-alive",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
}
session = requests.session()
session.headers = headers


def check_login_status():
    """校验是否登陆成功"""
    url = 'https://status.ppdai.com/status?v=2014&tmp=0.0033873628051058757'
    headers = {
        "Cookie": ck
    }
    try:
        resp = requests.get(url, headers=headers, timeout=TIMEOUT)
        content = resp.content
        if re.search(r'user/logout', content):
            return True
        else:
            print "login failed"
    except requests.Timeout:
        return True
    except Exception as e:
        logger.error("check_login_status failed, err_msg=%s" % e)
    return False


def one_key_buy_list():
    """
    符合筛选条件的债权信息
    {
        "data":{
            "userId":6659862,
            "availableBalance":300206.59,
            "availableCount":4614,
            "sumAmount":1757.61,
            "queryId":"b704c9dd-db8f-4d2a-8c3d-289cb225fa59"
        },
        "Code":1,
        "Message":"成功"
    }
    """
    post_data = {
        "category": "1",
        "currentLevels": ",AA,",
        "lastDueDays": "",
        "levels": ",",
        "maxAllowanceRadio": "",
        "maxAmount": "",
        "maxPastDueDay": "",
        "maxPastDueNumber": "",
        "minAllowanceRadio": "",
        "minAmount": "",
        "minPastDueDay": "",
        "minPastDueNumber": "",
        "monthGroup": "1,",
        "overDueDays": "",
        "queryCount": 10,  # 查询
        "rate": "9"
    }
    url = 'https://invdebt.ppdai.com/buy/oneKeyBuyList'
    resp = session.post(url, json=post_data, timeout=TIMEOUT)
    return resp.json()


def bid_confirm(query_id):
    """
    根据过滤出的符合条件的标的，这里进行一键投标
    {"data":null,"Code":1,"Message":"成功"}
    """
    url = 'https://invdebt.ppdai.com/buy/oneKeyBuy'
    post_data = {
        "queryId": query_id
    }
    resp = session.post(url, json=post_data, timeout=TIMEOUT)
    return resp.json()


def one_key_bid():
    debt_list_info = one_key_buy_list()
    logger.info(debt_list_info.get('data'))
    if debt_list_info.get('Code') != 1:
        raise Exception(u"function=one_key_buy_list\terr_msg=%s" % debt_list_info.get("Message"))
    if debt_list_info.get('data', {}).get('availableBalance') < debt_list_info.get('data', {}).get("sumAmount"):
        logger.info('余额不足')
        return
    query_id = debt_list_info.get('data', {}).get('queryId')
    bid_info = bid_confirm(query_id)
    if bid_info.get('Code') != 1:
        raise Exception(u"function=one_key_bid\terr_msg=%s" % bid_info.get("Message"))


if __name__ == "__main__":
    while True:
        try:
            if not check_login_status():
                break
            one_key_bid()
        except Exception as e:
            logger.error(e)
        time.sleep(sleep_interval)
