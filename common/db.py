# -*- coding:utf-8 -*-
import os
import sqlite3
from common import logger

# sqlite3数据库初始化
def init_db():
    # 建db文件夹
    if not os.path.exists(os.getcwd() + '/db'):
        os.mkdir(os.getcwd() + '/db')
    # 建库
    conn = sqlite3.connect('./db/account.db', check_same_thread = False, isolation_level = None)
    cur = conn.cursor()
    # 建账号表
    cur.execute('''create table if not exists account(uid bigint primary key, create_time timestamp DEFAULT CURRENT_TIMESTAMP, access_token varchar(1024), 
                   account varchar(1024), password varchar(1024), device_id varchar(1024), device_id2 varchar(1024), device_id3 varchar(1024),
                   nickname varchar(1024) DEFAULT "", android_diamond interger DEFAULT 0, diamond_shard interger DEFAULT 0, gold interger DEFAULT 0, ssr_cnt interger DEFAULT 0, 
                   ap interger DEFAULT 0, max_ap interger DEFAULT 0, attr MEDIUMTEXT)''')
    return conn

# 数据库连接
conn_db = init_db()

# 数据库query
def query(sql):
    try:
        cur = conn_db.cursor()
        cur.execute(sql)
        return cur.fetchall()
    except Exception as e:
        logger.e('数据库操作失败: sql:{}, err_msg:{}'.format(sql, str(e)))
    raise RuntimeError('Oops!')





