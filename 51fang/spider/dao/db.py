# -*- coding: utf-8 -*-
# @Time    : 2020/7/5 10:38 上午
# @Author  : stevinwang

from peewee import MySQLDatabase
import settings
from peewee import Model
from peewee import IntegerField, CharField, DateTimeField, TextField
import datetime
import logging
import traceback

db = MySQLDatabase(
    database=settings.DB_NAME,
    host=settings.DB_HOST,
    port=settings.DB_PORT,
    user=settings.DB_USER,
    passwd=settings.DB_PASSWORD,
    charset=settings.DB_CHARSET,
    use_unicode=True,
)


class BaseMdoel(Model):
    uptime = DateTimeField(default=datetime.datetime.now, null=False, verbose_name='该条记录更新时间')
    crtime = DateTimeField(default=datetime.datetime.now, null=False, verbose_name='该条记录创建时间')

    class Meta:
        database = db


class Html(BaseMdoel):
    state = IntegerField(default=0, null=False, verbose_name='状态，0 新增，1 已抓取过')
    uri = CharField(max_length=255, null=False, verbose_name='网页链接', index=True, unique=True)
    html = TextField(default='', null=True, verbose_name='网页原始HTML内容')
    modtime = DateTimeField(default=datetime.datetime.now, null=True, verbose_name='网页更新时间')
    spdtime = DateTimeField(default=datetime.datetime.now, null=True, verbose_name='网页抓取时间')


class Xiaoqu(BaseMdoel):
    uri = CharField(max_length=255, default='', null=False, verbose_name='小区链接', index=True, unique=True)
    name = CharField(max_length=255, default='', null=False, verbose_name='小区名称', index=True, unique=True)
    district = CharField(max_length=255, null=True, verbose_name='行政区名称')
    bizcircle = CharField(max_length=255, null=True, verbose_name='街道名称')
    let_info = CharField(max_length=255, null=True, verbose_name='出租信息')
    let_href = CharField(max_length=255, null=True, verbose_name='出租链接')
    sale_info = CharField(max_length=255, null=True, verbose_name='成交信息')
    sale_href = CharField(max_length=255, null=True, verbose_name='成交链接')
    tags = CharField(max_length=255, null=True, verbose_name='tagList')
    avg_price = IntegerField(null=True, verbose_name='均价')
    state = IntegerField(null=True, default=0, verbose_name='状态，0未抓取，1已抓取')
    xiaoqu_id = CharField(default='0', null=False, verbose_name='小区id', index=True, unique=True)
    sell_num = IntegerField(default=0, null=False, verbose_name='二手房在售', index=True, unique=True)
    sell_href = CharField(max_length=255, null=True, verbose_name='二手房链接')
    # alter table TABLE_NAME convert to character set utf8mb4 collate utf8mb4_bin;


# 小区详细的结构化信息
class XiaoquDetail(BaseMdoel):
    xiaoqu_id = CharField(default='0', null=False, verbose_name='小区id', index=True, unique=True)
    favorite = IntegerField(null=True, default=0, verbose_name='关注人数')
    unit_price = IntegerField(null=True, default=0, verbose_name='单价')
    house_num = IntegerField(null=True, default=0, verbose_name='户数')
    building_num = IntegerField(null=True, default=0, verbose_name='栋数')
    xq_type = CharField(max_length=255, null=True, verbose_name='类型')
    mgr_company = CharField(max_length=255, null=True, verbose_name='物业公司')
    dev_company = CharField(max_length=255, null=True, verbose_name='开发商')
    near = CharField(max_length=255, null=True, verbose_name='福进门店')
    mgr_fee = CharField(default='', null=True, verbose_name='物业费')


# 房屋详细的结构化信息
class HouseInfo(BaseMdoel):
    house_id = CharField(default='0', null=False, verbose_name='house id', index=True, unique=True)


def create_tables():
    if not Html().table_exists():
        db.create_table(Html)
    if not Xiaoqu().table_exists():
        db.create_table(Xiaoqu)
    if not XiaoquDetail().table_exists():
        db.create_table(XiaoquDetail)


def insert_many_xiaoqu(infos):
    if not infos:
        return
    for info in infos:
        try:
            with db.atomic():
                n = Xiaoqu.insert(info).upsert().execute()
        except Exception as e:
            msg = traceback.print_exc()
            logging.error(msg)
            logging.error(info)



def insert_xiaoqu_detail(info):
    if not info:
        return
    try:
        with db.atomic():
            n = XiaoquDetail.insert(info).upsert().execute()
    except Exception as e:
        logging.error(e)
