import pdb
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pprint import pprint
import datetime
from collections import namedtuple

import requests
from lxml import etree

stocks = [
    ['重庆水务', 'SH601158', 5.25, True, False],
    ['长江电力', 'SH600900', 17, True, True],
    ['中国石化', 'SH600028', 4.665, False, True],
    ['工商银行', 'SH601398', 5.35, True, False],
    ['农业银行', 'SH601288', 3.37, True, False],
    ['建设银行', 'SH601939', 6.6, True, False],
    ['民生银行', 'SH600016', 5.75, True, False],
    ['交通银行', 'SH601328', 5.2, True, False],
    ['北京银行', 'SH601169', 5.15, True, False],
    ['中国银行', 'SH601988', 3.45, True, False],
    ['浦发银行', 'SH600000', 10.75, True, False],
]

Stock = namedtuple('Stock', ['name', 'code', 'warn_price', 'low_warn', 'high_warn'])

SMTP_SERVER = 'smtp.office365.com'
SMTP_PORT = 587
SENDER = ''
USER = ''
PASSWORD = ''
RECEIVER = []

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
    'Cookie': 's=bk12cb3pqf; device_id=66a0754479b3f10841d88fec40201458; xq_token_expire=Fri%20Feb%2028%202020%2009%3A14%3A04%20GMT%2B0800%20(China%20Standard%20Time); bid=b0a8d8e5cc7bf579e1ea43cfd0a85c52_k65s5c7u; cookiesu=981581649264259; Hm_lvt_1db88642e346389874251b5a1eded6e3=1581648676,1582296223,1582714582,1582769615; xq_a_token=7543573d63139e5c2726484b443fd8db99d1a452; xqat=7543573d63139e5c2726484b443fd8db99d1a452; xq_r_token=b589df04962f6c2b72e9b2b779c1823571021b08; xq_id_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOjEyNjA4ODY2MzEsImlzcyI6InVjIiwiZXhwIjoxNTgzMjg0NDQ0LCJjdG0iOjE1ODI3NzA2ODkzNzUsImNpZCI6ImQ5ZDBuNEFadXAifQ.Q1KBUahNXaeys81JjvGcIF-ynUlccr7r8QwFH0BHdq6KSTgI2G4OK_vAgOdNLg-JjaqXeIwBbbH7qOPAwcHPFURdYWHrl3N5_uykaNZtP-jhF3DK4hQasu4eBgiHZpZ6dosIJ6y3OROOgxCSn30_UihNSEI05FSQsWJUgDY4ElUqo-Clvh8n6UErYifvK9ug9r1oby1-h2-899jLiy3rZShI3hG_9usGtr3dX4H9_kWyXBK6QqBUIOv7QDx21FPsq_HQdzDLT56QiLpRBgJPlQHau6U2U3f06i0O6KGBrD6IQFuRhkB2uV7uIwVhc3ByDu8-HsS86jSZdJ7zeWDfmQ; xq_is_login=1; u=1260886631; snbim_minify=true; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1582774882'
}

def get(code):
    url = 'https://stock.xueqiu.com/v5/stock/batch/quote.json?symbol={}'.format(code)
    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        return 0
    return r.json()['data']['items'][0]['quote']['current']

def send_email(subject, content, receiver):
    msgroot = MIMEMultipart('related')
    msgroot['to'] = ','.join(receiver) if isinstance(receiver, list) else receiver
    msgroot['Subject'] = subject
    msgroot.attach(MIMEText(content))

    smtp = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    smtp.ehlo()
    smtp.starttls()
    smtp.login(USER, PASSWORD)
    smtp.sendmail(SENDER, receiver, msgroot.as_string())
    smtp.quit()

def main():
    for i in stocks:
        stock = Stock(*i)
        price = get(stock.code)
        print(stock.name, price, stock.warn_price)

        if price <= stock.warn_price and stock.low_warn:
            send_email('股票低价', '{}, {}'.format(stock.name, price), RECEIVER)
            print('low_warn')

        if price >= (stock.warn_price * 1.03) and stock.high_warn:
            send_email('股票高价', '{}, {}'.format(stock.name, price), RECEIVER)
            print('high_warn')

main()
