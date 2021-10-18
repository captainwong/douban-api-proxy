# -*- coding:utf-8 -*-

import execjs
import json


with open('decrypt.js', 'r', encoding='utf-8') as f:
    decrypt_js = f.read()
ctx = execjs.compile(decrypt_js)

def decrypt(data):
    """ decrypt douban's window.__DATA__ and return json"""
    dict_ = ctx.call('decrypt', data)
    #s = json.dumps(dict_)
    return dict_

