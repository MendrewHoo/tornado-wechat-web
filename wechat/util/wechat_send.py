#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .base import wechatBase

class wechatSend(wechatBase):

    def send_articles(self, userid, articles, account=None):
        self.client.message.send_articles(userid, articles, account)

    def send_text(self, userid, content, account=None):
        self.client.message.send_text(userid, content, content)
