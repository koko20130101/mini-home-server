# -*- coding: utf8 -*-
import json
import time
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest


def getAliyunToken(accessKeyId, accessKeySecret):
    # 创建AcsClient实例
    client = AcsClient(accessKeyId, accessKeySecret, "cn-shanghai")

    # 创建request，并设置参数。
    request = CommonRequest()
    request.set_method('POST')
    request.set_domain('nls-meta.cn-shanghai.aliyuncs.com')
    request.set_version('2019-02-28')
    request.set_action_name('CreateToken')

    try:
        response = client.do_action_with_exception(request)

        jss = json.loads(response)
        print(jss)
        if 'Token' in jss and 'Id' in jss['Token']:
            token = jss['Token']['Id']
            expireTime = jss['Token']['ExpireTime']
            return {'token': token, 'expireTime': expireTime}
            print("token = " + token)
            print("expireTime = " + str(expireTime))
    except Exception as e:
        print(e)
