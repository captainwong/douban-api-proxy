# -*- coding:utf-8 -*-

from decrypt import decrypt
import requests
import re

if __name__ == '__main__':
    url = 'https://search.douban.com/book/subject_search?search_text={}&cat=1001'.format('解忧杂货店')
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
    }
    resp = requests.get(url=url, headers=headers)
    encrypt_data = re.findall('window.__DATA__ = "(.+?)"', resp.text)[0]
    data = decrypt(encrypt_data)
    print(data)
