# -*- coding:utf-8 -*-

import os
import json
import hashlib

def hash_q(q):
    return hashlib.md5(q.encode('utf-8')).hexdigest()

class cache:

    def __init__(self, cache_dir = '.cache'):
        self.cache_dir_ = cache_dir
        self.cache_dir_book_ = os.path.join(cache_dir, 'book')
        self.cache_dir_search_ = os.path.join(cache_dir, 'search')
        os.makedirs(self.cache_dir_book_, exist_ok=True)
        os.makedirs(self.cache_dir_search_, exist_ok=True)

    def cache_book_info(self, id, data):
        path = os.path.join(self.cache_dir_book_, str(id) + ".json")
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def get_cached_book_info(self, id):
        path = os.path.join(self.cache_dir_book_, str(id) + ".json")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                d = f.read()
                j = json.loads(d)
                return j
        except Exception as e:
            print('get_cacked_book_info', e)
        return False

    def cache_book_html(self, id, html):
        path = os.path.join(self.cache_dir_book_, str(id) + ".html")
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)

    def get_cached_book_html(self, id):
        path = os.path.join(self.cache_dir_book_, str(id) + ".html")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                d = f.read()
                return d
        except Exception as e:
            print('get_cacked_book_html', e)
        return False


    def cache_search_result_ids(self, q, ids):
        q = hash_q(q)
        path = os.path.join(self.cache_dir_search_, q + ".json")
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(ids, f, ensure_ascii=False, indent=4)

    def get_cached_search_result_ids(self, q):
        pass


