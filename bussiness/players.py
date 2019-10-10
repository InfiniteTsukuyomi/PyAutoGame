# -*- coding:utf-8 -*-
import json
from bussiness import config
from common import logger
from common import db
from common import utils


# 保存玩家相关所有信息
class Player:
    def __init__(self, device_id, device_id2 = '', device_id3 = '', access_token = ''):
        self.__device_id = device_id                            # 登录设备指纹, 注册账号时使用的唯一标识
        if device_id2:
            self.__device_id2 = device_id2  
        else:
            self.__device_id2 = config.get_random_device_id2()  # imei
        if device_id3:
            self.__device_id3 = device_id3  
        else:
            self.__device_id3 = config.get_random_device_id3()  # 登录设备指纹, 可为空
        self.__account = ''                                     # 账号
        self.__password = ''                                    # 密码
        self.__uid = 0                                          # 当前账号唯一标识
        self.__channel_uid = 0                                  # 渠道uid
        self.__access_token = access_token                      # 游客登录凭据, 用来获取channel_uid
        self.__token = ''                                       # 使用channel_uid和access_token换取的一次性登录凭据
        self.__secret = ''                                      # http session_id, 标志客户端登录状态
        self.__seqnum = 0                                       # 封包编号, 服务器会返回下一次请求使用的编号, 通常每次请求自增1
        self.__login_time = 0                                   # syncData返回的服务器时间, 副本战斗日志加密时使用
        self.__attr = {}                                        # 游戏数据
        return
    def get_device_id(self):
        return self.__device_id
    def get_device_id2(self):
        return self.__device_id2
    def get_device_id3(self):
        return self.__device_id3
    def get_account(self):
        return self.__account
    def set_account(self, account):
        self.__account = account
        return
    def get_password(self):
        return self.__password
    def set_password(self, password):
        self.__password = password
        return
    def get_uid(self):
        return self.__uid
    def set_uid(self, uid):
        self.__uid = uid
        return
    def get_channel_uid(self):
        return self.__channel_uid
    def set_channel_uid(self, channel_uid):
        self.__channel_uid = channel_uid
        return
    def get_access_token(self):
        return self.__access_token
    def set_access_token(self, access_token):
        self.__access_token = access_token
        return
    def get_token(self):
        return self.__token
    def set_token(self, token):
        self.__token = token
        return
    def get_secret(self):
        return self.__secret
    def set_secret(self, secret):
        self.__secret = secret
        return        
    def get_seq(self):
        return self.__seqnum
    def set_seq(self, http_res_header):
        for info in http_res_header:
            if info[0] == 'seqnum':
                # 使用服务器返回的seqnum作为下一次http请求的封包编号
                self.__seqnum = int(info[1])
                return
        # 若服务器未返回, 默认封包编号+1
        self.__seqnum += 1
        return
    def get_login_time(self):
        return self.__login_time    
    def set_login_time(self, ts):
        self.__login_time = ts
        return
    # 获取玩家游戏数据
    def get_attr(self):
        return self.__attr
    # 玩家游戏数据差量更新
    def update_attr(self, diff_attr):
        utils.merge_dict(self.__attr, diff_attr)
        # 数据存盘
        self.save_attr_to_db()
        return
    # 获取sst卡牌数量
    def get_card_cnt(self, rarity):
        try:
            cnt = 0
            if self.__attr:
                if 'troop' in self.__attr:
                    chars = self.__attr['troop']['chars']
                    for index in chars:
                        card_id = chars[index]['charId']
                        if rarity == config.CARD_INFO[card_id]['rarity']:
                            cnt += 1
            return cnt
        except Exception as e:
            logger.e('获取卡牌数量失败: uid:{}, err_msg:{}'.format(self.__uid, str(e)))
        return 0
    # 登录信息存档
    def save_account_info(self):
        # 不会写sql
        db.query('''
            update account set account="{}", password="{}" where uid={} and exists(select uid from account where uid = {});
        '''.format(self.__account, self.__password, self.__uid, self.__uid))
        db.query('''
            insert into account(uid, access_token, account, password, device_id, device_id2, device_id3, attr) select
                    {}, '{}', '{}', '{}', '{}', '{}', '{}', '{}' where not exists(select uid from account where uid = {})
        '''.format(self.__uid, self.__access_token, self.__account, self.__password,
            self.__device_id, self.__device_id2, self.__device_id3, json.dumps(self.__attr, ensure_ascii = False), self.__uid))
        return
    # 数据存档
    def save_attr_to_db(self):
        db.query('''
            update account set nickname='{}', android_diamond={}, diamond_shard={}, gold={}, ssr_cnt={}, 
            ap={}, max_ap={}, attr='{}' where uid={};
        '''.format(self.__attr['status']['nickName'], self.__attr['status']['androidDiamond'], self.__attr['status']['diamondShard'], self.__attr['status']['gold'], self.get_card_cnt(5), 
            self.__attr['status']['ap'], self.__attr['status']['maxAp'], json.dumps(self.__attr, ensure_ascii = False), self.__uid))
        return
    # 打印账号当前状态
    def report_status(self):
        logger.i('脚本完成: uid: {} 剩余体力: {}/{} 玉:{} 源石:{} 金币:{} ssr数量:{}'.format(
            self.get_uid(), self.get_attr()['status']['ap'], self.get_attr()['status']['maxAp'], 
            self.get_attr()['status']['diamondShard'], self.get_attr()['status']['androidDiamond'], self.get_attr()['status']['gold'], self.get_card_cnt(5)))
        return


# 载入指定数量存档
def load_player_from_db(cnt = -1):
    player_list = []
    try:
        rows = db.query('select * from account order by create_time asc limit {}'.format(cnt))
        for row in rows:
            player = Player(row[5], row[6], row[7], row[2])
            player.set_uid(row[0])
            player.set_account(row[3])
            player.set_password(row[4])
            player_list.append(player)
        return player_list
    except Exception as e:
        logger.e('载入账号失败: err_msg:{}'.format(str(e)))
    raise RuntimeError('Oops!')

    