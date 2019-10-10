# -*- coding:utf-8 -*-
import json
from common import logger
from common import db
from common import utils
from bussiness import config
from bussiness import players
from bussiness import encrypt_utils


# 程序异常
def panic(msg):
    logger.e(msg)
    raise RuntimeError('Oops!')

# 注册账号
def api_guest_login(player):
    sign = encrypt_utils.u8_sign(encrypt_utils.GUEST_LOGIN_SIGN_STR.format(player.get_device_id()))
    data = '{{"deviceId":"{}","sign":"{}"}}'.format(player.get_device_id(), sign)
    res = utils.post_to_as('/user/guestLogin', data)
    code = int(res['result'])
    if code:
        panic('账号注册失败: data={}, err_code={}'.format(data, code))
    player.set_channel_uid(res['uid'])
    player.set_access_token(res['token'])
    logger.i('账号注册成功: deviceId:{}, channel_uid:{}, access_token:{}'.format(player.get_device_id(), res['uid'], res['token']))
    # 返回新注册账号的信息
    return res

# 账号密码登录login server
def api_as_login(player):
    sign = encrypt_utils.u8_sign(encrypt_utils.LOGIN_SIGN_STR.format(
        player.get_account(), player.get_device_id(), player.get_password(), config.PLATFORM))
    data = '{{"account":"{}","password":"{}","deviceId":"{}","platform":{},"sign":"{}"}}'.format(
        player.get_account(), player.get_password(), player.get_device_id(), config.PLATFORM, sign)
    res = utils.post_to_as('/user/login', data)
    code = int(res['result'])
    if code:
        panic('账号密码登录失败: data={}, err_code={}'.format(data, code))
    player.set_channel_uid(res['uid'])
    player.set_access_token(res['token'])
    logger.i('账号密码登录成功: 账号:{}, 密码:{}, deviceId:{}, channel_uid:{}, access_token:{}'.format(
        player.get_account(), player.get_password(), player.get_device_id(), res['uid'], res['token']))
    return

# 游客账号绑定手机
def api_upgrade_guest_user(player_guest, player_new):
    sign = encrypt_utils.u8_sign(encrypt_utils.GUEST_UPGRADE_STR.format(
        player_new.get_device_id(), player_guest.get_device_id2(), player_guest.get_device_id3(), 
        player_guest.get_channel_uid(), player_guest.get_access_token(), 
        player_new.get_channel_uid(), player_new.get_access_token(), 
        config.PLATFORM, player_guest.get_uid()))
    data = '''{{"uid":"{}","extension1":"{{\\"uid\\":\\"{}\\",\\"access_token\\":\\"{}\\"}}","extension2":"{{\\"uid\\":\\"{}\\",\\"access_token\\":\\"{}\\"}}","platform":{},"deviceId":"{}","deviceId2":"{}","deviceId3":"{}","sign":"{}"}}'''.format(
        player_guest.get_uid(),
        player_guest.get_channel_uid(), player_guest.get_access_token(), 
        player_new.get_channel_uid(), player_new.get_access_token(), 
        config.PLATFORM, 
        player_new.get_device_id(), player_guest.get_device_id2(), player_guest.get_device_id3(), 
        sign)
    res = utils.post_to_as('/u8/user/upgradeGuestUser', data)
    code = int(res['result'])
    if code:
        panic('游客账号绑定失败: data={}, err_code={}'.format(data, code))
    player_guest.set_account(player_new.get_account())
    player_guest.set_password(player_new.get_password())
    logger.i('游客账号绑定成功: 账号:{}, 密码:{}, uid:{}'.format(
        player_guest.get_account(), player_guest.get_password(), player_guest.get_uid()))
    return

# auth登录
def api_auth(player):
    sign = encrypt_utils.u8_sign(encrypt_utils.AUTH_SIGN_STR.format(player.get_access_token()))
    data = '{{"token":"{}","sign":"{}"}}'.format(player.get_access_token(), sign)
    res = utils.post_to_as('/user/auth', data)
    player.set_channel_uid(res['uid'])
    logger.i('auth登录成功: channel_uid:{}'.format(res['uid']))
    return

# 获取token
def api_get_token(player):
    sign = encrypt_utils.u8_sign(encrypt_utils.GET_TOKEN_SIGN_STR.format(config.APP_ID, config.CHANNEL_ID, player.get_device_id(), player.get_device_id2(), player.get_device_id3(), player.get_channel_uid(), player.get_access_token(), config.PLATFORM, config.SUB_CHANNEL, config.WORLD_ID))
    data = '''{{"appId":"{}","channelId":"{}","extension":"{{\\"uid\\":\\"{}\\",\\"access_token\\":\\"{}\\"}}","worldId":"{}","platform":{},"subChannel":"{}","deviceId":"{}","deviceId2":"{}","deviceId3":"{}","sign":"{}"}}'''.format(
        config.APP_ID, config.CHANNEL_ID, player.get_channel_uid(), player.get_access_token(), config.WORLD_ID, config.PLATFORM, config.SUB_CHANNEL, player.get_device_id(), player.get_device_id2(), player.get_device_id3(), sign)
    res = utils.post_to_as('/u8/user/getToken', data) 
    code = int(res['result'])
    if code:
        panic('获取token失败: data={}, err_code={}'.format(data, code))
    player.set_uid(res['uid'])
    player.set_token(res['token'])
    player.save_account_info()
    logger.i('获取token成功: uid:{}, channel_uid:{}, token:{}'.format(res['uid'], res['channelUid'], res['token']))
    return res

# 获取客户端最新版本号
def api_get_version():
    res = {"resVersion": "19-09-24-12-06-01-04fffa",	"clientVersion": "0.7.52"}
    logger.i('获取客户端版本号成功: resVersion:{}, clientVersion:{}'.format(res['resVersion'], res['clientVersion']))
    return res['resVersion'], res['clientVersion']

# 客户端最新版本号
RES_VERSION, CLIENT_VERSION = api_get_version()

# game server登录
def api_login(player):
    if not RES_VERSION or not CLIENT_VERSION:
        panic('获取客户端版本号失败!')
    data = '''{{"networkVersion":"{}","uid":"{}","token":"{}","assetsVersion":"{}","clientVersion":"{}","platform":{},"deviceId":"{}","deviceId2":"{}","deviceId3":"{}"}}'''.format(
        config.NETWORK_VERSION, player.get_uid(), player.get_token(), RES_VERSION, CLIENT_VERSION, config.PLATFORM, player.get_device_id(), player.get_device_id2(), player.get_device_id3())
    res = utils.post_to_gs('/account/login', data, player)
    code = int(res['result']) 
    if code:
        panic('登录失败: data={}, err_code={}'.format(data, code))  
    player.set_secret(res['secret'])
    logger.i('账号登录成功: uid={}, secret={}'.format(player.get_uid(), player.get_secret()))
    return player.get_secret()

# 同步账号数据
def api_sync_data(player):
    data = '{"platform":1}'
    res = utils.post_to_gs('/account/syncData', data, player)
    logger.i('数据同步成功: uid:{}, 服务器时间:{}'.format(player.get_uid(), res['ts']))
    # 本地时间校正
    utils.set_time_diff(res['ts'])
    # 记录玩家上线时间
    player.set_login_time(res['user']['event']['status'])
    # 保存玩家游戏数据
    player.update_attr(res['user'])
    logger.i('登陆时间戳已保存: uid:{}, login_time:{}'.format(player.get_uid(), player.get_login_time()))
    return res

# 状态更新
def api_sync_status(player, modules):
    data = '{{"modules":{},"params":{{"16":{{"goodIdMap":{{"LS":[],"HS":[],"ES":[],"CASH":[],"GP":["GP_Once_1"],"SOCIAL":[]}}}}}}}}'.format(modules)
    res = utils.post_to_gs('/account/syncStatus', data, player)
    # 游戏数据差量更新
    player.update_attr(res['playerDataDelta']['modified'])
    logger.i('状态同步成功: uid:{}, 更新账号上线时间:{}'.format(player.get_uid(), res['ts']))
    return

# 获取未完成订单
def api_get_unconfirmed_orderid_list(player):
    data = '{}'
    utils.post_to_gs('/pay/getUnconfirmedOrderIdList', data, player)
    logger.i('获取未完成订单成功: uid:{}'.format(player.get_uid()))
    return

# 设置昵称
def api_bind_nickname(player, nickname):
    data = '{{"nickName":"{}"}}'.format(nickname)
    res = utils.post_to_gs('/user/bindNickName', data, player)
    code = int(res['result']) 
    if code:
        panic('设置昵称失败: data={}, err_code={}'.format(data, code))
    # 游戏数据差量更新
    player.update_attr(res['playerDataDelta']['modified'])
    logger.i('昵称设置成功: uid:{}, 昵称:{}'.format(player.get_uid(), nickname))
    return

# 进入副本
def api_battle_start(player, stage_id, squad = 'null', is_weekly_copy = False):
    cgi = '/quest/battleStart' if not is_weekly_copy else '/campaign/battleStart'
    # 不演习/不求助好友/不自动战斗
    use_practice_ticket = 0
    assist_friend = 'null'
    is_replay = 0
    data = '''{{"usePracticeTicket":{},"stageId":"{}","squad":{},"assistFriend":{},"isReplay":{},"startTs":{}}}'''.format(
        use_practice_ticket, stage_id, squad, assist_friend, is_replay, utils.get_local_time())
    res = utils.post_to_gs(cgi, data, player)    
    code = int(res['result']) 
    if code:
        panic('进入副本失败: data={}, err_code={}'.format(data, code))
    battle_id = res['battleId']
    # 游戏数据差量更新
    player.update_attr(res['playerDataDelta']['modified'])
    logger.i('进入副本成功: uid:{}, 副本id:{}, battle_id:{}'.format(player.get_uid(), stage_id, battle_id))
    return battle_id

# 副本通关
def api_battle_finish(player, battle_id, battle_start_time, battle_data, is_weekly_copy = False):
    cgi = '/quest/battleFinish' if not is_weekly_copy else '/campaign/battleFinish'
    # 校正battle_data数据
    battle_data['battleId'] = battle_id
    # 生成is_cheat校验参数
    is_cheat = encrypt_utils.get_is_cheat(battle_id)
    battle_data['battleData']['isCheat'] = is_cheat
    # 通关时间
    now = utils.get_local_time()
    complete_time = config.get_random_complete_time(now - battle_start_time)
    battle_data['battleData']['completeTime'] = complete_time
    battle_data['battleData']['stats']['beginTs']    = battle_start_time
    battle_data['battleData']['stats']['endTs']      = now
    # 生成access校验
    access = encrypt_utils.get_access_token(player.get_login_time())
    battle_data['battleData']['stats']['access'] = access
    # 应用包名
    battle_data['battleData']['stats']['packageName'] = config.PACKAGE_NAME
    # 平台
    battle_data['platform'] = config.PLATFORM
    # 战斗数据更多优化
    config.adjust_battle_data(battle_data)
    # battle_data加密
    encrypted_data = encrypt_utils.battle_finish_data_encrypt(json.dumps(battle_data), player.get_login_time())
    data = '''{{"data":"{}","battleData":{{"isCheat":"{}","completeTime":{},"stats":null}}}}'''.format(
        encrypted_data, is_cheat, complete_time)
    res = utils.post_to_gs(cgi, data, player)
    code = int(res['result']) 
    if code:
        panic('副本通关失败: data={}, err_code={}'.format(data, code))
    # 游戏数据差量更新
    player.update_attr(res['playerDataDelta']['modified'])
    logger.i('副本通关成功: uid:{}, 当前剩余体力: {}/{}'.format(
        player.get_uid(), player.get_attr()['status']['ap'], player.get_attr()['status']['maxAp']))
    return res

# 完成剧情
def api_finish_story(player, story):
    data = '{{"storyId":"{}"}}'.format(story)
    res = utils.post_to_gs('/story/finishStory', data, player)
    # 游戏数据差量更新
    player.update_attr(res['playerDataDelta']['modified'])
    logger.i('完成剧情: uid:{}, story: {}'.format(player.get_uid(), story))
    return

# 同步卡池信息
def api_sync_normal_gacha(player):
    data = '{}'
    res = utils.post_to_gs('/gacha/syncNormalGacha', data, player)
    # 游戏数据差量更新
    player.update_attr(res['playerDataDelta']['modified'])
    logger.i('卡池信息同步成功: uid:{}'.format(player.get_uid()))
    return

# 单抽
def api_advancedGacha(player, pool_id, use_ticket):
    data = '{{"poolId":"{}","useTkt":{}}}'.format(pool_id, use_ticket)
    res = utils.post_to_gs('/gacha/advancedGacha', data, player)
    # 游戏数据差量更新
    player.update_attr(res['playerDataDelta']['modified'])
    is_new = '新' if res['charGet']['isNew'] else '重复'
    logger.i('单抽成功: uid:{}, 获得{}卡牌: {}'.format(player.get_uid(), is_new, res['charGet']['charId']))
    return

# 修改编队
def api_squad_formation(player, squad_id, slots, change_skill = 0):
    data = '{{"squadId":"{}","slots":{},"changeSkill":{}}}'.format(squad_id, json.dumps(slots, ensure_ascii = False), change_skill)
    res = utils.post_to_gs('/quest/squadFormation', data, player)
    # 游戏数据差量更新
    player.update_attr(res['playerDataDelta']['modified'])
    logger.i('编队更新成功: uid:{}'.format(player.get_uid()))
    return

# 完成任务
def api_confirm_mission(player, mission_id):
    data = '{{"missionId":"{}"}}'.format(mission_id)
    res = utils.post_to_gs('/mission/confirmMission', data, player)
    # 游戏数据差量更新
    player.update_attr(res['playerDataDelta']['modified'])
    logger.i('完成任务: uid:{}, mission_id:{}'.format(player.get_uid(), mission_id))
    return

# 每日签到
def api_checkin(player):
    data = '{}'
    res = utils.post_to_gs('/user/checkIn', data, player)
    # 游戏数据差量更新
    player.update_attr(res['playerDataDelta']['modified'])
    logger.i('每日签到完成: uid:{}'.format(player.get_uid()))
    return

# 活动签到
def api_activity_checkin(player, activity_id, index):
    data = '{{"index":{},"activityId":"{}"}}'.format(index, activity_id)
    res = utils.post_to_gs('/activity/getActivityCheckInReward', data, player)
    # 游戏数据差量更新
    player.update_attr(res['playerDataDelta']['modified'])
    logger.i('活动签到完成: uid:{}, 活动id:{}, 当前签到次数:{}'.format(player.get_uid(), activity_id, index))
    return

# 查询邮件(返回未读邮件id/type列表)
def api_get_meta_info_list(player):
    data = '{{"from":{}}}'.format(utils.get_local_time())
    res = utils.post_to_gs('/mail/getMetaInfoList', data, player)
    # 游戏数据差量更新
    player.update_attr(res['playerDataDelta']['modified'])
    unread_mail_list = []
    has_item = False
    for mail in res['result']:
        if 0 == mail['state']:
            unread_mail_list.append({'mailId': mail['mailId'], 'type': mail['type']})
            if mail['hasItem']:
                has_item = True
    logger.i('成功获取邮件列表: uid:{}, 未读邮件数:{}, 是否有物品:{}'.format(player.get_uid(), len(unread_mail_list), has_item))
    return unread_mail_list

# 收邮件
def api_recieve_mail(player, mail_id, mail_type):
    data = '{{"type":{},"mailId":{}}}'.format(mail_type, mail_id)
    res = utils.post_to_gs('/mail/receiveMail', data, player)
    # 游戏数据差量更新
    player.update_attr(res['playerDataDelta']['modified'])
    logger.i('邮件收取成功: uid:{}, 邮件id:{}'.format(player.get_uid(), mail_id))
    return

# 使用道具
def api_use_item(player, inst_id, item_id, cnt):
    data = '{{"instId":{},"itemId":"{}","cnt":{}}}'.format(inst_id, item_id, cnt)
    res = utils.post_to_gs('/user/useItem', data, player)
    # 游戏数据差量更新
    player.update_attr(res['playerDataDelta']['modified'])
    logger.i('道具使用成功: uid:{}, 道具id:{}, 道具剩余数量:{}'.format(player.get_uid(), item_id, player.get_attr()['consumable'][item_id][inst_id]['count']))
    return







