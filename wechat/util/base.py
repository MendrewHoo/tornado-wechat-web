#!/usr/bin/env python
# -*- coding: utf-8 -*-
from wechatpy import WeChatClient

class wechatBase():
    def __init__(self, client):
        self.client = client