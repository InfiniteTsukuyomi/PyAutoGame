# -*- coding:utf-8 -*-
import random
import hashlib
import json
import string

# 当前签到活动id(活动签到)
CHECKIN_ACTIVITY_ID = 'act3d7'

# 登录参数
APP_ID              = '1'
CHANNEL_ID          = '1'
WORLD_ID            = '1'
PLATFORM            = 1
SUB_CHANNEL         = '1'
NETWORK_VERSION     = '3'

# 应用包名
PACKAGE_NAME        = 'com.hypergryph.arknights'

# 昵称
NICKNAME = [
"苍井空", "波多野结衣", "桃谷绘里香", "小泽玛利亚", "樱井莉亚", "天海翼", "西田麻衣", "明日花绮罗", "原纱央莉", "濑亚美莉", 
"橘梨纱", "西野翔", "柚木提娜", "早川濑里奈", "希崎杰西卡", "麻仓优", "雨宫琴音", "早乙女露依", "椎名由奈", "周防雪子", 
"友田彩也香", "工藤美纱", "冬月枫", "观月雏乃", "横山美雪", "西条琉璃", "若菜光", "红音萤", "木南日菜", "古川伊织", 
"芦名未帆", "相崎琴音", "里美尤利娅", "吉川爱美", "夕树舞子", "织田真子", "朝日奈明", "堀口奈津美", "藤泽美羽", "由爱可奈", 
"望月凉子", "小泽爱丽丝", "川岛和津实", "霞理沙", "星野飞鸟", "小川亚纱美", "程嘉美", "水城奈绪", "初音实", "大友梨奈"
]

# 载入配置文件
def load_config(filename):
    with open(filename, 'rb') as f:
        return json.load(f)

# 所有卡牌数据
CARD_INFO = load_config('./gamedata/character_table.json')

# 所有副本数据
COPY_INFO = load_config('./gamedata/stage_table.json')

# md5
def GetMd5(src):
    m1 = hashlib.md5()
    m1.update(src.encode('utf-8'))
    return m1.hexdigest()

# 生成随机device_id
def get_random_device_id():
    return GetMd5(''.join(random.choices(string.ascii_letters + string.digits, k = 12)))

# 生成随机device_id2
def get_random_device_id2():
    return '86' + ''.join(random.choices(string.digits, k = 13))

# 生成随机device_id3
def get_random_device_id3():
    return GetMd5(''.join(random.choices(string.ascii_letters + string.digits, k = 12)))

# 获取随机昵称
def get_random_nickname():
    return random.choice(NICKNAME)

# 获取随机战斗结束时间
def get_random_battle_finish_time(battle_start_time):
    return battle_start_time + random.randint(80, 200)

# 获取随机通关时间
def get_random_complete_time(real_time):
    return int((random.random()*0.25 + 0.66) * real_time)

# 战斗数据优化(添加更多随机项)
def adjust_battle_data(battle_data):
    return
