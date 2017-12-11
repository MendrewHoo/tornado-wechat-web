#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .base import BasePlugin
from util.chat_rebot import chatRebot

__type__ = ("receive_message", )
__className__ = "ChatterBotPlugin"

class ChatterBotPlugin(BasePlugin):
    name = "聊天机器人插件"
    description = "聊天机器人插件"
    version = "0.1"
    author = "Mendrew"

    bot = chatRebot()

    async def run(self, msg=None):
        return {'type': 'text', 'content': self.bot.getResponse(msg.content)}
