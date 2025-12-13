import base64
import json
import urllib.request
import urllib.parse
from Cryptodome.Cipher import AES
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
import datetime
import random
import secrets
import string
import re
import time
import hashlib

# 解密微信手机号等信息


class WXBizDataCrypt:
    def __init__(self, appId, sessionKey):
        self.appId = appId
        self.sessionKey = sessionKey

    def decrypt(self, encryptedData, iv):
        sessionKey = base64.b64decode(self.sessionKey)
        encryptedData = base64.b64decode(encryptedData)
        iv = base64.b64decode(iv)
        cipher = AES.new(sessionKey, AES.MODE_CBC, iv)
        decrypted = json.loads(self._unpad(
            cipher.decrypt(encryptedData).decode()))

        if decrypted['watermark']['appid'] != self.appId:
            raise Exception('Invalid Buffer')

        return decrypted

    def _unpad(self, s):
        return s[:-ord(s[len(s)-1:])]


# 基本分页
class NewPagination(PageNumberPagination):

    page_size = 50
    max_page_size = 100
    page_size_query_param = 'pageSize'
    page_query_param = 'page'       # 查询的页数。

    def get_paginated_response(self, data):
        if self.page.has_next():
            next = self.page.next_page_number()
        else:
            next = ''
        return Response({
            'count': self.page.paginator.count,
            'next': next,
            # 'previous': self.page.paginator.page_range,
            # 'code': status.HTTP_200_OK,
            'message': 'ok',
            'results': data,
        })

# 偏移分页
# class NewPagination(LimitOffsetPagination):

#     default_limit = 5   # 显示多少条
#     limit_query_param = 'size'  # 每次取的条数
#     offset_query_param = 'page' # 如果page=6 表示从第6条可以查。
#     max_limit  = 50   # 最多取50条

# 游标分页
# class NewPagination(CursorPagination):

#     cursor_query_param = 'cursor'
#     # ordering = 'id'  # 按照id排序
#     page_size = 10  # 每页显示多少条
#     page_size_query_param = 'pageSize'  # 每页显示多少条、
#     max_page_size = 50    # 最多显示5条


def getSessionInfo(jsCode, appid, secret):
    url = "https://api.weixin.qq.com/sns/jscode2session?appid=" + appid + \
        "&secret=" + secret + "&js_code=" + jsCode + "&grant_type=authorization_code"
    res = urllib.request.urlopen(url)
    content = res.read().decode()
    obj = json.loads(content)
    return obj


def getAccessToken(appid, secret):
    url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=" + appid + \
        "&secret=" + secret
    access_token = cache.get('access_token')
    if not access_token:
        res = urllib.request.urlopen(url)
        content = res.read().decode()
        obj = json.loads(content)
        # 缓存起来,7200秒（两小时）有效
        cache.set('access_token', obj['access_token'], obj['expires_in'])
        return obj['access_token']
    else:
        return access_token


# 获取小程序二维码

def getUnlimited(access_token, params):
    url = "https://api.weixin.qq.com/wxa/getwxacodeunlimit?access_token=" + access_token

    # 使用urlencode将字典参数序列化成字符串
    data_string = json.dumps(params)
    # 将序列化后的字符串转换成二进制数据，因为post请求携带的是二进制参数
    last_data = bytes(data_string, 'utf8')
    res = urllib.request.urlopen(url, data=last_data)
    content = res.read()
    return content


def getPhonenumber(access_token, params):
    url = "https://api.weixin.qq.com/wxa/business/getuserphonenumber?access_token=" + access_token

    # 使用urlencode将字典参数序列化成字符串
    data_string = json.dumps(params)
    # 将序列化后的字符串转换成二进制数据，因为post请求携带的是二进制参数
    last_data = bytes(data_string, 'utf8')
    res = urllib.request.urlopen(url, data=last_data)
    content = res.read().decode()
    obj = json.loads(content)
    return obj['phone_info']


# 修改上传文件名称及存储路径
def get_upload_to(instance, filename):
    ext = filename.split('.')[-1]  # 获取后缀名
    filename = "%s_%d.%s" % ((datetime.datetime.now().strftime(
        '%Y%m%d%H%M%S')), random.randrange(100, 999), ext)
    if instance.user:
        return 'MiniHome/upload/{0}_{1}'.format(instance.user.id, filename)
    else:
        return 'MiniHome/upload/{0}'.format(filename)

# 生成随机字符串


def generate_random_string(length: int = 16) -> str:
    # 定义字符集：大小写字母 + 数字（共 62 个字符）
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))


def generate_product_id(length=12, use_hash=False):
    """
    生成唯一商品ID

    参数:
    length (int): 最终ID长度 (8-32, 默认12)
    use_hash (bool): 是否用SHA256压缩内容 (增加唯一性但降低可读性)

    返回:
    str: 格式为 [时间戳][随机字符] 的唯一ID
    """
    # 生成时间戳部分 (微秒精度)
    timestamp = int(time.time() * 1e6)
    hex_time = f"{timestamp:016x}"  # 16位十六进制

    # 生成随机部分
    rand_str = secrets.token_hex((length - 8) // 2)  # 根据长度计算随机字节

    # 组合基础ID
    base_id = hex_time.upper() + rand_str.upper()

    # 可选哈希压缩
    if use_hash:
        hashed = hashlib.sha256(base_id.encode()).hexdigest()[:length]
        return hashed.upper()

    return base_id[:length]

# 去除字符串中的表情和特殊符号


def remove_emojis_and_special_chars(text):
    # 匹配中文、英文字母、中文标点和常见英文标点
    pattern = re.compile(
        r'[^'
        r'\u4e00-\u9fa5'  # 中文
        r'a-zA-Z0-9'          # 英文
        r'\u3000-\u303F'  # 基础中文标点（。，、！？等）
        r'\uFF00-\uFF0F'  # 全角标点（！％，：；等）
        r'\u2010-\u201F'  # 引号（‘’“”―–等）
        r'!\"#\$%&\'()*+,\-\./:;<=>\?@\[\\\]\^_`\{\|\}~'  # 英文标点
        r']'
    )
    return re.sub(pattern, '', text)


def increment_array(arr, step):
    # 数组中的值根据step依次增长（应用于比赛点兵）
    try:
        if len(arr) < 2 or len(set(arr)) <= 1 or (len(set(arr[1:])) <= 1 and arr[0] - arr[1] < step):
            return 0

        # 一般情况：从左到右找第一个小于基数的元素并加1
        for i in range(1, len(arr)):
            if arr[i] < arr[0]:
                return i
        return 0
    except:
        return 0
