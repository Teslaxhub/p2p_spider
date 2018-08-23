#!-*- coding:utf-8 -*-
import requests
headers = {
    "Host": "www.tuandai.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:35.0) Gecko/20100101 Firefox/35.0",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www.tuandai.com/pages/invest/zqzr_list.aspx",
    "Content-Length": "161",
    "Connection": "keep-alive",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
}


post_data = {
    "beginRate": "0",
    "endDeadLine": "3",
    "endRate": "0",
    "flashData": "false",
    "initPage": "10",
    "orderby": "9",
    "pageindex": "1",
    "pagesize": "5",
    "rate": "13",
    "repaymentTypeId": "0",
    "startDeadLine": "1",
    "status": "1",
    "strkey": "",
    "type": "1",
}
url = 'https://www.tuandai.com/pages/invest/getZqzrList'
resp = requests.post(url, post_data, headers=headers)
print resp.content