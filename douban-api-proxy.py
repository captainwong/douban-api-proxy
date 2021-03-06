# -*- coding:utf-8 -*-

from flask import Flask, request, jsonify
from flask_cors import CORS
from urllib import parse
import requests
import re
from decrypt import decrypt
from cache import cache
from parse import parse_book_html_return_json
import json

requests.packages.urllib3.disable_warnings()

app = Flask(__name__)
CORS(app, resources=r'/*')
app.debug = False

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36'
}

gcache = cache('.cache')


def get_book_info(id):
    """访问豆瓣图书获取HTML并解析出JSON"""
    data = gcache.get_cached_book_info(id)
    if data: return data

    html = gcache.get_cached_book_html(id)
    if html:
        data = parse_book_html_return_json(id, html)
        gcache.cache_book_info(id, data)
        return data

    url = "https://book.douban.com/subject/" + str(id)
    try:
        res = requests.get(url, headers = headers)
        if res.status_code == 200:
            gcache.cache_book_html(id, res.text)
            data = parse_book_html_return_json(id, res.content)
            gcache.cache_book_info(id, data)
            return data
        return False
    except Exception as e:
        print('get_book_info', e)
        return False


@app.route('/v2/book/<id>', methods=['GET'])
def get(id):
    """获取图书信息"""
    try:
        info = get_book_info(id)
        info["success"] = True
        info["message"] = "success"
        return info
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }


@app.route('/v2/book/search', methods=['GET'])
def search():
    """搜索图书"""
    try:
        q = parse.unquote(request.args.get("q"))
        callback = request.args.get('callback')
        ids = gcache.get_cached_search_result_ids(q)
        if not ids:
            url = 'https://search.douban.com/book/subject_search?search_text={}&cat=1001'.format(q)       
            resp = requests.get(url=url, headers=headers)
            encrypt_data = re.findall('window.__DATA__ = "(.+?)"', resp.text)[0]
            data = decrypt(encrypt_data)
            ids = [str(item["id"]) for item in data["payload"]["items"]]
            gcache.cache_search_result_ids(q, ids)

        books = []
        for id in ids:
            book = get_book_info(id)
            if book:
                books.append(book)

        data = {
            "success": True,
            "message": "success",
            "start": 0,
            "count": len(books),
            "total": len(books),
            "books": books
        }

        if callback:
            response = callback + '(' + json.dumps(data) + ')'
        else:
            response = jsonify(data)      
        return response

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
    # with open('代码大全.html', 'r', encoding='utf-8') as f:
    #     #origin_title = re_find('<span.*?>原作名.*?</span>(.+?)<br', f.read())
    #     data = parse_book_html_return_json('1477390', f.read())
    #     data =json.dumps(data)
    #     print(data)

    app.run(host='0.0.0.0', port=8085)
