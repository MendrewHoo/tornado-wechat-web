#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymongo
from .base import wechatBase

class wechatMenu(wechatBase):
    typedict = {
        'supmenu': '父级菜单',
        'click': '点击',
        'view': '链接'
    }

    def create_menu4btn(self, menulist):
        return self.client.menu.create({
            "button": menulist
        })

    def get_menu(self):
        return self.client.menu.get()

    async def menu2db(self, request, menulist, parent=None):
        '''
        将微信服务器下载menu数据 解析至数据库
        :param request: handler 用于获取db操作对象
        :param menulist:
        :param parent:
        :return:
        '''
        for index, menu in enumerate(menulist):
            is_supmenu = (menu['sub_button'] and 'type' not in menu)
            menudb = {
                'name': menu['name'],
                'type': 'supmenu' if is_supmenu else menu['type'],
                'index': index,
                'parent': parent,
                'args': None if is_supmenu else {k: v for k, v in menu.items() if
                                                 k not in ('name', 'type', 'sub_button')}
            }
            menuid = await request.db.wechat_menu.insert(menudb)
            if is_supmenu:
                await self.menu2db(request, menu['sub_button'], parent=str(menuid))

    async def db2menu(self, request, parent=None):
        '''
        将数据库中的数据解析成易于辨析的menu list(本地)
        :param request: handler 用于获取db操作对象
        :param parent:
        :return:
        '''
        menulist = []
        cursor = request.db.wechat_menu.find({'parent': parent})
        cursor.sort([('index', pymongo.ASCENDING)])
        while (await cursor.fetch_next):
            menu = cursor.next_object()
            menu['_id'] = str(menu['_id'])
            if menu['type'] == 'supmenu':
                menu['sub_button'] = await self.db2menu(request, parent=menu['_id'])
            menulist.append(menu)
        return menulist

    async def db2menu4wechat(self, request, menulist=None):
        '''
        将数据库中的数据解析成微信格式的menu list(网络数据)
        :param request: handler 用于获取db操作对象
        :param parent:
        :return:
        '''
        if menulist is None:
            menulist = await self.db2menu(request)
        result = []
        for menu in menulist:
            if menu['type'] == 'supmenu':
                result.append({
                    'name': menu['name'],
                    'sub_button': (await self.db2menu4wechat(request, menulist=menu['sub_button']))
                })
            else:
                menu = {k:v for k, v in menu.items() if k in ('type', 'name', 'args')}
                if menu['args']: menu.update(menu['args'])
                del menu['args']
                result.append(menu)
        return result