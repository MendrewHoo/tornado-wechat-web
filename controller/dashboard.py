#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.web, re
from controller.base import BaseHandler
from tornado import gen
import time, pymongo
from util.function import intval, hidekey
from bson.objectid import ObjectId
from tornroutes import route
from wechat.util.wechat_user import wechatUser
from wechat import hook, plugin_manager

@route(r"^/manage/(\w+)(/(.*))?")
class DashboardHandler(BaseHandler):
    def initialize(self):
        super().initialize()

    def prepare(self):
        super().prepare()
        if self.power != 'admin':
            self.redirect('/login')

    def get(self, *args, **kwargs):
        action = args[0] if len(args) else 'index'
        self.topbar = action
        method = '_view_{}'.format(action)
        args = args[2] if len(args) == 3 else None
        if hasattr(self, method):
            getattr(self, method)(args)
        else:
            self._view_404(args)

    @tornado.web.asynchronous
    @gen.coroutine
    def _view_index(self, arg):
        subscribe_count = yield self.db.wechat_user.find({
            'subscribe': True
        }).count()
        m_subscribe_count = yield self.db.wechat_user.find({
            'subscribe': True,
            'subscribe_time': {'$gt': time.time() - 30 * 24 * 60 * 60}
        }).count()
        kargs = {
            'subscribe_count': subscribe_count,
            'm_subscribe_count': m_subscribe_count
        }
        self.render('index.html', **kargs)


    @tornado.web.asynchronous
    @gen.coroutine
    def _view_userlist(self, arg):
        if arg not in ('all', 'subscribe', 'unsubscribe'): arg = 'all'
        options = {
            'all': {},
            'subscribe': {'subscribe': True},
            'unsubscribe': {'subscribe': False}
        }
        page = intval(self.get_argument('page', default=1))
        if not page or page <= 0: page = 1
        limit = 10
        cursor = self.db.wechat_user.find(options[arg])
        count = yield cursor.count()
        cursor.sort([('time', pymongo.DESCENDING)]).limit(limit).skip((page - 1) * limit)
        userlist = yield cursor.to_list(limit)
        if userlist:
            wUser = wechatUser(self.settings['wechat']['appid'], self.settings['wechat']['appsecret'])
            w_userlist = wUser.get_user_list([u['wechatid'] for u in userlist])
            for i in range(len(userlist)):
                userlist[i].update(w_userlist[i])
        sex = {
            0: '未知',
            1: '男',
            2: '女'
        }
        self.render('user-list.html', userlist=userlist, item=arg, sex=sex, page=page, each=limit, count=count)

    @tornado.web.asynchronous
    @gen.coroutine
    def _view_plugins(self, arg):
        args = {
            'plugins': hook.plugins,
            'hook_info': hook.hook_info,
            'plugin_con': len(plugin_manager.plugins)
        }
        self.render('plugin-manage.html', **args)

    @tornado.web.asynchronous
    @gen.coroutine
    def _view_settings(self, arg):
        cursor = self.db.admin.find()
        count = yield cursor.count()
        cursor.sort([('logintime', pymongo.DESCENDING)])
        userlist = yield cursor.to_list(count)
        config = self._read_config()
        self.render('settings.html', userlist=userlist, config=config, hidekey=hidekey)

    @tornado.web.asynchronous
    @gen.coroutine
    def _view_404(self, arg):
        '''
        404 页面
        :param arg:
        :return:
        '''
        self.render('404.html')
