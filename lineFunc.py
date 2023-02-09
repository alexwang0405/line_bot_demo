# -*- coding: utf-8 -*-
"""
linebot's function
"""

import requests
from bs4 import BeautifulSoup
import json, re, datetime, pytz
from geopy.distance import geodesic

# 外幣利率
def getRate():
    url='https://www.esunbank.com.tw/bank/personal/deposit/rate/forex/foreign-exchange-rates'
    header = {'user-agent': 'Googlebot'}
    content = requests.get(url, headers = header).text
    soup = BeautifulSoup(content, 'html.parser')
    rateData = soup.find_all('tr', class_='tableContent-light')
    
    moneyName=[]
    moneyBuy=[]
    moneySell=[]
    reply='幣別'+ ' '*13 +'即期買人'+' '*10+'即期賣出\n'
    
    for item in rateData:
        moneyName.append(item.find('td', class_='itemTtitle').text)
        moneyBuy.append(item.find('td', class_='odd').text)
        moneySell.append(item.find('td', class_='even').text)
    
    for i in range(5):
        reply = reply + moneyName[i] + ' '*2 + moneyBuy[i] + ' '*13 + moneySell[i] + '\n'
        
    return reply

# 空氣品質
def getAQI():
    url='http://opendata.epa.gov.tw/webapi/Data/REWIQA/?$orderby=SiteName&$skip=0&$top=1000&format=json'
    content=requests.get(url).text
    data=json.loads(content)
    reply = {}
    for row in data:
        reply[row['SiteName']] = row['Status']
    return reply
            
# 鄧紫棋圖片
def getImg():
    url = 'https://i.pinimg.com/originals/15/96/0e/15960ea9bf6f4ac20797b1e2951cef2e.jpg'
    return url

# 使用定位抓取最近五個站空氣品質
def getAQIByLocation(latitude, longitude):
    url='http://opendata.epa.gov.tw/webapi/Data/REWIQA/?$orderby=SiteName&$skip=0&$top=1000&format=json'
    air = requests.get(url).text
    airData = json.loads(air)
    
    for d in airData:
        d['Dest'] = geodesic((latitude, longitude),(d['Latitude'], d['Longitude'])).miles
    airData.sort(key=lambda x:x['Dest'])
    
    message='距離最近的五個站的狀態：\n'
    for i in range(5):
        message = message + airData[i]['SiteName'] + ': ' + airData[i]['Status'] +'\n'
        
    return message

# 取得目前時間的節目表
def getTV():
    url = 'http://www.niotv.com/i_index.php?cont=day&grp_id=4&sch_id=57&way=outter'

    channel = {'衛視電影': 55, '東森電影': 56, '緯來電影': 57, 'HBO': 46, '東森洋片': 48, 'FOX_Movies': 47}

    # 取得所有電影頻道和id
    # response = requests.get(url)
    # response.encoding = 'utf-8'
    # # print(response.text)
    # all_channel = re.findall(r'<form action="" method=post>(.*?)</form>', response.text.replace('\n', ''))
    # for ac in all_channel:
    #     if 'sch_id' not in ac: continue
    #     cid = re.findall(r'<input type=hidden name=sch_id value=(\d+)>', ac)[0]
    #     cname = re.findall(r'<input type=hidden name=ch_name value=(.*?)>', ac)[0]
    #     print(cid, cname)
    taiwan = pytz.timezone('asia/taipei')  # 指定時區
    today = datetime.datetime.now(taiwan).strftime('%Y-%m-%d')  # 日期
    moment = datetime.datetime.now(taiwan).strftime('%H%M')  # 時間
    message = ''
    for ch in channel:
        ck = 0
        message += ch+':\n'
        data = {
            'act': 'select',
            'sch_id': channel[ch],
            'ch_name': ch,
            'day': today,
            'grp_id': 4,
            'cont': 'day',
        }
        response = requests.post(url, data=data)
        response.encoding = 'utf-8'
        # print(response.text)

        all_time = re.findall(r'<td class=epg_tab_tm>(.*?)</td>', response.text)
        all_tv = re.findall(r'<td>.*?target=_blank>(.*?)</a></td>', response.text)

        for t, v in zip(all_time, all_tv):
            start = ''.join(t.split('~')[0].split(':'))  # 節目開始時間
            end = ''.join(t.split('~')[1].split(':'))  # 節目結束時間
            if int(moment) < int(end):
                ck = 1
            if ck == 1:
                message += '{} {}\n'.format(t, v)
        message += '\n'
    return message