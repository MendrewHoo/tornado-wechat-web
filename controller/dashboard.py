#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.web, re, json
from controller.base import BaseHandler
from tornado import gen
import time, pymongo
from util.function import intval, hidekey, server_info_percent
from bson.objectid import ObjectId
from tornroutes import route
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
        cpu, memory, disk = yield self.backend.submit(server_info_percent)
        kargs = {
            'subscribe_count': subscribe_count,
            'm_subscribe_count': m_subscribe_count,
            'cpu': cpu,
            'memory': memory,
            'disk': disk
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
            w_userlist = self.wechat.user.get_user_list([u['wechatid'] for u in userlist])
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
    def _view_menu(self, arg):
        def menu_table_html(menulist, is_submenu=False):
            menu_operate_str = '''
                                <td>
                                    <div class="tpl-table-black-operation">
                                        <a href="javascript:;" onclick="editmenu(this)">
                                            <i class="am-icon-pencil"></i> 编辑
                                        </a>
                                        <a href="javascript:;" onclick="delmenu('{}')" class="tpl-table-black-operation-del">
                                            <i class="am-icon-trash"></i> 删除
                                        </a>
                                        </div>
                                </td>
                                '''
            menu_html = ''
            for menu in menulist:
                if not is_submenu: menu_html += '<tbody data-menu-id="%s">' % (menu['_id'])

                menu_html += '<tr class="gradeX" data-menu-id="%s">' % (menu['_id'])
                menu_html += '<td>%s</td>' % (('┣━ ' if is_submenu else '') + menu['name'])  # 菜单名
                menu_html += '<td>%s</td>' % (menu['type'])  # 菜单类型
                menu_html += '<td>%s</td>' % (menu['args']) # 菜单参数
                menu_html += menu_operate_str.format(menu['_id'])  # 菜单操作
                menu_html += '</tr>'
                if 'sub_button' in menu and menu['sub_button']:  # 子菜单
                    menu_html += menu_table_html(menu['sub_button'], is_submenu=True)

                if not is_submenu: menu_html += '</tbody>'
            return menu_html

        # yield self.db.wechat_menu.remove({})
        # menu = self.wechat.menu.get_menu()
        #
        # yield self.menu2db(menu['menu']['button'])
        menudata = yield self.wechat.menu.db2menu(self)
        menu_sort_str = json.dumps([menu['_id'] for menu in menudata if menu['parent'] == None])

        self.render('menu-manage.html', menulist=menudata, typedict=self.wechat.menu.typedict,
                    menu_sort_str=menu_sort_str, menu_table_html=menu_table_html)


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