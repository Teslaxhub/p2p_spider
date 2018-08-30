#!-*- coding:utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import json
import codecs
import requests
from bs4 import BeautifulSoup
from model.industry import Industry
from model.platform import Platform
from mail_send import mail_monitor
from utils import retries
default_timeout = 10
platform_detail_url_filepath = r'data/eye_platform_detail_info_url'


class PlatformData(object):
    def __init__(self):
        self.platform_model = Platform()

    def get_plat_info_list(self):
        headers = {
            "Host": "www.p2peye.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:35.0) Gecko/20100101 Firefox/35.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }
        root_url = 'https://www.p2peye.com/shuju/ptsj/'
        resp = requests.get(root_url, headers=headers, timeout=default_timeout)
        content = resp.content.decode('gbk')
        base_soup = BeautifulSoup(content, 'lxml')
        plat_info_list = base_soup.find('table', id='platdata').find_all('tr', class_='bd')
        platform_page_url_list = []
        for plat_info in plat_info_list:
            dom_a_soup = plat_info.find('td', class_='name').find('a')
            href = 'https:' + dom_a_soup['href']
            platform_page_url_list.append(href)
        return platform_page_url_list

    def load_plat_url_from_local(self):
        platform_page_url_list = [item.strip().split('\t')[-1] for item in codecs.open(platform_detail_url_filepath, encoding='utf-8').readlines()]
        return platform_page_url_list

    def get_plat_info_urls(self):
        """获取平台名称以及对应url地址"""
        platform_page_url_list = self.get_plat_info_list()
        if not platform_page_url_list:
            platform_page_url_list = self.load_plat_url_from_local()
        assert platform_page_url_list, "获取平台名称及url地址失败"
        return platform_page_url_list

    @retries(retry_times=4)
    def platform_request(self, url):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:35.0) Gecko/20100101 Firefox/35.0",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "X-Requested-With": "XMLHttpRequest",
            "Connection": "keep-alive",
        }
        try:
            resp = requests.get(url, headers=headers, timeout=default_timeout)
            jdata = resp.json()
            assert jdata.get('code') == "200"
            platform_info_list = jdata.get('data', {}).get('data')
            return platform_info_list
        except Exception as e:
            raise Exception('url=%s\terr_msg=%s' % (url, e))

    def get_platform_detail_data(self, plat_url):
        try:
            self.platform_parsed_data = {}
            self.new_borrow(plat_url)
            self.inflows(plat_url)
            self.invest_user_count(plat_url)
            self.user_invest_amount(plat_url)
        except Exception as e:
            if 'platjump' not in plat_url:  # 过滤特殊地址
                mi = "url:%s\terr_msg:%s" % (plat_url, e)
                mail_monitor(mi)
                print mi

    def new_borrow(self, plat_url):
        """新增投资"""
        url = '%s?&type=new_borrow_paid&flag=1' % plat_url
        platform_info_list = self.platform_request(url)
        for platform_info in platform_info_list:
            res_tmp = {}
            platform_name = platform_info.get('platform_name')
            newmoney = platform_info.get('newmoney')
            time_sequences = platform_info.get('time_sequences')
            plat_official_url = platform_info.get('plat_name')
            res_tmp['platform_name'] = platform_name
            res_tmp['newmoney'] = newmoney
            res_tmp['time_sequences'] = time_sequences
            res_tmp['plat_official_url'] = plat_official_url
            pt = "%s_%s" % (time_sequences, platform_name)
            self.platform_parsed_data[pt] = res_tmp
            self.platform_parsed_data[pt]['data_from'] = u'天眼'

    def inflows(self, plat_url):
        """资金净流入"""
        url = '%s?&type=inflows&flag=1' % plat_url
        platform_info_list = self.platform_request(url)
        for platform_info in platform_info_list:
            moneyinout = platform_info.get('moneyinout')
            platform_name = platform_info.get('platform_name')
            time_sequences = platform_info.get('time_sequences')
            plat_official_url = platform_info.get('plat_name')
            pt = "%s_%s" % (time_sequences, platform_name)
            if pt not in self.platform_parsed_data:
                return
            self.platform_parsed_data[pt]['moneyinout'] = moneyinout

    def invest_user_count(self, plat_url):
        """新/老投资人数"""
        url = '%s?&type=invest_vs&flag=1' % plat_url
        platform_info_list = self.platform_request(url)
        for platform_info in platform_info_list:
            newuser_count = platform_info.get('newuser_count')
            olduser_count = platform_info.get('olduser_count')
            platform_name = platform_info.get('platform_name')
            time_sequences = platform_info.get('time_sequences')
            plat_official_url = platform_info.get('plat_name')
            pt = "%s_%s" % (time_sequences, platform_name)
            if pt not in self.platform_parsed_data:
                return
            self.platform_parsed_data[pt]['newuser_count'] = newuser_count
            self.platform_parsed_data[pt]['olduser_count'] = olduser_count

    def user_invest_amount(self, plat_url):
        """新/老投资人的投资额"""
        url = '%s?&type=invest_total_vs&flag=1' % plat_url
        platform_info_list = self.platform_request(url)
        for platform_info in platform_info_list:
            newuser_money = platform_info.get('newuser_money')
            olduser_money = platform_info.get('olduser_money')
            platform_name = platform_info.get('platform_name')
            time_sequences = platform_info.get('time_sequences')
            plat_official_url = platform_info.get('plat_name')
            pt = "%s_%s" % (time_sequences, platform_name)
            if pt not in self.platform_parsed_data:
                return
            self.platform_parsed_data[pt]['newuser_money'] = newuser_money
            self.platform_parsed_data[pt]['olduser_money'] = olduser_money

    def platform_run(self):
        platform_url_list = self.get_plat_info_urls()
        if not platform_url_list:
            mail_monitor('天眼平台地址获取为空，请确认')
            return
        platform_set = set()
        for platform_url in platform_url_list:
            self.get_platform_detail_data(platform_url)
            for parsed_info in self.platform_parsed_data.values():
                try:
                    if self.platform_model.get_by_plat_time(parsed_info.get('platform_name'), parsed_info.get('time_sequences')):
                        continue
                    platform_set.add(platform_url)
                    self.platform_model._insert(**parsed_info)
                except Exception as e:
                    msg =  'sql_exec fail\tindustry_run\tparsed_info=%s\terr_msg=%s' % ( parsed_info, e)
                    print msg
        platform_cnt = len(platform_set)
        if platform_cnt > 0:
            mail_monitor('天眼新增平台数:%s' % platform_cnt)


class IndustryData():
    def __init__(self):
        self.industry_model = Industry()
        self.industry_parsed_data = {}

    @retries(retry_times=4)
    def industry_request(self, url):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:35.0) Gecko/20100101 Firefox/35.0",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://lu.p2peye.com/shuju/",
            "Connection": "keep-alive",
        }
        data_list = []
        try:
            resp = requests.get(url, headers=headers, timeout=default_timeout)
            jdata = resp.json()
            data_list = jdata.get('data', [])
        except Exception as e:
            print 'industry_request fail, err_msg:%s' % e
        return data_list

    def industry_invest_data(self):
        """行业口径成交量、资金净流入、平均期限等数据"""
        url = 'https://www.p2peye.com/platformData.php?mod=industrydata&ajax=1&industryDataFlag=1'
        data_list = self.industry_request(url)
        for data_detail in data_list:
            res_tmp = {}
            process_amount = data_detail.get('process_amount')  # 新增成交量
            moneyinout = data_detail.get('moneyinout')  # 资金净流入
            avg_industry_times = data_detail.get('avg_industry_times')  # 平均期限
            time_sequences = data_detail.get('time_sequences')  #
            res_tmp['process_amount'] = process_amount
            res_tmp['moneyinout'] = moneyinout
            res_tmp['avg_industry_times'] = avg_industry_times
            res_tmp['time_sequences'] = time_sequences
            self.industry_parsed_data[time_sequences] =res_tmp

    def industry_alive_plat_cnt(self):
        """存活平台数"""
        url = 'https://www.p2peye.com/platformData.php?mod=industrydata&ajax=1&platformNumberFlag=2'
        data_list = self.industry_request(url)
        for data_detail in data_list:
            noblack_total = data_detail.get("noblack_total")    # 正常运营
            time_sequences = data_detail.get("time_sequences")  #
            if time_sequences in self.industry_parsed_data:
                self.industry_parsed_data[time_sequences]['plat_alive_count'] = noblack_total

    def industry_run(self):
        self.industry_invest_data()
        self.industry_alive_plat_cnt()
        assert self.industry_parsed_data
        data_cnt = 0
        for parsed_info in self.industry_parsed_data.values():
            try:
                if self.industry_model.get_by_time_sequences(parsed_info.get("time_sequences")):
                    continue
                data_cnt += 1
                self.industry_model._insert(**parsed_info)
            except Exception as e:
                msg =  'sql_exec fail\tindustry_run\tparsed_info=%s\terr_msg=%s' % ( parsed_info, e)
                print msg
        if data_cnt > 0:
            mail_monitor('新增平台数据数cnt: %s' % data_cnt)

if __name__ == "__main__":
    try:
        industry_model = IndustryData()
        industry_model.industry_run()
        plat_model = PlatformData()
        plat_model.platform_run()
    except Exception as e:
        print e