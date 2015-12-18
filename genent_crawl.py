# -*- coding: utf-8 -*-
__author__ = 'huafeng'

import time
import gevent
import requests
import gevent.monkey

gevent.monkey.patch_socket()

thread_count = 100  #指定同一时刻并发量

url = 'http://10.0.2.53:9091/Tasker?Action=0&TemplateID=200001'


def read(url):
    try:
        context = requests.post(url)
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
    print "Elapsed Time : %d" %(end-start)

if __name__ == '__main__':
    concuyRead()
