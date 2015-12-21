# -*- coding: utf-8 -*-
__author__ = 'huafeng'

import time
import gevent
import requests
import gevent.monkey

gevent.monkey.patch_socket()

thread_count = 100  #指定同一时刻并发量

url = 'http://192.168.0.144:9081/IBANK'

# cookie_dic = {
#     '?BANK_TYPE':'60',
#     'CARD_NO':'120105198907310623',
#     'PWD':'Rng360',
#     'MAIN_CARD':'4367420********7791',
# }
# r = requests.get(url, cookies=cookie_dic)

s = requests.Session()  #注意cookie设置时，value必须为string基础类型
s.cookies['?BANK_TYPE'] = '60'
s.cookies['CARD_NO'] = '120105198907310623'
s.cookies['PWD'] = 'Rng360'
s.cookies['MAIN_CARD'] = '4367420********7791'

def read(url):
    try:
        context = s.get(url)
        print context
    except Exception:
        print "load %s failure." %url
        return

def concuyRead():
    start = time.time()
    threads = []
    for i in range(thread_count):
        threads.append(gevent.spawn(read, url))
    gevent.joinall(threads)
    end = time.time()
    print "consume time: %d" %(end-start)

if __name__ == '__main__':
    concuyRead()
    # for i in range(1, 20):
    #     concuyRead()
    #     time.sleep(1)