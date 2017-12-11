#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.web, time
from controller.base import BaseHandler
from tornado import gen
from tornroutes import route
from model.user import UserModel
from util.function import hash

@route(r"^/settings/(\w+)")
class SettingsHandler(BaseHandler):
    def initialize(self):
        super().initialize()

    def get(self, *args, **kwargs):
        self.post(args, kwargs)

    def post(self, *args, **kwargs):
        action = args[0]
        method = '_post_{}'.format(action)
        if hasattr(self, method):
            getattr(self, method)()
        else:
            self.redirect("/manage/404")

    @tornado.web.asynchronous
    @gen.coroutine
    def _post_system(self):
        wx_appid = self.get_body_argument('wx_appid', default=None)
        wx_appsecret = self.get_body_argument('wx_appsecret', default=None)
        wx_auth = self.get_body_argument('wx_auth', default=None)
        config = self._read_config()
        if wx_appid:
            config['global']['wechat']['appid'] = wx_appid
        if wx_appsecret:
            config['global']['wechat']['appsecret'] = wx_appsecret
        config['global']['wechat_auth'] = (wx_auth == 'on')
        self._write_config(config)
        self.redirect('/manage/settings')

    @tornado.web.asynchronous
    @gen.coroutine
    def _post_httpapi(self):
        config = self._read_config()
        apikeys = {}
        for k in config['apikey'].keys():
            apikeys[k] = self.get_body_argument(k, default=None)
            if not apikeys[k]:
                del apikeys[k]

        config['apikey'].update(apikeys)
        self._write_config(config)
        self.redirect('/manage/settings')

    @tornado.web.asynchronous
    @gen.coroutine
    def _post_addadmin(self):
        userid = self.get_body_argument('userid', default='')
        password = self.get_body_argument('password', default='')
        repassword = self.get_body_argument('repassword', default='')

        # 两次输入的密码不匹配
        if password != repassword:
            self._json('fail', '两次密码不匹配')
        # 密码长度太短
        if len(password) < 6:
            self._json('fail', '密码设置过短')
        # 加密密码
        password = yield self.backend.submit(hash.get, password)
        oldadmin = yield self.db.admin.find_one({'userid': userid})
        # 用户id已存在
        if oldadmin:
            self._json('fail', '用户id已存在, 请更换')
        # 添加用户
        user = {
            'userid': userid,
            'password': password,
            'power': 20,
            'registertime': time.time(),
            'faceurl': '/static/assets/img/user04.png'
        }
        model = UserModel()
        if not model(user):
            self._json('fail', model.error_msg)
        result = yield self.db.admin.insert(user)
        self._json('success')
