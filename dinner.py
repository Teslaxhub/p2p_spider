#coding:utf-8
import urllib2
import re
import time
import poplib
import urllib
from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr

def popRequests(username, password, pop3_server):
    '''
    公司订餐系统升级，共分为四个步骤
    1、模拟订餐按钮点击动作，服务器生成一个url连接发送到邮箱中
    2、通过pop协议读取有邮件，解析出该url连接并模拟点击该链接
    3、点击邮箱中的确认连接以后会在指定页面生成自己订餐记录，可以解析该页面，通过正则查看自己的邮箱是不是已经在成功订餐的列表中
    4、若成功，则向自己指定的邮箱发送邮件通知该次订餐操作执行成功；若失败则间隔5秒后做第二次操作
    '''
    def guess_charset(msg):
        charset = msg.get_charset()
        if charset is None:
            content_type = msg.get('Content-Type', '').lower()
            pos = content_type.find('charset=')
            if pos >= 0:
                charset = content_type[pos + 8:].strip()
        return charset

    def decode_str(s):
        value, charset = decode_header(s)[0]
        if charset:
            value = value.decode(charset)
        return value
    content_list = []
    def print_info(msg, indent=0):

        if indent == 0:
            for header in ['From', 'To', 'Subject']:
                value = msg.get(header, '')
                if value:
                    if header=='Subject':
                        value = decode_str(value)
                    else:
                        hdr, addr = parseaddr(value)
                        name = decode_str(hdr)
                        value = u'%s <%s>' % (name, addr)
                # print('%s%s: %s' % ('  ' * indent, header, value))
        if (msg.is_multipart()):
            parts = msg.get_payload()
            for n, part in enumerate(parts):
                # print('%spart %s' % ('  ' * indent, n))
                # print('%s--------------------' % ('  ' * indent))
                print_info(part, indent + 1)
        else:
            content_type = msg.get_content_type()
            if content_type=='text/plain' or content_type=='text/html':
                content = msg.get_payload(decode=True)
                charset = guess_charset(msg)
                if charset:
                    content = content.decode(charset)
                # print('%sText: %s' % ('  ' * indent, content + '...'))
                content_list.append(content)
            else:
                print('%sAttachment: %s' % ('  ' * indent, content_type))
        return  "".join(content_list)

    server = poplib.POP3(pop3_server)
    server.user(username)
    server.pass_(password)
    # print('Messages: %s. Size: %s' % server.stat())
    resp, mails, octets = server.list()
    resp, lines, octets = server.retr(len(mails))
    msg = Parser().parsestr('\r\n'.join(lines))
    return print_info(msg)

def order_inner(username):
    url = 'http://mis.rong360.com/mis/welcome/dinner.html'
    # ss = requests.session()
    post_data = {
        'email':'%s@rong360.com'%username
    }
    post_data = urllib.urlencode(post_data)
    req = urllib2.Request(url, post_data)
    # ss.post(url, data=post_data)
    urllib2.urlopen(req)
    print 'dinner order sucess...'
def confirmInEmail(username, password, pop3_server='mail.rong360.com'):
    confirm_pattern = ur'<a href="(.*?)">'
    mail_content = popRequests(username, password, pop3_server)
    try:
        confirm_url = re.search(confirm_pattern, mail_content).group(1)
        urllib2.urlopen(confirm_url)
    except:
        print "Email confirm failed..."
    print 'check email sucess...'
def checkIfSucess():
    check_url = 'http://mis.rong360.com/mis/welcome/dinnerlist.html'
    # html = requests.get(check_url).text
    html = urllib2.urlopen(check_url).read()
    if '%s@rong360.com'%username in html:
        print 'your name in the dinner lists, so congratulations ! ! !'
        return True
    else:
        print 'sorry, dinner order failed...'
        return False
def mail_send(mail_content, mailto):
    import time
    import smtplib
    from email.mime.text import MIMEText
    mail_host_server = "smtp.163.com"
    mail_user = 'wachfx@163.com'
    mail_password = ''

    msg = MIMEText(mail_content, _subtype='html', _charset='utf-8')
    timestamp = time.strftime('%Y_%m_%d_%H%M%S')
    msg['Subject'] = 'dinner sucess...' + timestamp
    msg['From'] = mail_user

    s = smtplib.SMTP()
    s.connect(mail_host_server)
    s.login(mail_user, mail_password)
    s.sendmail(mail_user, mailto, msg.as_string())
    s.close()

if __name__ == "__main__":
    mail_list = ['chenchong', 'zhoufei']
    for user in mail_list:
        order_inner(user)
    username = 'wanghuafeng'
    password = ''
    order_inner(username)
    time.sleep(5)#延迟n秒，以保证确认订餐邮件已发送至邮箱内
    confirmInEmail(username, password)
    sucessed = checkIfSucess()
    if not sucessed:
        order_inner(username)
        time.sleep(5)#延迟n秒，以保证确认订餐邮件已发送至邮箱内
        confirmInEmail(username, password)
        sucessed = checkIfSucess()
        if not sucessed:
            order_inner(username)
            time.sleep(5)#延迟n秒，以保证确认订餐邮件已发送至邮箱内
            confirmInEmail(username, password)
            sucessed = checkIfSucess()
        else:
            mail_send('dinner sucess...', 'wanghuafeng@rong360.com')
    else:
        mail_send('dinner sucess...', 'wanghuafeng@rong360.com')