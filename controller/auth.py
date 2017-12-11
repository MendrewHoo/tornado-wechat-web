#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.web, time, json
from controller.base import BaseHandler
from tornado import gen
from util.function import not_need_login, hash, intval
from tornroutes import route
from wechat.util import wechat_qrcode

@route(r"^/auth/(\w+)")
class AuthHandler(BaseHandler):
    @not_need_login
    def prepare(self):
        super().prepare()


    def get(self, *args, **kwargs):
        method = '_get_{}'.format(args[0])
        if hasattr(self, method):
            getattr(self, method)()
        else:
            self.redirect("/login")

    def _get_quit(self):
        self.session.delete('current_user')
        self.redirect('/login')

    @tornado.web.asynchronous
    @gen.coroutine
    def _get_qrcode(self):
        key = self.get_query_argument('key', default='')
        now, expire_seconds = time.time(), 600
        while True:
            yield gen.sleep(2)
            if time.time() > now + expire_seconds:
                self._json('overtime', '超时处理')
            value = self.redis.get(key)

            if len(value) > 5:
                self.redis.delete(key)
                break
        # 有值将取回临时存储的user信息
        user = self.flash['temp_user']
        intent_list = key.split(':', 1)
        print('user', user)
        if intent_list[1] != user['userid']:
            self._json('fail', '错误操作, 会话值不符合预期')
        # 登录或者绑定
        if intent_list[0] == wechat_qrcode.login_qrcode and user['wechatid'] == value:
            self.set_session(user)
            self._json('pass', '/manage/index')
        elif intent_list[0] == wechat_qrcode.binding_qrcode:
            oldadmin = yield self.db.admin.find_one({
                'wechatid': value
            })
            if oldadmin:
                self._json('fail', '该微信已被绑定过')
            yield self.db.admin.update({
                'userid': user['userid']
            }, {
                '$set': {'wechatid': value}
            })
            self._json('pass', '/login')
        else:
            self._json('fail', '错误操作, 无效事件')


@route(r"^/login")
class LoginHandler(BaseHandler):
    def initialize(self):
        super().initialize()
        self.topbar = 'login'

    @not_need_login
    def prepare(self):
        super().prepare()

    def get(self, *args, **kwargs):
        self.render('login.html')

    @tornado.web.asynchronous
    @gen.coroutine
    def post(self, *args, **kwargs):
        user = None
        try:
            userid = self.get_body_argument('userid', default='')
            password = self.get_body_argument('password', default='')

            user = yield self.db.admin.find_one({'userid': userid})
            assert user
            check = yield self.backend.submit(hash.verify, password, user.get('password'))
            if check and user['power'] == 20:
                temp = yield self.db.admin.find_and_modify({'userid': userid}, {
                    '$set': {
                        'logintime': time.time(),
                        'loginip': self.get_ipaddress()
                    }
                })
                print('login ok', temp)
            else:
                assert False
        except:
            import traceback
            print(traceback.print_exc())
            self._json('fail', '登录失败, 用户名或密码错误')

        # 是否关闭微信认证
        if self.settings['wechat_auth']:
            # 微信扫描认证
            wQrcode = wechat_qrcode.wechatQrcode(self.settings['wechat']['appid'], self.settings['wechat']['appsecret'])
            # 登录或者绑定
            if 'wechatid' in user and user['wechatid']:
                key = '{}:{}'.format(wechat_qrcode.login_qrcode, user['userid'])
            else:
                key = '{}:{}'.format(wechat_qrcode.binding_qrcode, user['userid'])
            res = wQrcode.create_qrcode(key)
            self.redis.set(key, 0)
            self.flash['temp_user'] = user
            self._json('success', {'url': res['url'], 'key': key})
        else:
            self.set_session(user)
            self._json('pass', '/manage/index')
