# -*- coding:utf-8 -*-

import json
import gevent
import time
from common import logger
from common import db
from common import utils
from bussiness import config
from bussiness import players
from bussiness import encrypt_utils
from bussiness import api

def play(player):
    if player.get_account() and player.get_password():
        # 账号密码登录
        api.api_as_login(player)
    else:
        # auth登录
        api.api_auth(player)
    gevent.sleep(3)

    # 获取token
    api.api_get_token(player)
    gevent.sleep(1)

    # 登录游戏服务器
    api.api_login(player)
    # 同步账号数据
    api.api_sync_data(player)
    # 更新在线状态
    api.api_sync_status(player, 95)
    # 获取未完成订单
    api.api_get_unconfirmed_orderid_list(player)
    gevent.sleep(2)

    # 每日签到
    if player.get_attr()['checkIn']['canCheckIn']:
        api.api_checkin(player)

    # 领取维护补偿
    mail_list = api.api_get_meta_info_list(player)
    for mail in mail_list:
        api.api_recieve_mail(player, mail['mailId'], mail['type'])
        gevent.sleep(1)

    # 活动签到
    if config.CHECKIN_ACTIVITY_ID:
        history = player.get_attr()['activity']['CHECKIN_ONLY'][config.CHECKIN_ACTIVITY_ID]['history']
        for index in range(len(history)):
            if history[index]:
                api.api_activity_checkin(player, config.CHECKIN_ACTIVITY_ID, index)

    # 使用消耗品
    for item_id in player.get_attr()['consumable']:
        for inst_id in player.get_attr()['consumable'][item_id]:
            cnt = player.get_attr()['consumable'][item_id][inst_id]['count']
            if cnt > 0:
               api.api_use_item(player, inst_id, item_id, cnt)

    # 当前角色脚本完成
    player.report_status()
    return

# 协程
def run(player_cnt):
    # 从数据库载入账号数据
    player_list = players.load_player_from_db(player_cnt)
    routine_list = []
    for player in player_list:
        routine_list.append(gevent.spawn(play, player))
    gevent.joinall(routine_list)
    return

if __name__=="__main__":
    run(1)