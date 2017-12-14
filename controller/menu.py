#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time, tornado.web, json, pymongo
from tornado import gen
from .base import BaseHandler
from util.function import intval
from tornroutes import route
from bson.objectid import ObjectId
from model.wechat_menu import WechatMenuModel


@route(r"/menu")
class MenuManageHandler(BaseHandler):

    def get(self, *args, **kwargs):
        action = self.get_query_argument('action', default=None)
        method = '_get_{}'.format(action)
        if hasattr(self, method):
            getattr(self, method)()
        else:
            self._json('fail', '参数错误')

    @tornado.web.asynchronous
    @gen.coroutine
    def _get_download2db(self):
        '''
        get 方式 请求从微信服务器将menu数据下载并解析到数据库
        :return:
        '''
        try:
            yield self.db.wechat_menu.remove({}) # 清空数据库
            menudata = self.wechat.menu.get_menu()
            yield self.wechat.menu.menu2db(self, menudata['menu']['button'])
        except:
            self._json('fail', '更新数据库失败')
        self._json('success', '更新数据库成功')

    @tornado.web.asynchronous
    @gen.coroutine
    def _get_upload2wechat(self):
        '''
        get 方式请求 将数据库内容打包提交到微信服务器以更新菜单
        :return:
        '''
        try:
            menudata = yield self.wechat.menu.db2menu4wechat(self)
            result = self.wechat.menu.create_menu4btn(menudata)
            assert result['errcode'] == 0
        except:
            self._json('fail', '上传微信服务器失败')
        self._json('success', '上传微信服务器成功')

    # ajax 获取修改的html
    @tornado.web.asynchronous
    @gen.coroutine
    def _get_edit(self):
        menuid = self.get_query_argument('id', default=None)
        print(menuid)
        try:
            menu = yield self.db.wechat_menu.find_one({
                '_id': ObjectId(menuid)
            })
        except:
            menu = {'type': 'new'}
        if menu['type'] == 'supmenu':
            # 子菜单列表
            cursor = self.db.wechat_menu.find({'parent': menuid})
            count = yield cursor.count()
            cursor.sort([('index', pymongo.ASCENDING)])
            menu['sub_button'] = yield cursor.to_list(count)
            # 可添加列表
            cursor = self.db.wechat_menu.find({
                'parent': None,
                '_id': {'$ne': menu['_id']},
                'type': {'$ne': 'supmenu'}
            })
            count = yield cursor.count()
            cursor.sort([('index', pymongo.ASCENDING)])
            menu['enableAdd'] = yield cursor.to_list(count)
        self.render('/ajax/edit-menu.html', menu=menu, typedict=self.wechat.menu.typedict)


    def post(self, *args, **kwargs):
        action = self.get_body_argument('action', default=None)
        method = '_post_{}'.format(action)
        if hasattr(self, method):
            getattr(self, method)()
        else:
            self._json('fail', '参数错误')

    @tornado.web.asynchronous
    @gen.coroutine
    def _post_new(self):
        menu = {
            'name': self.get_body_argument('name', default=None),
            'type': self.get_body_argument('type', default=None),
            'index': 0,
            'parent': None,
            'args': None
        }

        # 模型校验数据
        model = WechatMenuModel()
        if not model(menu):
            self._json('fail', model.error_msg)

        menuid = yield self.db.wechat_menu.insert(menu)
        if isinstance(menuid, ObjectId):
            self._json('success', '添加成功')
        else:
            self._json('fail', '添加失败')

    @tornado.web.asynchronous
    @gen.coroutine
    def _post_edit(self):
        id = self.get_body_argument('id', default=None)
        menu = {
            'name': self.get_body_argument('name', default=None),
            'type': self.get_body_argument('type', default=None),
            'sub_button': []
        }
        if menu['type'] == 'supmenu':
            sub_button = self.get_body_argument('sub_button', default=None)
            menu['sub_button'] = json.loads(sub_button)
        else:
            args = self.get_body_argument('args', default=None)
            menu['args'] = json.loads(args)

        # 模型校验数据
        model = WechatMenuModel()
        if not model(menu):
            self._json('fail', model.error_msg)

        # 数据库中是否有效值
        try:
            menu['sub_button'] = [ObjectId(sub_button) for sub_button in menu['sub_button']]
            menu_count = yield self.db.wechat_menu.find({
                '_id': {'$in': menu['sub_button'] + [ObjectId(id)]}
            }).count()
            assert menu_count == (len(menu['sub_button']) + 1)
        except:
            self._json('fail', '未找到原数据')

        # 更新
        if menu['type'] == 'supmenu':
            # 主菜单的处理
            # 清除原有的子菜单数据
            yield self.db.wechat_menu.update({
                'parent': id
            }, {
                '$set': {'parent': None}
            }, multi=True)
            # 修改子菜单数据
            for idx, val in enumerate(menu['sub_button']):
                yield self.db.wechat_menu.update({
                    '_id': val
                }, {
                    '$set': {
                        'parent': id,
                        'index': idx
                    }
                })
        del menu['sub_button']
        yield self.db.wechat_menu.update({
            '_id': ObjectId(id)
        }, {
            '$set': menu
        })
        self._json('success', '修改成功')

    @tornado.web.asynchronous
    @gen.coroutine
    def _post_del(self):
        id = self.get_body_argument('id', default=None)

        # 数据库中是否有效值
        try:
            result = yield self.db.wechat_menu.remove({
                '_id': ObjectId(id)
            })
            print(result)
            assert result['n'] == 1
        except:
            self._json('fail', '未找到原数据')
        self._json('success')

    @tornado.web.asynchronous
    @gen.coroutine
    def _post_updatesort(self):
        sort = self.get_body_argument('sort', default=None)
        sort = json.loads(sort)

        # 数据库中是否有效值
        try:
            sort = [ObjectId(menuid) for menuid in sort]
            menu_count = yield self.db.wechat_menu.find({
                '_id': {'$in': sort}
            }).count()
            assert menu_count == len(sort)
        except:
            self._json('fail', '未找到原数据')

        # 更新
        for idx, val in enumerate(sort):
            yield self.db.wechat_menu.update({
                '_id': val
            }, {
                '$set': { 'index': idx }
            })
        self._json('success', '更新排序成功')

