# -*- coding: utf-8 -*-
import os
import  time
import subprocess
detect_dir = r'E:\php_workspace\ec_vm\home'

def get_phpfile_list():
    php_file_list = []
    for root, subdir, filelist in  os.walk(detect_dir):
        for filename in filelist:
            abs_path = os.path.join(root, filename)
            if (os.path.isfile(abs_path) and abs_path.endswith('.php')):
                php_file_list.append(abs_path)
# get_phpfile_list()

def detect_phpcode(phpfile):
    if not os.path.isfile(phpfile):
        print 'file not exists:%s' % phpfile
        return
    check_command = 'php -l %s' % phpfile
    detect_info = subprocess.call(check_command, shell=True)
    # print detect_info
    # print detect_info .stdout.read()
    # if detect_info.find('No syntax errors detected in') == 0:
    #     print 'yes'
# detect_phpcode(r'E:\php_workspace\ec_vm\home\rong\www\ec\model\MailParseSinaMobile.php')



url = 'http://10.0.2.53:9091/Tasker?Action=0&TemplateID=200000'
import requests
for i in range(1, 100000):
    std = subprocess.Popen(requests.post(url), shell=True, stdout=subprocess.PIPE)
    print std.stdout.read()
    # time.sleep(1)
