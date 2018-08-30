#!-*- coding:utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import json
import re
import requests
from bs4 import BeautifulSoup
from utils import retries
from mail_send import mail_monitor
from model.platform import Platform

default_timeout = 10
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:35.0) Gecko/20100101 Firefox/35.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}


class PlatformData(object):
    def __init__(self):
        self.platform_id_dic = {}
        self.platform_model = Platform()

    @retries()
    def get_plat_ids(self):
        """获取平台名称及平台id"""
        root_url = 'https://shuju.wdzj.com'
        resp = requests.get(root_url, headers=headers, timeout=default_timeout)
        content = resp.content.decode('utf-8')
        base_soup = BeautifulSoup(content, 'lxml')
        plat_info_list = base_soup.find('tbody', id='platTable').find_all('tr', class_=True)
        for plat_info in plat_info_list:
            dom_a_soup = plat_info.find('td', class_='td-item td-platname').find('a')
            href = dom_a_soup['href']
            plat_id = re.search(ur'plat-info-(\d+)\.html', href).group(1)
            platform_name = dom_a_soup.get_text(strip=True)
            self.platform_id_dic[platform_name] = plat_id
        # for k in platform_page_url_dic:
        #     print k, platform_page_url_dic.get(k)

    @retries()
    def _do_request(self, data):
        url = 'https://shuju.wdzj.com/plat-info-target.html'
        resp = requests.post(url, data=data, headers=headers, timeout=default_timeout)
        return resp.json()

    def new_borrow(self, plat_id):
        """新增投资"""
        post_data = {
            "target1": 1,
            "target2": 0,
            "type": 1,
            "wdzjPlatId": plat_id,
        }
        jdata = self._do_request(post_data)
        date_list = jdata.get('date')
        newmoney_list = jdata.get('data1')
        data_tuple_list = zip(date_list, newmoney_list)
        for data_tuple in data_tuple_list:
            res_tmp = {}
            res_tmp['time_sequences'] = data_tuple[0]
            res_tmp['newmoney'] = data_tuple[1]
            pt = "%s_%s" % (data_tuple[0], plat_id)
            self.platform_parsed_data[pt] = res_tmp

    def invest_user_count(self, plat_id):
        """新/老投资人数"""
        post_data = {
            "target1": "19",
            "target2": "20",
            "type": "1",
            "wdzjPlatId": plat_id,
        }
        jdata = self._do_request(post_data)
        date_list = jdata.get('date')
        newuser_count_list = jdata.get('data1')
        olduser_count_list = jdata.get('data2')
        data_tuple_list = zip(date_list, newuser_count_list, olduser_count_list)
        for data_tuple in data_tuple_list:
            res_tmp = {}
            res_tmp['time_sequences'] = data_tuple[0]
            res_tmp['newuser_count'] = data_tuple[1]
            res_tmp['olduser_count'] = data_tuple[2]
            pt = "%s_%s" % (data_tuple[0], plat_id)
            self.platform_parsed_data.get(pt).update(res_tmp)

    def user_invest_amount(self, plat_id):
        """新/老投资人的投资额"""
        post_data = {
            "target1": "21",
            "target2": "22",
            "type": "1",
            "wdzjPlatId": plat_id,
        }
        jdata = self._do_request(post_data)
        date_list = jdata.get('date')
        newuser_money_list = jdata.get('data1')
        olduser_money_list = jdata.get('data2')
        data_tuple_list = zip(date_list, newuser_money_list, olduser_money_list)
        for data_tuple in data_tuple_list:
            res_tmp = {}
            res_tmp['time_sequences'] = data_tuple[0]
            res_tmp['newuser_money'] = data_tuple[1]
            res_tmp['olduser_money'] = data_tuple[2]
            pt = "%s_%s" % (data_tuple[0], plat_id)
            self.platform_parsed_data.get(pt).update(res_tmp)

    def get_platform_detail_data(self, plat_id):
        """根据plat_id抓取平台维度数据"""
        try:
            self.platform_parsed_data = {}
            self.new_borrow(plat_id)
            self.invest_user_count(plat_id)
            self.user_invest_amount(plat_id)
            # print json.dumps(self.platform_parsed_data, sort_keys=True)
        except Exception as e:
            mi = "plat_id:%s\terr_msg:%s" % (plat_id, e)
            print mi

    def platform_run(self):
        self.get_plat_ids()
        plat_id_set = set()
        for plat_name in self.platform_id_dic:
            plat_id = self.platform_id_dic.get(plat_name)
            self.get_platform_detail_data(plat_id)
            for parsed_info in self.platform_parsed_data.values():
                parsed_info['platform_name'] = plat_name
                time_sequences = parsed_info.get('time_sequences')
                try:
                    res = self.platform_model.check_for_update_by_plat_time(plat_name, time_sequences, parsed_info)
                    if res:
                        plat_id_set.add(plat_id)
                except Exception as e:
                    msg =  'sql_exec fail\tplat_name=%s\tparsed_info=%s\terr_msg=%s' % (plat_name, parsed_info, e)
                    print msg
                    mail_monitor(msg)
        new_plat_cnt = len(plat_id_set)
        if new_plat_cnt:
            mail_monitor('之家新增平台数:%s' % new_plat_cnt)

if __name__ == "__main__":
    p = PlatformData()
    p.platform_run()