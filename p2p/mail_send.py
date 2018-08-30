#!-*- coding:utf-8 -*-
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class SendEmail(object):
    def __init__(self):
        # 设置服务器
        self.mail_host = "smtp.mxhichina.com"
        # 用户名
        self.mail_user = "robot@daixiaomi.com"
        # 口令
        self.mail_pass = "I5VgIf2c^gIJg8H#6jf8##bL"

    # 发送邮件
    def send_mail(self, receive_list=[], sub_content='', text_type='', content='', attachments_list={}):
        # 附件检查，限制大小为单个不超过20M，总大小不超过50M
        _ATTACH_SINGLE_SIZE = 20 * 1024 * 1024
        _ATTACH_TOTAL_SIZE = 50 * 1024 * 1024
        attach_total_size = 0

        for (attachment_file_name, attachment_file_path) in attachments_list.items():
            attach_part_size = os.path.getsize(attachment_file_path)
            attach_total_size += attach_part_size
            if attach_part_size > _ATTACH_SINGLE_SIZE:
                return False
        if attach_total_size > _ATTACH_TOTAL_SIZE:
                return False

        # 支持的内容发送格式，plain普通文本，html格式
        text_type_scope = ['plain', 'html']

        # 任意设置显示名，收到信后，将按照设置显示
        me = "邮件机器人" + "<" + self.mail_user + ">"

        # 判断文本类型
        if text_type not in text_type_scope:
            print 'Error text type, please input plain for txt or html.'
            return False

        msg = MIMEMultipart()

        # 设置主题
        msg['Subject'] = sub_content
        msg['From'] = me
        msg['To'] = ";".join(receive_list)

        # 添加内容
        content_part = MIMEText(content, _subtype=text_type, _charset='utf-8')
        msg.attach(content_part)

        # 添加附件
        for (attachment_file_name, attachment_file_path) in attachments_list.items():
            attach_part = MIMEText(open(attachment_file_path, 'rb').read(), 'base64', 'gb2312')
            attach_part["Content-Type"] = 'application/octet-stream'
            attach_part["Content-Disposition"] = 'attachment; filename="' + str(attachment_file_name).strip() + '"'
            msg.attach(attach_part)

        try:
            s = smtplib.SMTP()
            # 连接SMTP服务器
            s.connect(self.mail_host)
            # 登陆服务器
            s.login(self.mail_user, self.mail_pass)
            # 发送邮件
            s.sendmail(me, receive_list, msg.as_string())
            s.close()
            return True
        except Exception, e:
            print str(e)
            return False

se = SendEmail()
receive_list = ['wanghuafeng@daixiaomi.com']
sub_content = 'p2p抓取报警'

def mail_monitor(content, receive_list=receive_list, sub_content=sub_content):
    assert isinstance(receive_list, (list, tuple))
    if not content.strip():
        return
    mail_send = se.send_mail(
        receive_list=receive_list,
        sub_content=sub_content,
        text_type="html",
        content=content
    )


if __name__ == '__main__':
    mail_monitor('hello', ['wanghuafeng@daixiaomi.com'], sub_content='p2p报警')
