# -*- coding:utf-8 -*-

import re
from bs4 import BeautifulSoup


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
        strong = div.find_all('strong', class_=re.compile("ll rating_num.*?"), property="v:average")
        if len(strong) == 0: return {}
        strong = strong[0]
        average = strong.string.strip()
        spans = div.find_all('span', property="v:votes")
        if len(spans) == 0: return {}
        numRaters = spans[0].string.strip()
        return {
            "max": 10,
            "numRaters": numRaters,
            "average": average,
            "min": 0
        }

    except Exception as e:
        print('get_rating', e)
        return {}

def get_tags(soup):
    try:
        div = soup.find_all('div', id="db-tags-section", class_="blank20")[0]
        tags = []
        for a in div.find_all('a', class_=re.compile('.*?tag')):
            tags.append({
                "count":0,
                "title": a.string.strip(),
                "name": a.string.strip()
            })
        return tags
    except Exception as e:
        print('get_tags', e)
        return []
        
def get_series(sinfo):
    try:
        res = re.findall('<span.*?>丛书.*?</span>.*?<a.*?href="(.+)">(.+)</a>', sinfo)   
        if len(res) > 0:
            id = res[0][0].split('/')[-1]
            name = res[0][1].strip()
            return {
                'id': id,
                'name': name
            }
        return {}
    except Exception as e:
        print('get_series', e)
        return {}

def get_intros(soup):
    try:
        intros = soup.find_all('div', class_='intro')
        if len(intros) > 1:
            summary = intros[0].find_all('p')[0].string.strip()
            author_intro = ' '.join(intros[1].find_all('p')[0].string.strip().split())
            return author_intro, summary
        elif len(intros) == 1:
            intro = intros[0].find_all('p')[0].string.strip()
            h2s = soup.find_all('h2')
            for h2 in h2s:
                spans = h2.find_all('span')
                for span in spans:
                    if span.string == '内容简介':
                        return intro, ''
                    elif span.string == '作者简介':
                        return '', intro
            # failed, 当成作者简介
            return '', intro
        else: return '', ''

    except Exception as e:
        print('get_intros', e)
        return '', ''

def get_catalog(soup):
    try:
        divs = soup.find_all('div', class_="indent", id=re.compile("dir_\\d+_full"), style="display:none")
        if len(divs) > 0:
            div = str(divs[0].text)
            res = div.split('\n')
            res = [i.replace('　', ' ').strip() for i in res]
            res = [i for i in res if i][:-1] # 移除 '· · · · · · (收起)'
            s = '\n'.join(res)
            s += '\n'
            return s
        return ''
    except Exception as e:
        print('get_catalog', e)
        return ''

def parse_book_html_return_json(id, html):
    """根据豆瓣图书HTML解析JSON"""
    soup = BeautifulSoup(html, "html.parser")
    info = soup.find('div', id='info')
    sinfo = str(info)
    
    isbn13 = soup.find_all('meta', property="book:isbn")[0].attrs['content']
    image = soup.find_all('meta', property="og:image")[0].attrs['content']
    # https://img2.doubanio.com/view/subject/l/public/s27264181.jpg
    img_base = image.split('/')[-1]    
    author_intro, summary = get_intros(soup)    

    return {
        "isbn13": isbn13,
        "isbn10" : isbn13[3:],
        "title" : soup.find_all('meta', property="og:title")[0].attrs['content'],
        "origin_title" : re_find('<span.*?>原作名.*?</span>(.+)<br', sinfo)    ,
        "alt_title" : '',
        "subtitle" : re_find('<span.*?>副标题.*?</span>(.+)<br', sinfo)   ,
        "url" : "http://api.douban.com/v2/book/{}".format(id)    ,
        "alt" : "http://book.douban.com/subject/{}/".format(id),
        "image": image,
        "images" : {
            "small": "https://img2.doubanio.com/view/subject/{}/public/{}".format('s', img_base),
            "medium": "https://img2.doubanio.com/view/subject/{}/public/{}".format('m', img_base),
            "large": "https://img2.doubanio.com/view/subject/{}/public/{}".format('l', img_base),
        },
        "author" : [i.attrs['content'] for i in soup.find_all('meta', property="book:author")],
        "translator" : soup_find_span_a(info, re.compile('.*?译者')),
        "publisher" : re_find('<span.*?>出版社.*?</span>(.+)<br', sinfo)    ,
        "pubdate" : re_find('<span.*?>出版年.*?</span>(.+)<br', sinfo)   ,
        "rating" : get_rating(soup),
        "tags" : get_tags(soup),
        "binding" : re_find('<span.*?>装帧.*?</span>(.+)<br', sinfo)   ,
        "price" : re_find('<span.*?>定价.*?</span>(.+)<br', sinfo)   ,
        "series" : get_series(sinfo),
        "pages" : re_find('<span.*?>页数.*?</span>(.+)<br', sinfo)   ,
        "author_intro": author_intro,
        "summary": summary,
        "catalog" : get_catalog(soup)    ,
        "ebook_url" : '',
        "ebook_price" : '',
    }

