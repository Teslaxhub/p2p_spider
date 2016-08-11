# -*- coding: utf-8 -*-
import re
import json
import time
import requests
import random
from bs4 import BeautifulSoup
ss = requests.session()
current_time = time.strftime('%Y-%m-%d %H:%M:%S')
bid_amount  = 50
def login():
    '''登陆'''
    # interval = random.randint(180,1700) #登陆时间尽量随机化3--30min
    # time.sleep(interval)
    print '**********************logining:%s*******************************'%current_time
    login_url = 'https://ac.ppdai.com/User/Login'
    post_data = {
        'Password':'',
        'UserName':''
    }
    ss.post(login_url, post_data, verify=False)

# def css_filter(x):
#     return re.compile('clearfix') and  re.compile('xsbol')

def get_rating_AA_id_list():
    '''获取AA及用户id, 三个月'''
    rating_order_url = 'http://invest.ppdai.com/loan/list_Safe_s10_p1?monthgroup=&rate=0&didibid=&listingispay=on'
    rating_html = ss.get(rating_order_url).content
    rating_inorder_soup = BeautifulSoup(rating_html)
    soup =  rating_inorder_soup.find('div',class_='wapBorrowList clearfix')
    # print soup.find_all('ol', class_= 'clearfix')
    user_info_list = [{'credit_rating':item.find('i', class_=re.compile('creditRating'))['class'][-1],  #获取等级
                    'uid':item.find('input')['id'], #获取用户id
                    'limit_time':int(item.find('div', class_='limitTime').contents[0].strip()), # 获取期限
                    'invested_already':1 if re.search('\d',item.find('span',id=True).text) else 0 # 判断是否已投
                    }
                   for item in soup.find_all('ol', class_= re.compile('clearfix')) if 'xsbol' not in item['class']]
    return user_info_list
def get_rating_A_id_list():
    '''分析最高等级的10个用户，获取等级为A的用户id'''
    rating_order_url = 'http://invest.ppdai.com/loan/list_RiskMiddle_s5_p1?monthgroup=&rate=0&didibid=&listingispay='
    rating_html = ss.get(rating_order_url).content
    rating_inorder_soup = BeautifulSoup(rating_html)
    soup =  rating_inorder_soup.find('div',class_='wapBorrowList clearfix')
    user_info_list = [{'credit_rating':item.find('i', class_=re.compile('creditRating'))['class'][-1],  #获取等级
                    'uid':item.find('input')['id'], #获取用户id
                    'limit_time':int(item.find('div', class_='limitTime').contents[0].strip()), # 获取期限
                    'invested_already':1 if re.search('\d',item.find('span',id=True).text) else 0 # 判断是否已投
                    }
                   for item in soup.find_all('ol', class_='clearfix')]
    return user_info_list
    # if not user_info_list:
    #     print 'user list empty , check if html pattern chged'
    # id_list = [user_info['uid'] for user_info in user_info_list #筛选符合条件的uid
    #            if (user_info['invested_already'] == 0 and user_info['credit_rating'] == 'A' and user_info['limit_time'] <= 12)]
    # if not id_list:
    #     print 'no id meets the your conditions(A+ within 12 month)'
    # return  id_list

def auto_bid_filter(user_info_list, credit_ratting='A', limit_time=12):
    '''筛选用户信息'''
    try:
        limit_time = int(limit_time)
    except:
        print '时间参数类型错误'
    if not user_info_list:
        print 'user list empty , check if html pattern chged'
    id_list = [user_info['uid'] for user_info in user_info_list #筛选符合条件的uid
               if (user_info['invested_already'] == 0 and user_info['credit_rating'] == credit_ratting and user_info['limit_time'] <= limit_time)]
    return  id_list

def bid(uid, amount=0):
    '''投标'''
    if not amount:
        amount = bid_amount
    bid_url = 'http://invest.ppdai.com/Bid/Bid'
    post_data = {
        'Amount':amount,  # 金额
        'ListingId':uid, # 11383558
    }
    bid_info_json = json.loads(ss.post(bid_url, post_data).content)
    if  bid_info_json.get('Message') == u'投标成功':
        print u'autobid success,time:%s,uid:%s' %(time.strftime('%Y-%m-%d %H:%M:%S'), uid)
    elif u'您的账户余额不够' in bid_info_json.get('Message'):
        return
    else:
        print bid_info_json.get('Message')
        print u'autobid failes,time:%s,uid:%s' %(time.strftime('%Y-%m-%d %H:%M:%S'), uid)
def get_amount_left():
    '''获取当前余额'''
    url = 'http://invest.ppdai.com/account/lend'
    soup = BeautifulSoup(ss.get(url).content)
    try:
       amount = float(soup.find('div', class_='my-ac-ctListall clearfix').find('p', class_='useramount').em.text.strip())
       print 'current amount:%s'%amount
    except:
        print 'get amount param falied'
        return False
    return amount

def main():
    login()
    amount = get_amount_left()
    if amount and (amount < bid_amount): #获取余额成功且余额大于当前最小投标额
        return
    #A类型12个月
    # user_info_list = get_rating_A_id_list()
    # bid_id_list = auto_bid_filter(user_info_list)
    #AA类型3个月
    user_info_list = get_rating_AA_id_list()
    bid_id_list = auto_bid_filter(user_info_list, 'AA', 3)
    if not bid_id_list:
        return
    else:
        for uid in bid_id_list:
            bid(uid, amount)
            time.sleep(3) #
if __name__ == "__main__":
    main()
