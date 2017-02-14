
#encoding:utf-8

import requests
import urllib
import codecs
from bs4 import BeautifulSoup
s=requests.Session()

url_login=''
html1=s.get(url_login)
loginsoup=BeautifulSoup(html1.text)

TOKEN=loginsoup.find_all("input")[0]['value']
checkurl=loginsoup.find_all("img")[1]['src']
checkurl="http://mis.rong360.com"+checkurl
path='./yzm.png'
# pic=urllib.urlretrieve(checkurl,path) #下载验证码到桌面
codecs.open(path, mode='wb').write(s.get(checkurl).content)

verifycode= raw_input("输入验证码:")

login_data = {
	'LoginForm[mobile]':'',
	'LoginForm[password]':'',
	'LoginForm[verifyCode]':verifycode.strip(),
	'RONG360_CSRF_TOKEN':TOKEN,
}
url=''
reponse1=s.post(url,data=login_data)
print reponse1.content
