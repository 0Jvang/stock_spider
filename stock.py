import pdb
import re
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import requests

SMTP_SERVER = 'smtp.office365.com'
SMTP_PORT = 587
SENDER = ''
USER = ''
PASSWORD = ''
RECEIVER = []


def get_market():
    url = 'https://stock.xueqiu.com/v5/stock/realtime/quotec.json?symbol=SH000001,SZ399001&_=1581648987273'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'}

    r = requests.get(url, headers=headers)
    index = {}

    for i in r.json()['data']:
        if i['symbol'].startswith('SH'):
            index_name = '上证指数'
        elif i['symbol'].startswith('SZ'):
            index_name = '深证成指'

        index.update({index_name: {'price_delta': i['chg'], 
                                   'percent_delta': i['percent']}})
    return index

def str2date(string, tmpl='%Y-%m-%d'):
    return datetime.datetime.strptime(string, tmpl)

def get_bond():
    data = []
    url = 'https://www.jisilu.cn/data/cbnew/pre_list/?___jsl=LST___t=1582352185460'
    r = requests.get(url)

    for i in r.json()['rows']:
        cell = i['cell']
        if '申购' in cell['progress_nm']:
            purchase_date = re.search(r'\d{4}-\d{2}-\d{2}', cell['progress_nm']).group()
            if str2date(purchase_date) >= datetime.datetime.now():
                data.append({'代码': cell['bond_id'], '申购日': purchase_date})
    return data

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
    content = ''
    data = get_market()
    for k, v in data.items():
        content += "{}\n涨跌: {}\t\t涨跌百分比: {}\n\n".format(k, v['price_delta'], v['percent_delta'])
    send_email('股票行情', content, RECEIVER)

    data = get_bond()
    if data:
        content = ''
        for i in data:
            for k, v in i.items():
                content += "{}: {}\t\t".format(k, v)
            content += '\n'
    send_email('可转债申购', content, RECEIVER)

main()

