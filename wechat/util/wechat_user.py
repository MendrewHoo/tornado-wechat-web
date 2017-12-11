#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .base import wechatBase

class wechatUser(wechatBase):
    def get_user(self, wechatid):
        return self.client.user.get(wechatid)

    def get_user_list(self, userlist):
        return self.client.user.get_batch(userlist)
