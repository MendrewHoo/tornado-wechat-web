#!/usr/bin/env python
# -*- coding: utf-8 -*-

class BasePlugin():
    """
    "插件需要有name，description，version，author属性，默认为空。__type__。
    """
    name = ""
    description = ""
    version = ""
    author = ""

    def __init__(self, request=None):
        self.request = request

    async def run(self):
        """
        :return:
        """
        pass