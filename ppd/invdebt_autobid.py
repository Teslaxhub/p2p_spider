#!-*- coding:utf-8 -*-
"""
债转标自动投
拍拍贷债权自动投标需要代收余额达40万才可以
这里投资规则使用官方默认规则:
    即:先按折让比例从大到小，再按债转金额从小到大
"""
import re
import time
import random
import logging
import requests
from bs4 import BeautifulSoup

TIMEOUT = 5
sleep_interval = random.randint(60, 60*10)

logging.basicConfig(
    filename='ppd.log',
    format='[%(levelname)s %(asctime)s] %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger(__name__)



ck = "regSourceId=0; referID=0; fromUrl=; referDate=2018-8-2%208%3A18%3A18; currentUrl=https%3A%2F%2Finvdebt.ppdai.com%2Fbuy%2Flist%3Fmonthgroup%3D1%252c%26rate%3D9%26category%3D1%26sorttype%3D6%26levels%3D%252c%26currentlevels%3D%252caa%252c%26lastduedays%3D%26overduedays%3D%26isshowmore%3D%26minamount%3D%26maxamount%3D%26minpastdueday%3D%26maxpastdueday%3D%26minpastduenumber%3D%26maxpastduenumber%3D%26minallowanceradio%3D%26maxallowanceradio%3D%26special%3D; uniqueid=f943569b-1882-401b-acd5-de2be914e820; noticeflag=true; __fp=fp; __vid=2054332811.1533169099792; __vsr=1533169099792.src%3Ddirect%7Cmd%3Ddirect%7Ccn%3Ddirect; gr_user_id=6b65af5c-f73c-4628-9ce5-cc4a1410ab42; Hm_lvt_f87746aec9be6bea7b822885a351b00f=1533169104,1533169127,1533208780; openid=03d61dd09a46ce9cd3db29f2d6692ff3; ppd_uname=pdu45415304; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22164f816880e34f-0ea0176b6ab70f-46544136-2073600-164f816880f8bf%22%2C%22%24device_id%22%3A%22164f816880e34f-0ea0176b6ab70f-46544136-2073600-164f816880f8bf%22%7D; sajssdk_2015_cross_new_user=1; aliyungf_tc=AQAAANdyjCbvRAAAIH3Gi6DmHuq38DLg; gr_session_id_b9598a05ad0393b9=8aab74e1-90ed-4c91-9242-0eb29eca8e00; gr_session_id_b9598a05ad0393b9_8aab74e1-90ed-4c91-9242-0eb29eca8e00=true; __tsid=119078225; __sid=1533208776060.3.1533209203567; Hm_lpvt_f87746aec9be6bea7b822885a351b00f=1533209204; token=758987375943ffa7e0aa6b7cf4033b51a001267c9c56302ec6b33d4f3f853e05481e45769f7c; __eui=yVp0QfEX5Bg%3D"
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
    if debt_list_info.get('data', {}).get("sumAmount") == 0:
        return
    if debt_list_info.get('data', {}).get('availableBalance') < debt_list_info.get('data', {}).get("sumAmount"):
        logger.info('余额不足')
        return
    query_id = debt_list_info.get('data', {}).get('queryId')
    bid_info = bid_confirm(query_id)
    if bid_info.get('Code') != 1:
        raise Exception(u"function=one_key_bid\terr_msg=%s" % bid_info.get("Message"))

def buy_debt():
    """筛选债权列表后进行购买，目前只支持单页"""
    DEFAULT_MAX_MONTH = 4
    url= 'https://invdebt.ppdai.com/buy/list'
    payload = {
        "category": 1,
        "currentLevels": ",AA,",
        "isShowMore": "",
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
        "monthGroup": "1,2,",
        "overDueDays": "",
        "rate": 9.5,
        "sortType": 6,
        "special": "",
    }
    resp = session.get(url, payload, headers=headers)
    soup = BeautifulSoup(resp.content, 'lxml')
    wap_borrow_debt = soup.find('ol', class_='clearfix')
    # 单条债权转让信息
    debt_info_str = wap_borrow_debt.find('li', class_='clearfix')
    debt_credit_info = debt_info_str.find('div', class_=re.compile('creditRating creditCode'))
    currentrate = debt_credit_info.get('currentrate')   # 当前利率
    debtdealid = debt_credit_info.get('debtdealid') # 交易id
    creditcode = debt_credit_info.get('creditcode') # 原始等级

    remain_time = debt_info_str.find('div', class_=re.compile('remaintime')).text
    match = re.search(r'(?P<remain_time>\d{1,2})\/\d{1,2}', remain_time)
    remain_month = int(match.group('remain_time'))
    if remain_month <= DEFAULT_MAX_MONTH:
        buy_debt_url = 'https://invdebt.ppdai.com/buy/buyDebt'
        post_data = {
            "debtDealId": debtdealid
        }
        resp = session.get(buy_debt_url, post_data)
        print resp.content


headers = {
"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:35.0) Gecko/20100101 Firefox/35.0",
"Accept": "*/*",
"Accept-Language": "en-US,en;q=0.5",
"Accept-Encoding": "gzip, deflate",
"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
"X-Requested-With": "XMLHttpRequest",
"Referer": "https://invdebt.ppdai.com/buy/list?monthGroup=1%2C2%2C&rate=9.5&category=1&sortType=6&levels=%2C&currentLevels=%2CAA%2C&lastDueDays=&overDueDays=&isShowMore=&minAmount=&maxAmount=&minPastDueDay=&maxPastDueDay=&minPastDueNumber=&maxPastDueNumber=&minAllowanceRadio=&maxAllowanceRadio=&special=",
"Content-Length": "16",
"Cookie": "regSourceId=0; referID=0; fromUrl=; referDate=2018-8-2%208%3A18%3A18; currentUrl=https%3A%2F%2Finvdebt.ppdai.com%2Fbuy%2Flist%3Fmonthgroup%3D1%252c2%252c%26rate%3D9.5%26category%3D1%26sorttype%3D6%26levels%3D%252c%26currentlevels%3D%252caa%252c%26lastduedays%3D%26overduedays%3D%26isshowmore%3D%26minamount%3D%26maxamount%3D%26minpastdueday%3D%26maxpastdueday%3D%26minpastduenumber%3D%26maxpastduenumber%3D%26minallowanceradio%3D%26maxallowanceradio%3D%26special%3D; uniqueid=f943569b-1882-401b-acd5-de2be914e820; __fp=fp; __vid=2054332811.1533169099792; __vsr=1533169099792.src%3Ddirect%7Cmd%3Ddirect%7Ccn%3Ddirect; gr_user_id=6b65af5c-f73c-4628-9ce5-cc4a1410ab42; Hm_lvt_f87746aec9be6bea7b822885a351b00f=1533169127,1533208780,1533513086,1534983514; openid=03d61dd09a46ce9cd3db29f2d6692ff3; ppd_uname=pdu45415304; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22pdu45415304%22%2C%22%24device_id%22%3A%22164f816880e34f-0ea0176b6ab70f-46544136-2073600-164f816880f8bf%22%2C%22first_id%22%3A%22164f816880e34f-0ea0176b6ab70f-46544136-2073600-164f816880f8bf%22%7D; aliyungf_tc=AQAAAC9eaG2ZwgcAem9S0gcc9KH0p+zO; noticeflag=true; __tsid=119078225; Hm_lpvt_f87746aec9be6bea7b822885a351b00f=1535084259; _ppdaiWaterMark=15349835148210; token=2fdcd0675943ffa7e0aa6b7cf4033b510ab4d550075f52a437ddb202506035b3c741bfdab866; __eui=yVp0QfEX5Bg%3D; waterMarkTimeCheck1=08%2F24%2F2018+12%3A17%3A38; __sid=1535081053922.9.1535084259120; gr_session_id_b9598a05ad0393b9=e78b028b-6281-4b82-b9a4-7ffa19f040d2; gr_session_id_b9598a05ad0393b9_e78b028b-6281-4b82-b9a4-7ffa19f040d2=true",
"Connection": "keep-alive",
"Pragma": "no-cache",
"Cache-Control": "no-cache",
}
url = "https://invdebt.ppdai.com/buy/buyPreCheck"
data = {"debtId": "117940945"}
resp = requests.post(url, json=data, headers=headers)
print resp.content


exit()
buy_debt_url = 'https://invdebt.ppdai.com/buy/buyDebt'
post_data = {
    "debtDealId": 117930809
}
resp = requests.post(buy_debt_url, json=post_data, headers=headers)
print resp.content

exit()
if __name__ == "__main__":
    while True:
        try:
            if not check_login_status():
                break
            one_key_bid()
        except Exception as e:
            logger.error(e)
        time.sleep(sleep_interval)
