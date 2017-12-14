#!/usr/bin/env python
# -*- coding: utf-8 -*-

from wechatpy import WeChatClient
from wechatpy.session.redisstorage import RedisStorage
from .wechat_menu import wechatMenu
from .wechat_user import wechatUser
from .wechat_send import wechatSend
from .wechat_qrcode import wechatQrcode

class wechatUtil():

    def __init__(self, appid, secret, redis_client=None):
        session_interface = None
        if redis_client:
            session_interface = RedisStorage(
                redis_client,
                prefix="wechatpy"
            )
        client = WeChatClient(appid, secret, session=session_interface)

        self.menu = wechatMenu(client)
        self.qrcode = wechatQrcode(client)
        self.send = wechatSend(client)
        self.user = wechatUser(client)