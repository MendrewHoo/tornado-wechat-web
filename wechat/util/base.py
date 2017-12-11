#!/usr/bin/env python
# -*- coding: utf-8 -*-
from wechatpy import WeChatClient
from wechatpy.session.redisstorage import RedisStorage

class wechatBase():
    def __init__(self, appid, secret, redis_client=None):
        session_interface = None
        if redis_client:
            session_interface = RedisStorage(
                redis_client,
                prefix="wechatpy"
            )
        self.client = WeChatClient(appid, secret, session=session_interface)