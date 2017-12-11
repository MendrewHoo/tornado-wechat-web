#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .base import BasePlugin
from wechat.util.wechat_user import wechatUser

__type__ = ("scan_event", "subscribe_event")
__className__ = "SubscribePlugin"


class SubscribePlugin(BasePlugin):
    name = "处理关注事件插件"
    description = "处理关注事件插件"
    version = "0.1"
    author = "Mendrew"

    async def run(self, msg=None):
        if msg.event in ('subscribe', 'subscribe_scan'):
            await self.subscribe(msg)
        elif msg.event == 'unsubscribe':
            await self.unsubscribe(msg)

    async def subscribe(self, msg):
        olduser = await self.request.db.wechat_user.find_one({
            'wechatid': msg.source
        })
        subscribe_data = {
            'wechatid': msg.source,
            'subscribe_time': msg.create_time.timestamp(),
            'subscribe': True
        }
        if olduser:
            await self.request.db.wechat_user.update({
                'wechatid': msg.source
            }, {
                '$set': subscribe_data
            })
        else:
            await self.request.db.wechat_user.insert(subscribe_data)

    async def unsubscribe(self, msg):
        await self.request.db.wechat_user.update({
            'wechatid': msg.source
        }, {
            '$set': {'subscribe': False, 'unsubscribe_time': msg.create_time.timestamp()}
        })
