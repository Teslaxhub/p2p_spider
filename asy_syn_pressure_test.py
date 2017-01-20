# -*- coding: utf-8 -*-
__author__ = 'huafeng'
import sys, os, re, time
import gevent
import requests
import gevent.monkey
from bs4 import BeautifulSoup
gevent.monkey.patch_socket()

def check_proxy_ip(ip_port, with_proxy=True):
    try:
        alive_check_url = 'http://1212.ip138.com/ic.asp'
        if with_proxy:
            proxies = {
                'http':'http://%s' % ip_port,
                'https':'http://%s' % ip_port
            }
            html = requests.get(alive_check_url, proxies=proxies, timeout=15).content
        else:
            html = requests.get(alive_check_url, timeout=15).content
        soup = BeautifulSoup(html)
        ip_info = soup.find('body').text
        # print '%s, time_consume:%s'%(ip_info, end-start)
        return ip_info
    except:
        return False

def asy_gevent_run(ip_port, thread_count):
    threads = []
    for i in range(thread_count):
        threads.append(gevent.spawn(check_proxy_ip, ip_port))
    gevent.joinall(threads)
    for thread_ret in threads:
        print thread_ret.value
    print 'total fail count:%s' % len([item for item in threads if not item.value])

def syn_check_xiaomi_proxy(proxy_ip_port, total_count):
    fail_count = 0
    # total_count = 60
    for i in range(0, total_count):
        # proxy_ip_port = '121.201.69.253:9003'
        # proxy_ip_port = '119.254.98.36:8121'
        ret =  check_proxy_ip(proxy_ip_port)#121.201.69.253:9003/119.254.98.36:8121
        print ret
        if not ret:
            fail_count += 1
    print 'total count:%s, fail count:%s, sucess rate:%s' % (total_count, fail_count, 1-fail_count/float(total_count))#29

if __name__ == '__main__':
    pass
    thread_count = 10  #指定同一时刻并发量
    ip_port = '119.254.98.6:8121'
    # ip_port = '121.201.9.253:9003'
    # asy_gevent_run(ip_port, thread_count)
    syn_check_xiaomi_proxy(ip_port, thread_count)