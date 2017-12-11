#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .base import BasePlugin
from wechat.util import wechat_qrcode

__type__ = ("scan_event", )
__className__ = "ScanQrcodePlugin"

class ScanQrcodePlugin(BasePlugin):
    name = "处理扫描二维码插件"
    description = "处理扫描二维码插件"
    version = "0.1"
    author = "Mendrew"

    async def run(self, msg=None):
        intent_list = msg.scene_id.split(':', 1)
        print('*'* 20, self.request.redis.get(msg.scene_id))
        if intent_list[0] in (wechat_qrcode.binding_qrcode, wechat_qrcode.login_qrcode) \
                and self.request.redis.get(msg.scene_id) == '0':
            self.request.redis.set(msg.scene_id, msg.source)
            self.request.redis.get(msg.scene_id)
