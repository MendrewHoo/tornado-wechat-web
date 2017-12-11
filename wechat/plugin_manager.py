#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob, os
from . import hook
from importlib import import_module

class PluginNoSupportException(Exception): pass

class NoFoundPluginException(Exception): pass

plugins = {}

class PluginManager(object):

    def __init__(self):
        self.directory = os.path.join(os.path.dirname(__file__), 'plugins')

    def load_plugins(self, config):
        """Load plugins by iterating files in plugin directory.
        """
        # 从文件夹中扫描出plugin文件
        plugins_file = []
        try:
            for f in glob.glob(os.path.join(self.directory, '*.py')):
                f = os.path.basename(f)
                if f not in ('__init__.py', 'base.py'):
                    plugins_file.append(f[:-3])
        except OSError:
            print("Failed to access: %s" % dir)

        # 将文件装置成类对象
        for name in plugins_file:
            path = os.path.relpath(self.directory, os.path.realpath('.'))
            path = path.replace(os.path.sep, '.')
            module = import_module('.%s' % name, path)
            plugin_class = getattr(module, getattr(module, "__className__"))
            if hasattr(module, "__type__"):
                plugins[name] = {'type': module.__type__, 'plugin_class': plugin_class}

        # 恢复初始值
        hook.plugins = {}

        # 根据配置顺序向hook注册
        print(config)
        for (type, plugin_list) in config.items():
            for plugin_name in plugin_list:
                if plugin_name in plugins:
                    plugin = plugins[plugin_name]
                    if type in plugin['type']:
                        hook.plugins.setdefault(type, []).append({
                            'name': plugin_name,
                            'plugin_class': plugin['plugin_class'],
                            'toggle': True
                        })
                    else:
                        raise PluginNoSupportException('{} no support {}'.format(plugin_name, type))
                else:
                    raise NoFoundPluginException('{} no found'.format(plugin_name))

        # 追加未开启的插件
        for name, plugin in plugins.items():
            for type in plugin['type']:
                if name not in config[type]:
                    # 添加未开启的插件信息
                    hook.plugins.setdefault(type, []).append({
                        'name': name,
                        'plugin_class': plugin['plugin_class'],
                        'toggle': False
                    })
