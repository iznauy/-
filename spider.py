import urllib
import urllib2
import re
from bs4 import BeautifulSoup
import time
import numpy as np
import pandas as pd
from pandas import Series, DataFrame
import sys


def get_file_url(name):
    regex = re.compile(r'http://movie.mtime.com/\d+/')
    url_part1 = r'http://service.channel.mtime.com/Search.api?Ajax_CallBack=true&' \
                r'Ajax_CallBackType=Mtime.Channel.Services&Ajax_CallBackMethod=GetSea' \
                r'rchResult&Ajax_CrossDomain=1&Ajax_RequestUrl=http%3A%2F%2Fsearch.mtime.' \
                r'com%2Fsearch%2F%3Fq%3D%25E4%25B8%2589%25E7%2594%259F%25E4%25B8%2589%25E4%2' \
                r'5B8%2596%25E5%258D%2581%25E9%2587%258C%25E6%25A1%2583%25E8%258A%25B1%26t%3D0' \
                r'&t=20178231730424285&Ajax_CallBackArgument0='
    url_part2 = r'&Ajax_CallBackArgument1=0&Ajax_CallBackArgument2' \
                r'=627&Ajax_CallBackArgument3=0&Ajax_CallBackArgument4=1'
    try:
        body = urllib2.urlopen(url_part1 + urllib.quote(name) + url_part2, timeout=3).read()
        strings = regex.findall(body)
        if len(strings) >= 1:
            return regex.findall(body)[0] + 'fullcredits.html'
        else:
            return None
    except Exception as e:
        print 'timeout!'
        return None


def get_info_from_html(html):
    soup = BeautifulSoup(html)
    temp = soup.select('.credits_list')
    divs = {}
    for tap in temp:
        if tap.h4.string == u'编剧 Writer':
            divs['playwright'] = tap
            continue
        elif tap.h4.string == u'制作人 Produced by':
            divs['maker'] = tap
            continue
        elif tap.h4.string == u'摄影 Cinematography':
            divs['photographer'] = tap

    result = {}

    if divs.get('playwright', None) != None:
        editors_names = ''
        for item in divs['playwright'].find_all('a'):
            editors_names += item.string + ' '
        result['playwright'] = editors_names.rstrip()

    if divs.get('maker', None) != None:
        maker_names = ''
        for item in divs['maker'].find_all('a'):
            maker_names += item.string + ' '
        result['maker'] = maker_names.rstrip()

    if divs.get('photographer', None) != None:
        photographer_names = ''
        for item in divs['photographer'].find_all('a'):
            photographer_names += item.string + ' '
        result['photographer'] = photographer_names.rstrip()

    return result


def crawling_data(name_series):
   list1, list2, list3 = [], [], []
   count = 0
   for name in name_series:
       if count > 2:
           time.sleep(count * 35)
       time.sleep(0.5)
       url = get_file_url(name)
       print name
       print url
       if url is None:
           list1.append(None)
           list2.append(None)
           list3.append(None)
           count += 1
       else:
           try:
               result = get_info_from_html(urllib2.urlopen(url, timeout=2))
               list1.append(result.get('playwright', None))
               list2.append(result.get('maker', None))
               list3.append(result.get('photographer', None))
               print 'OK'
               count = 0
           except Exception as e:
              list1.append(None)
              list2.append(None)
              list3.append(None)
              print 'Error, because :' + e.message
              count += 1
   return list1, list2, list3


df = pd.read_csv('films.csv')

if __name__ == 'main':
    df = pd.read_csv('films.csv')
    l1, l2, l3 = crawling_data(df['影片名称'])
    s1, s2, s3 = Series(l1), Series(l2), Series(l3)
    df['playwrights'] = s1
    df['makers'] = s2
    df['photographers'] = s3
    reload(sys)
    sys.setdefaultencoding('utf-8')
    df.to_csv('films.csv')

