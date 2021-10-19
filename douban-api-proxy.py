# -*- coding:utf-8 -*-

from flask import Flask, request
from urllib import parse
import requests
import re
from urllib import parse
from decrypt import decrypt
from bs4 import BeautifulSoup

requests.packages.urllib3.disable_warnings()

app = Flask(__name__)
app.debug = False

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
}

def re_find(regex, html):
    res = re.findall(regex, html)
    return res[0].strip() if len(res) > 0 else ''

def soup_find_span_a(soup, span):
    spans = soup.find_all('span', string=span)
    if len(spans) > 0:
        return [ ' '.join(a.string.strip().split()) for a in spans[0].parent.find_all('a')]
    else:
        return []

def get_rating(soup):
    try:
        div = soup.find_all(class_="rating_self clearfix", typeof="v:Rating")[0]
        strong = div.find_all('strong', class_=re.compile("ll rating_num.*?"), property="v:average")[0]
        average = strong.string.strip()
        span = div.find_all('span', property="v:votes")[0]
        numRaters = span.string.strip()
        return {
            "max": 10,
            "numRaters": numRaters,
            "average": average,
            "min": 0
        }

    except Exception as e:
        print(e)
        return {}

def get_tags(soup):
    try:
        div = soup.find_all('div', id="db-tags-section", class_="blank20")[0]
        tags = []
        for a in div.find_all('a', class_=re.compile('.*?tag')):
            tags.append({
                "count":0,
                "name": a.string.strip()
            })
        return tags
    except Exception as e:
        print(e)
        return []
        
def get_series(sinfo):
    try:
        res = re.findall('<span.*?>丛书.*?</span>.*?<a.*?href="(.+)">(.+)</a>', sinfo)   
        id = res[0][0].split('/')[-1]
        name = res[0][1].strip()
        return {
            'id': id,
            'name': name
        }    
    except Exception as e:
        print(e)
        return {}

def get_intros(soup):
    try:
        intros = soup.find_all('div', class_='intro')
        summary = intros[0].find_all('p')[0].string.strip()
        author_intro = ' '.join(intros[1].find_all('p')[0].string.strip().split())
        return author_intro, summary

    except Exception as e:
        print(e)
        return '', ''


def parse_book_html_return_json(id, html):
    """根据豆瓣图书HTML解析JSON"""
    soup = BeautifulSoup(html, "html.parser")
    info = soup.find('div', id='info')
    sinfo = str(info)
    isbn13 = soup.find_all('meta', property="book:isbn")[0].attrs['content']
    isbn10 = isbn13[3:]    
    title = soup.find_all('meta', property="og:title")[0].attrs['content']
    origin_title = re_find('<span.*?>原作名.*?</span>(.+)<br', sinfo)    
    alt_title = ''
    subtitle = ''
    url = "http://api.douban.com/v2/book/{}".format(id)    
    alt = "http://book.douban.com/subject/{}/".format(id)
    image = soup.find_all('meta', property="og:image")[0].attrs['content']
    # https://img2.doubanio.com/view/subject/l/public/s27264181.jpg
    img_base = image.split('/')[-1]
    images = {
        "small": "https://img2.doubanio.com/view/subject/{}/public/{}".format('s', img_base),
        "medium": "https://img2.doubanio.com/view/subject/{}/public/{}".format('m', img_base),
        "large": "https://img2.doubanio.com/view/subject/{}/public/{}".format('l', img_base),
    }
    author = [i.attrs['content'] for i in soup.find_all('meta', property="book:author")]
    translator = soup_find_span_a(info, re.compile('.*?译者'))
    publisher = re_find('<span.*?>出版社.*?</span>(.+)<br', sinfo)    
    pubdate = re_find('<span.*?>出版年.*?</span>(.+)<br', sinfo)   
    rating = get_rating(soup)
    tags = get_tags(soup)
    binding = re_find('<span.*?>装帧.*?</span>(.+)<br', sinfo)   
    price = re_find('<span.*?>定价.*?</span>(.+)<br', sinfo)   
    series = get_series(sinfo)
    pages = re_find('<span.*?>页数.*?</span>(.+)<br', sinfo)   
    author_intro, summary = get_intros(soup)

    pass

def get_book_info(id):
    """访问豆瓣图书获取HTML并解析出JSON"""
    url = "https://book.douban.com/subject/" + str(id)
    try:
        res = requests.get(url, headers = headers)
        data = parse_book_html_return_json(res.content)
        return data
    except Exception as e:
        print(e)
        return False


@app.route('/v2/book/search', methods=['GET'])
def search():
    try:
        q = parse.unquote(request.args.get("q"))
        url = 'https://search.douban.com/book/subject_search?search_text={}&cat=1001'.format(q)       
        resp = requests.get(url=url, headers=headers)
        encrypt_data = re.findall('window.__DATA__ = "(.+?)"', resp.text)[0]
        data = decrypt(encrypt_data)
        ids = [str(item["id"]) for item in data["payload"]["items"]]

    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }
    


if __name__ == '__main__':
    #html = r'<span class="pl">原作名:</span> Code Complete<br />'
    #origin_title = re_find(r'<span.*?>原作名.*?</span>(.+?)<br', html)
    #html = r''
    #origin_title = re_find(r'<span class="pl">原作名\:<\/span>(.+?)<br\/>', html)
    with open('代码大全.html', 'r', encoding='utf-8') as f:
        #origin_title = re_find('<span.*?>原作名.*?</span>(.+?)<br', f.read())
        parse_book_html_return_json('1477390', f.read())

    #app.run(host='0.0.0.0', port=8085)
