# -*- coding: utf-8 -*-

import requests
ss = requests.session()
USERNAME = 'wanghuafeng' #用户名
PASSWORD = '' #密码
MAIL_SUFFIX = '@rong360.com'
#登陆
oa_login_url = 'http://oa.rong360.com/site/login.html'
ss.post(oa_login_url, data={'email':USERNAME,'password':PASSWORD})
#订餐
ss.get('http://oa.rong360.com/home/addDinner?office=1')
#查询订餐是否成功
check_dinner_list_url = 'http://oa.rong360.com/home/index'
dinner_page = ss.get(check_dinner_list_url).content

def mail_send(mail_from, mailto, mail_content):
    import time
    import smtplib
    from email.mime.text import MIMEText
    smtp_server = "mail.rong360.com"

    #设置邮件类型
    msg = MIMEText(mail_content, _subtype='html', _charset='gbk')
    timestamp = time.strftime('%Y_%m_%d')
    msg['Subject'] = mail_content + ', ' + timestamp
    msg['From'] = 'rong360'

    s = smtplib.SMTP()
    s.connect(smtp_server)
    s.login(USERNAME, PASSWORD)
    s.sendmail(mail_from, mailto, msg.as_string())
    s.close()

mail = USERNAME+MAIL_SUFFIX
if mail in dinner_page: #订餐成功
    mail_send(mail,  mail, 'dinner sucess...')
else: #订餐失败
    mail_send(mail, mail,'dinner failed...',)

