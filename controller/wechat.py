#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time, tornado.web
from tornado import gen
from .base import BaseHandler
from util.function import not_need_login
from wechat.hook import Hook
from wechatpy.utils import check_signature
from wechatpy.exceptions import InvalidSignatureException
from wechatpy import parse_message
from tornroutes import route
from wechatpy.replies import TextReply

@route(r"/wechat")
class WeChatHandler(BaseHandler):
    responseStr = ''

    @not_need_login
    def prepare(self):
        super().prepare()

    def get(self, *args, **kwargs):
        echo_str = self.get_argument('echostr', '')
        if self.check_signature():
            self.write(echo_str)
        else:
            self.write(self.responseStr)

    def check_signature(self):
        signature = self.get_argument('signature', '')
        timestamp = self.get_argument('timestamp', '')
        nonce = self.get_argument('nonce', '')
        try:
            if not check_signature(self.settings['wechat_token'], signature, timestamp, nonce):
                return True
        except InvalidSignatureException:
            # 处理异常情况或忽略
            pass

    @tornado.web.asynchronous
    @gen.coroutine
    def post(self, *args, **kwargs):
        if not self.check_signature():
            self.write(self.responseStr)

        msg, result = parse_message(self.request.body), None
        print('msg', msg)
        result = yield Hook().listen(self, msg=msg)

        # 回复
        if result and 'type' in result:
            if result['type'] == 'text':
                self.responseStr = TextReply(content=result['content'], message=msg).render()
        self.write(self.responseStr)
