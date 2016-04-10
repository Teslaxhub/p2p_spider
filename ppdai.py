# -*- coding: utf-8 -*-
import re
import requests
from bs4 import BeautifulSoup

ss = requests.session()
login_url = 'https://ac.ppdai.com/User/Login'
post_data = {
    'IsAsync':'true',
    'Password':'',
    'Redirect':'http://www.ppdai.com/account',
    'RememberMe':'true',
    'UserName':''
}
ss.post(login_url, post_data)

content_url = 'http://www.ppdai.com/account'
black_list_url = 'http://invest.ppdai.com/account/blacklist'
black_list_html = ss.get(black_list_url).content
soup = BeautifulSoup(black_list_html)

def get_page_no():
    '''解析黑名单总页数'''
    page_no = 0
    try:
        total_page_str = soup.find('div', class_='fen_ye_nav').find_all('a')[-1]['href']
        page_no = re.search(r'PageIndex=([0-9]*)', total_page_str).group(1)
    except BaseException:
        print '黑名单总页数抓取失败'
    return page_no

id_list = [item['listingid']  for item in soup.find_all('tr', 'blacklistdetail dn')]

def get_credit_Rating(user_id):
    '''根据用户id，获取评级参数'''
    detail_url = 'http://invest.ppdai.com/loan/info?id=' + user_id
    black_detail_info_html = ss.get(detail_url).content    # creditRating D
    creditRatingSoup = BeautifulSoup(black_detail_info_html)
    creditRating = creditRatingSoup.find('span', class_=re.compile('creditRating'))['class'][-1]
    # user_desc = creditRatingSoup.find('div', class_='lendDetailTab_tabContent').find('p').text
    user_desc = creditRatingSoup.find('span', attrs={'tt':re.compile('\d*')}).text
    return user_desc, creditRating
    # print  user_desc

    # return creditRating
# get_credit_Rating('')
for user_id in id_list:
    print '\t'.join(get_credit_Rating(user_id))