# -*- coding:utf-8 -*-
import base64
import hashlib
import hmac
import json
import random
import string
from Crypto.Cipher import AES

HMAC_KEY            = '91240f70c09a08a6bc72af1a5c8d4670'
LOG_TOKEN_KEY       = '28hfFQq^VmVhmYq5'
ACCESS_TOKEN_KEY    = '62AE221E4C5D4CAD4B851D7380F4ED2C'
CHAT_MASK           = '8OjXUSNSi8yXC0u98mNWvh7MRLGhyEuQ'

AES_KEY_LENGTH = 16
AES_IV_LENGTH  = 16

# u8 签名字串格式
GUEST_LOGIN_SIGN_STR    = 'deviceId={}'
AUTH_SIGN_STR           = 'token={}'
GET_TOKEN_SIGN_STR      = 'appId={}&channelId={}&deviceId={}&deviceId2={}&deviceId3={}&extension={{"uid":"{}","access_token":"{}"}}&platform={}&subChannel={}&worldId={}'
LOGIN_SIGN_STR          = 'account={}&deviceId={}&password={}&platform={}'
GUEST_UPGRADE_STR       = 'deviceId={}&deviceId2={}&deviceId3={}&extension1={{"uid":"{}","access_token":"{}"}}&extension2={{"uid":"{}","access_token":"{}"}}&platform={}&uid={}'

# md5
def GetMd5(src):
    m1 = hashlib.md5()
    m1.update(src.encode('utf-8'))
    return m1.hexdigest()

# aes padding
def pad(s): return s + bytes([AES_KEY_LENGTH - len(s) % AES_KEY_LENGTH] * (AES_KEY_LENGTH - len(s) % AES_KEY_LENGTH))
def unpad(s): return s[0:(len(s) - s[-1])] 

# hex bin to string
def bin_to_string(data):
    return ''.join(["%02X" % x for x in data]).strip()

# 生成随机长字串
def get_random_string(n):
    return ''.join(random.choices(string.ascii_letters + string.digits, k = n))  

# aes-128-cbc encrypt
def rijndael_encrypt(data, key, iv):
    aes_obj = AES.new(key, AES.MODE_CBC, iv)
    encrypt_buf = aes_obj.encrypt(pad(data))
    return encrypt_buf  

# aes-128-cbc decrypt
def rijndael_decrypt(data, key, iv):
    aes_obj = AES.new(key, AES.MODE_CBC, iv)
    decrypt_buf = aes_obj.decrypt(data)
    return unpad(decrypt_buf)         

# u8登录签名: 登录json参数按key从小到大排序;使用&连接;使用HMAC-SHA1算法
def u8_sign(data):
    sign = hmac.new(HMAC_KEY.encode(), data.encode(), hashlib.sha1)
    return sign.hexdigest()

# access_token
def get_access_token(login_time):
    return GetMd5(ACCESS_TOKEN_KEY + str(login_time)).upper()

# batte_finish数据加密
def battle_finish_data_encrypt(data, login_time):
    # key根据登录时服务器时间动态生成
    aes_key = bytes.fromhex(GetMd5(LOG_TOKEN_KEY + str(login_time)))
    # iv在客户端随机生成
    aes_iv  = get_random_string(AES_IV_LENGTH).encode()
    # 对原始数据使用aes-128-cbc加密
    battle_finish_data = rijndael_encrypt(data.encode(), aes_key, aes_iv)
    # iv附在加密数据最后
    battle_finish_data += aes_iv
    return bin_to_string(battle_finish_data)

# is_cheat 加密：battle_id 每个字节+7; base64加密
def get_is_cheat(battle_id):
    data = bytearray(battle_id.encode())
    for i in range(len(data)):
        data[i] += 7
    return base64.b64encode(data).decode()

# TextAsset 资源解密
def text_asset_decrypt(filename):
    # TextAsset资源使用aes-128-cbc加密算法, 加密key是CHAT_MASK前16字节
    aes_key = CHAT_MASK[:AES_KEY_LENGTH].encode()
    aes_iv  = bytearray(AES_IV_LENGTH)   
    with open(filename, 'rb') as fr:
        # 读取文件数据
        data = fr.read()
        # 文件头16字节异或CHAT_MASK后16字节, 得到aes加密iv
        buf  = data[:AES_IV_LENGTH]
        mask = CHAT_MASK[AES_KEY_LENGTH:].encode()
        for i in range(len(buf)):
            aes_iv[i] = buf[i] ^ mask[i]
        # 对剩余数据aes解密
        game_data = rijndael_decrypt(data[AES_IV_LENGTH:], aes_key, aes_iv)
        # 保存解密后的数据到同目录下
        with open(filename + '.json', 'wb') as fw:
            fw.write(game_data)