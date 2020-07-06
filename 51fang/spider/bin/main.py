# -*- coding: utf-8 -*-
# @Time    : 2020/7/5 10:35 上午
# @Author  : stevinwang

from dao import db
from crawler import xiaoqu
import logging


def configure():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)5s - %(filename)8s:%(lineno)-3s - %(message)s', level=logging.INFO)
    logging.getLogger('peewee').setLevel(logging.WARN)
    db.create_tables()


def xiaoqu_do():
    short_city = 'bj'
    xiaoqu.walk_city_for_xiaoqu(short_city)


def run():
    xiaoqu_do()


if __name__ == '__main__':
    configure()
    run()
