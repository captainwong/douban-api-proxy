# douban-api-proxy

豆瓣API代理


以解析HTML的方式提供原豆瓣图书的（部分）API，目前有搜索图书，获取图书信息。


搜索结果页面提取 `window.__DATA__` 抄了 `sergiojune` 的 [代码](https://github.com/acdzh/douban-book-api/blob/master/douban/libs/decrypt.js)，感谢！


因为 `exejs` 库未指定编码为 `utf-8` 导致使用了默认编码 `gbk` 解析 `window.__DATA` 时出错，因此修改了一份拷贝在这里。


使用文件缓存访问过的数据，未来做个定期删除。
