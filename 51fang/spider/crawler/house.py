# -*- coding: utf-8 -*-
# @Time    : 2020/7/5 3:51 下午
# @Author  : stevinwang
from crawler.xiaoqu import get_page_with_db


def get_xiaoqu_page_total(soup):
    return 0


def walk_xaioqu(uri):
    soup = get_xiaoqu_page_total(uri)
    page_total = get_xiaoqu_page_total(soup)
    for i in range(page_total):
        _no = i + 1
        page_uri = ''
