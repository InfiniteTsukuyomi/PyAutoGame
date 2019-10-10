# -*- coding:utf-8 -*-
import json
import urllib.request
import urllib.parse
import ssl
import time
import gevent
from common import logger

# https
context = ssl._create_unverified_context()

# host
HOST_AUTH_SERVER = 'https://ak-as.hypergryph.com:9443'
HOST_GAME_SERVER = 'https://ak-gs.hypergryph.com:8443'

# 默认https请求头
COMMON_HEADER = {
    'Content-Type' : 'application/json',
    'X-Unity-Version' : '5.6.7f1',
    'User-Agent' : 'Dalvik/2.1.0 (Linux; U; Android 5.1.1; X Build/LYZ28N)',
    'Connection' : 'Keep-Alive',
}

# https发包
def post_to_as(cgi, data):
    # http请求失败, 每隔3秒重试一次
    retry_cnt = 3
    while retry_cnt > 0:
        retry_cnt -= 1
        try:
            # 拼接url
            url = HOST_AUTH_SERVER + cgi
            # 发送请求
            logger.d('{} 请求数据:{}'.format(url, data))
            req = urllib.request.Request(url, data = data.encode(), headers = COMMON_HEADER)
            with urllib.request.urlopen(req, context=context, timeout = 3) as response:
                res = response.read().decode()
                logger.d('{} 返回数据:{}'.format(url, res))
                # 服务器返回数据解析成json
                return json.loads(res)  
        except Exception as e:
                if str(e) == 'HTTP Error 500: Internal Server Error':
                    logger.e('{} 请求失败, 剩余重试次数{}: data:{} err_msg:{}'.format(url, retry_cnt, data, str(e)))
                    gevent.sleep(3)
                else:
                    logger.e('{} 请求失败: data:{} err_msg:{}'.format(url, data, str(e)))
                    break
    raise RuntimeError('[post_to_as] Oops!') 

# https发包
def post_to_gs(cgi, data, player):
    # http请求失败, 每隔3秒重试一次
    retry_cnt = 3
    while retry_cnt > 0:
        retry_cnt -= 1
        try:
            # 拼接url
            url = HOST_GAME_SERVER + cgi
            # 更新http请求头
            header = COMMON_HEADER
            headder_ex = {
                'uid': int(player.get_uid()),
                'secret': player.get_secret(),
                'seqnum': player.get_seq()
            }

            header.update(headder_ex)
            # 发送请求
            logger.d('{} 请求数据:{}'.format(url, data))
            req = urllib.request.Request(url, data = data.encode(), headers = header)
            with urllib.request.urlopen(req, context=context, timeout = 3) as response:
                res = response.read().decode()
                # 更新封包编号
                player.set_seq(response.getheaders())
                logger.d('{} 返回数据:{}'.format(url, res))
                # 服务器返回数据解析成json
                return json.loads(res)  
        except Exception as e:
            if -1 != str(e).find('urlopen error timed out'):
                logger.e('{} 请求失败, 可能触发AntiDos, 剩余重试次数{}: data:{} err_msg:{}'.format(url, retry_cnt, data, str(e)))
                time.sleep(3)
            else:
                logger.e('{} 请求失败: data:{} err_msg:{}'.format(url, data, str(e)))
                break
    raise RuntimeError('[post_to_gs] Oops!')


# 服务器与本地时间差
time_diff = 0

# 本地时间校正
def set_time_diff(server_time):
    global time_diff
    time_diff = server_time - int(time.time())

# 获取本地时间
def get_local_time():
    return int(time.time()) + time_diff

# 读文件
def read_buf_from_file(filename):
    with open(filename, 'rb') as f:
        return f.read()

# 写文件
def write_buf_to_file(filename, buf):
    with open(filename, 'wb') as f:
        f.write(buf)

# 字典合并
def merge_dict(old, new):
    for k in new:
        if k in old:
            if not isinstance(new[k], dict):
                old[k] = new[k]
                continue
            merge_dict(old[k], new[k])
        else:
            old[k] = new[k]
    return
