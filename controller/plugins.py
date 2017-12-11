#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time, tornado.web, json
from tornado import gen
from .base import BaseHandler
from util.function import intval
from tornroutes import route
from wechat import plugin_manager


@route(r"/plugins")
class PluginManageHandler(BaseHandler):
    def get(self, *args, **kwargs):
        self.post(args, kwargs)

    # ajax 进行修改
    def post(self, *args, **kwargs):
        action = self.get_body_argument('action', default=None)
        method = '_post_{}'.format(action)
        if hasattr(self, method):
            getattr(self, method)()
        else:
            self._json('fail', '参数错误')

    @tornado.web.asynchronous
    @gen.coroutine
    def _post_toggle(self):
        index = intval(self.get_body_argument('index', default=None))
        type = self.get_body_argument('type', default=None)
        plugin = self.get_body_argument('plugin', default=None)
        toggle = bool(intval(self.get_body_argument('toggle', default=None)))
        config = self._read_config()
        # 验证数据
        if plugin not in plugin_manager.plugins or type not in config['plugin_config'] \
                or type not in plugin_manager.plugins[plugin]['type']:
            self._json('fail', '参数错误')

        # 开启 or 关闭
        if toggle:
            if plugin in config['plugin_config'][type]:
                self._json('fail', '插件已开启')
            else:
                config['plugin_config'][type].insert(index, plugin)
        else:
            if plugin in config['plugin_config'][type]:
                config['plugin_config'][type].remove(plugin)
            else:
                self._json('fail', '插件已关闭')

        # 更新
        if (yield self.update_plugin(config)):
            self._json('success', '更新成功')
        else:
            self._json('fail', '更新失败')

    @tornado.web.asynchronous
    @gen.coroutine
    def _post_sort(self):
        type = self.get_body_argument('type', default=None)
        list = self.get_body_argument('list', default=None)
        config = self._read_config()
        # 数据校验
        try:
            list = json.loads(list)
            assert type in config['plugin_config']
        except:
            self._json('fail', '参数错误')

        config['plugin_config'][type] = []
        for plugin in list:
            # plugin 开启状态 and 有效的plugin and plugin 有 type的处理能力
            if plugin['toggle'] and plugin['name'] in plugin_manager.plugins \
                    and type in plugin_manager.plugins[plugin['name']]['type']:
                config['plugin_config'][type].append(plugin['name'])

        # 更新
        if (yield self.update_plugin(config)):
            self._json('success', '更新成功')
        else:
            self._json('fail', '更新失败')

    # 更新plugin manage
    async def update_plugin(self, config):
        try:
            plugin_manager.PluginManager().load_plugins(config['plugin_config'])
        except Exception as e:
            return False

        # 写入配置
        self._write_config(config)
        return True
