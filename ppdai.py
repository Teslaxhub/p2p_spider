# -*- coding: utf-8 -*-
import re
import requests
from collections import Counter
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
if __name__ == '__main__':
    page_no = get_page_no()
    credit_rate_list = []
    for index in range(1, int(page_no)+1):
        print '----------------当前第:%s页------------------' % index
        black_list_page_url = 'http://invest.ppdai.com/account/blacklist?PageIndex=%s&IsCalendarRequest=0'%index
        black_list_html = ss.get(black_list_page_url).content
        soup = BeautifulSoup(black_list_html)
        id_list = [item['listingid']  for item in soup.find_all('tr', 'blacklistdetail dn')]
        for user_id in id_list:
            user_desc_crdit_rate_tuple = get_credit_Rating(user_id)
            print '\t'.join(user_desc_crdit_rate_tuple)
            credit_rate_list.append(user_desc_crdit_rate_tuple[-1])
    rating_counter = Counter(credit_rate_list)
    val_sum = sum(rating_counter.values())
    print rating_counter
    print 'total overDuePerson count: %s' % val_sum
    for rating in rating_counter:
        print rating, float(rating_counter[rating])/val_sum