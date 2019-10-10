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

def play():
    # 新建玩家
    player = players.Player(config.get_random_device_id())
    time.sleep(0.5)

    # 注册账号
    api.api_guest_login(player)
    gevent.sleep(1)

    # auth登录
    api.api_auth(player)
    gevent.sleep(5)
    
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

    # 设置昵称
    api.api_bind_nickname(player, config.get_random_nickname())
    gevent.sleep(1)

    # 进入教程01副本
    battle_id = api.api_battle_start(player, 'guide_01')
    # 计算本次副本持续时间
    battle_start_time = utils.get_local_time()
    battle_finish_time = config.get_random_battle_finish_time(battle_start_time)
    logger.i('本次副本持续时间: {}秒'.format(battle_finish_time - battle_start_time))
    # 等待战斗结束
    gevent.sleep(battle_finish_time - battle_start_time)

    # 战斗日志
    battle_data = json.loads(utils.read_buf_from_file('gamedata/battle_log/guide_01.json'))
    # 教程01副本通关
    api.api_battle_finish(player, battle_id, battle_start_time, battle_data)
    gevent.sleep(1)

    # 进入教程02副本
    battle_id = api.api_battle_start(player, 'guide_02')
    battle_start_time = utils.get_local_time()
    battle_finish_time = config.get_random_battle_finish_time(battle_start_time)
    logger.i('本次副本持续时间: {}秒'.format(battle_finish_time - battle_start_time))
    # 等待战斗结束
    gevent.sleep(battle_finish_time - battle_start_time)

    # 战斗日志
    battle_data = json.loads(utils.read_buf_from_file('gamedata/battle_log/guide_02.json'))
    # 教程02副本通关
    api.api_battle_finish(player, battle_id, battle_start_time, battle_data)
    gevent.sleep(1)

    # 更新在线状态
    api.api_sync_status(player, 95)
    # 提交剧情
    api.api_finish_story(player, 'obt/guide/l0-0/0_home_ui')
    gevent.sleep(1)

    # 同步卡池
    api.api_sync_normal_gacha(player)
    # 单抽
    api.api_advancedGacha(player, 'BOOT_0_1_1', 0)
    gevent.sleep(5)

    # 提交剧情
    api.api_finish_story(player, 'obt/guide/l0-0/1_recruit_adv')
    gevent.sleep(1)

    # 更新编队0信息
    squad_id = '0'
    slots = player.get_attr()['troop']['squads'][squad_id]['slots']
    slots[4] = {"charInstId": 5, "skillIndex": 0}
    api.api_squad_formation(player, squad_id, slots)
    # 提交剧情
    api.api_finish_story(player, 'obt/guide/l0-0/2_make_squad')
    gevent.sleep(1)

    # 进入主线main_00-01副本
    squad = player.get_attr()['troop']['squads']['0']
    battle_id = api.api_battle_start(player, 'main_00-01', json.dumps(squad, ensure_ascii = False))
    gevent.sleep(2)

    # 提交剧情
    api.api_finish_story(player, 'obt/guide/l0-0/3_battle_ui')
    gevent.sleep(2)
    api.api_finish_story(player, 'obt/main/level_main_00-01_beg')
    gevent.sleep(2)

    # 等待战斗结束
    battle_start_time = utils.get_local_time()
    battle_finish_time = config.get_random_battle_finish_time(battle_start_time)
    logger.i('本次副本持续时间: {}秒'.format(battle_finish_time - battle_start_time))
    gevent.sleep(battle_finish_time - battle_start_time) 

    # 战斗日志
    battle_data = json.loads(utils.read_buf_from_file('gamedata/battle_log/main_00-01.json'))
    # 主线main_00-01副本通关
    api.api_battle_finish(player, battle_id, battle_start_time, battle_data)
    gevent.sleep(2)

    # 提交剧情
    api.api_finish_story(player, 'obt/main/level_main_00-01_end')
    gevent.sleep(2)
    # 更新在线状态
    api.api_sync_status(player, 95)

    # 提交任务
    api.api_confirm_mission(player, 'main_1')
    gevent.sleep(2)
    # 提交剧情
    api.api_finish_story(player, 'obt/guide/l0-1/0_mission_main')
    gevent.sleep(2)

    # 每日签到
    if player.get_attr()['checkIn']['canCheckIn']:
        api.api_checkin(player)
    
    # 领取新手礼包
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
    gevent.joinall([gevent.spawn(play) for i in range(player_cnt)])
    return

if __name__=="__main__":
    run(1)