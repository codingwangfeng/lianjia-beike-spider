# -*- coding: utf-8 -*-
# @Time    : 2020/7/5 10:45 上午
# @Author  : stevinwang
from crawler import misc
from datetime import datetime
from dao.db import Html
import logging
from bs4 import BeautifulSoup
import json
from dao import db
import time

PARSER = 'lxml'

INFO_MAP = {
    '建筑类型': 'xq_type',
    '物业费用': 'mgr_fee',
    '物业公司': 'mgr_company',
    '开发商': 'dev_company',
    '楼栋总数': 'building_num',
    '房屋总数': 'house_num',
    '附近门店': 'near',
}


def get_all_district(html):
    soup = BeautifulSoup(html, PARSER)
    districts_div = soup.find('div', {'data-role': 'ershoufang'})
    ret = {}
    for a in districts_div.div.find_all('a'):
        href = a['href']
        name = a.text
        ret[name] = href
    return ret


def get_page_with_db(uri):
    for i in range(3):
        active = Html.select().where(Html.uri == uri)
        try:
            h = active.get()
            logging.debug("%s from db", uri)
        except Html.DoesNotExist:
            h = None
        if h is None:
            http_rsp = misc.http_GET(uri)
            logging.debug("%s from http", uri)
            if http_rsp.status_code == 200:
                h = Html()
                h.html = http_rsp.content
                h.uri = uri
                h.crtime = datetime.now()
                n = h.save()
                logging.debug("save %s", n)
            else:
                logging.error(http_rsp.status_code, uri)
        if h is not None:
            return h.html
        else:
            time.sleep(1)
    return None


def parse_total_page(soup):
    try:
        page_info = soup.find('div', {'class': 'page-box house-lst-page-box'})
    except AttributeError as e:
        page_info = None

    if page_info is None:
        return 50
    page_info_str = page_info.get('page-data')
    js = json.loads(page_info_str)
    return js['totalPage']


def xq_details(xqs):
    for xq in xqs:
        info = xiaoqu_detail(xq['uri'])
        info['xiaoqu_id'] = xq['xiaoqu_id']
        db.insert_xiaoqu_detail(info)


def xiaoqu_detail(uri):
    info = {}
    htmltext = get_page_with_db(uri)
    soup = BeautifulSoup(htmltext, PARSER)

    # fav
    fav = soup.find('span', {'id': 'favCount'})
    try:
        info['favorite'] = int(fav.text)
    except:
        info['favorite'] = 0
        pass
    # uni price
    try:
        price = soup.find('span', {'class': 'xiaoquUnitPrice'})
        info['unit_price'] = int(price.text)
    except:
        info['unit_price'] = 0
        pass

    # xiaoquInfoItem
    try:
        info_items = soup.find_all('div', {'class': 'xiaoquInfoItem'})
        for item in info_items:
            spans = item.find_all('span')
            key = INFO_MAP[spans[0].text]
            value = spans[1].text.strip().replace('元/平米/月', '').replace('栋', '').replace('户', '')
            if key in ('building_num', 'house_num'):
                value = int(value)
            info[key] = value
    except:
        pass
    return info


def walk_xiaoqu(uri):
    htmltext = get_page_with_db(uri)
    if htmltext is None:
        return None
    soup = BeautifulSoup(htmltext, PARSER)
    items = soup.find_all('li', {'class': 'clear xiaoquListItem CLICKDATA'})
    xiaoqus = []
    for item in items:
        info = {}
        info['xiaoqu_id'] = item['data-housecode']
        a = item.find('a', {'class': 'img maidian-detail'})
        # href
        info['uri'] = a['href']
        info['name'] = a['title']
        r = get_page_with_db(info['uri'])
        if r is None:
            logging.debug('%s empty', uri)
        # 小区出租、成交数据
        house_info = item.find('div', {'class': 'houseInfo'})
        aa = house_info.find_all('a')
        for a in aa:
            if a.text.find('出租') > -1:
                info['let_info'] = a.text
                info['let_href'] = a['href']
            if a.text.find('成交') > -1:
                info['sale_info'] = a.text
                info['sale_href'] = a['href']
        # 位置信息
        positionInfo = item.find('div', {'class': 'positionInfo'})
        district_a = positionInfo.find('a', {'class': 'district'})
        bizcircle_a = positionInfo.find('a', {'class': 'bizcircle'})
        info['district'] = district_a.text
        info['bizcircle'] = bizcircle_a.text

        # 标签
        tagList = item.find('div', {'class': 'tagList'})
        info['tags'] = tagList.text.strip()

        # 均价
        price = item.find('div', {'class': 'totalPrice'})
        try:
            info['avg_price'] = int(price.span.text)
        except:
            info['avg_price'] = 0
            pass

        # 在售
        sell = item.find('a', {'class': 'totalSellCount'})
        info['sell_num'] = sell.span.text
        info['sell_href'] = sell['href']
        xiaoqus.append(info)
    return xiaoqus


def walk_district(district_url):
    htmltext = get_page_with_db(district_url)
    soup = BeautifulSoup(htmltext, PARSER)
    total_page = parse_total_page(soup)
    for i in range(total_page):
        page_id = i + 1
        page_uri = '%spg%s' % (district_url, page_id)
        logging.info('district=%s, page=%s', district_url, page_id)
        xqs = walk_xiaoqu(page_uri)
        db.insert_many_xiaoqu(xqs)
        xq_details(xqs)


def walk_city_for_xiaoqu(short_city):
    uri = 'http://%s.ke.com/xiaoqu' % short_city
    print(uri)
    html_content = get_page_with_db(uri)
    districts = get_all_district(html_content)
    for name, href in districts.items():
        if name in ('东城', '西城'):
            continue
        district_url = 'https://%s.ke.com%s' % (short_city, href)
        walk_district(district_url)
