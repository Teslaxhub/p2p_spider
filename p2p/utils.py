#!-*- coding:utf-8 -*-
import time
def retries(retry_times=3, timeout=1):
    """对未捕获异常进行重试"""
    def decorator(func):
        def _wrapper(*args, **kw):
            att, retry = 0, 0
            while retry < retry_times:
                retry += 1
                try:
                    return func(*args, **kw)
                except Exception as e:
                    att += timeout
                    if retry < retry_times:
                        time.sleep(att)
        return _wrapper
    return decorator