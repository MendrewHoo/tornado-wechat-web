#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.web, json, yaml, os, time, re, logging
from torndsession.sessionhandler import SessionBaseHandler
from util.flash import flash
from util.function import humantime, nl2br


class BaseHandler(SessionBaseHandler):
    def initialize(self):
        self.db = self.settings.get('database')
        self.redis = self.settings.get('redis')
        self.httpapi = self.settings.get('httpapi')
        self.backend = self.settings.get('thread_pool')
        self.flash = flash(self)
        self.topbar = 'home'

    def prepare(self):
        self.add_header("Content-Security-Policy", "default-src 'self'; script-src 'self' 'unsafe-eval' 'unsafe-inline'; "
                                                   "connect-src 'self'; img-src 'self' data: blob:; style-src 'self'  'unsafe-inline'; "
                                                   "font-src 'self' data:; frame-src 'self'; ")
        self.add_header("X-Frame-Options", "deny")
        self.add_header("X-XSS-Protection", "1; mode=block")
        self.add_header("X-Content-Type-Options", "nosniff")
        self.add_header("X-UA-Compatible:", "IE=edge,chrome=1")
        self.clear_header('Server')
        self.power = 'guest'
        power = {
            20: 'admin'
        }
        if self.current_user and self.current_user.get('power') in power:
            self.power = power[self.current_user['power']]

        flush = self.get_cookie('flush_info', default=None)
        if self.current_user and not flush:
            self.flush_session()

    def check_login(self):
        try:
            assert type(self.current_user) is dict
            assert 'userid' in self.current_user
        except AssertionError:
            self.custom_error('请先注册或登录', jump='/login')

    def get_current_user(self):
        try:
            user = self.session.get('current_user')
            # assert self.set_session(user)
        except:
            user = None
        return user

    # 设置用户的session信息
    def set_session(self, user):
        try:
            assert ('_id' in user and 'userid' in user)
            session = dict(user)
            session['login_time'] = time.time()

            self.session.set('current_user', session)
            return session
        except:
            import traceback
            print(traceback.print_exc())
            return None

    # 获取客户端ip
    def get_ipaddress(self):
        if self.settings['intranet']:
            return self.request.headers.get('X-Real-Ip')
        else:
            return self.request.remote_ip

    def flush_session(self):
        def call_back(user, error):
            if error:
                print('error getting user!', error)
            else:
                if user:
                    user['_id'] = str(user['_id'])
                    user['login_time'] = self.current_user['login_time']
                    del user['password']
                else:
                    user = self.current_user
                self.set_session(user)
                self.current_user = user

        self.set_cookie('flush_info', 'ok', expires=time.time() + 60)
        self.db.admin.find_one({
            'userid': self.current_user['userid']
        }, callback=call_back)

    def render(self, template_name, **kwargs):
        kwargs['topbar'] = self.topbar
        kwargs['humantime'] = humantime
        kwargs['nl2br'] = nl2br
        kwargs['str'] = str
        kwargs['power'] = self.power
        kwargs['pagenav'] = self.pagenav
        return super().render(template_name, **kwargs)

    # 跳转网页
    def redirect(self, url, permanent=False, status=None):
        super().redirect(url, permanent, status)
        raise tornado.web.Finish()

    # 显示错误信息页面
    def custom_error(self, info, **kwargs):
        if not self._finished:
            status_code = kwargs.get('status_code', 200)
            self.set_status(status_code)
            error_title = kwargs.get('title', '提示信息')
            error_status = kwargs.get('status', 'warning')
            error_jump = kwargs.get('jump', '#back')
            self.render('error.html', error_info=info, error_status=error_status,
                        error_title=error_title, error_jump=error_jump)
        raise tornado.web.Finish()

    # json 数据返回
    def _json(self, status, info=''):
        data = {
            'status': status,
            'info': info
        }
        self.write(data)
        raise tornado.web.Finish()

    # 读写配置
    def _write_config(self, config):
        with open(self.settings['config_filename'], 'w') as f:
            yaml.dump(config, f, default_flow_style=False, default_style='"')
        for k, v in config['global'].items():
            self.settings[k] = v

    def _read_config(self):
        with open(self.settings['config_filename'], 'r') as f:
            config = yaml.load(f)
        return config

    # 分页导航
    def pagenav(self, count, url, each, now,
                pre='<ul class="am-pagination tpl-pagination">', end='</ul>'):
        _ret = ''
        _pre = pre
        _end = end
        page = (count // each + 1) if (count % each != 0) else (count / each)
        i = now - 5
        while (i <= now + 5) and (i <= page):
            if i > 0:
                _url = url.format(pagination=i)
                if now == i:
                    _ret += '<li class="am-active"><a href="{url}">{i}</li>'.format(url=_url, i=i)
                else:
                    _ret += '<li><a href="{url}">{i}</li>'.format(url=_url, i=i)
            i += 1
        if now > 6:
            _url = url.format(pagination=1)
            _ret = '<li><a href="{url}">首页</a></li>' \
                   '<li class="am-disabled"><a href="#">...</a></li>{ret}'.format(url=_url, ret=_ret)
        if now + 5 < page:
            _url = url.format(pagination=page)
            _ret = '{ret}<li class="am-disabled"><a href="#">...</a></li>' \
                   '<li><a href="{url}">尾页</a></li>'.format(url=_url, ret=_ret)
        if page <= 1:
            _ret = ''
        _ret = _pre + _ret + _end
        return _ret