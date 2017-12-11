#!/usr/bin/env python
# -*- coding: utf-8 -*-

plugins = {}

hook_info = {
    'receive_message': '接收文本信息处理',
    'click_event': '点击菜单事件处理',
    'scan_event': '扫描二维码处理',
    'subscribe_event': '关注事件处理',
    'location_event': '获取地理位置信息处理'
}

class Hook(object):
    @staticmethod
    async def listen(request, msg=None):
        '''
        可以通过msg
        '''
        hook_str = None
        if msg.type == 'text':
            hook_str = 'receive_message'
        elif msg.type == 'event':
            if msg.event == 'click':
                hook_str = 'click_event'
            elif msg.event in ('scan', 'subscribe_scan'):
                hook_str = 'scan_event'
            elif msg.event in ('subscribe', 'unsubscribe'):
                hook_str = 'subscribe_event'
            elif msg.event == 'location':
                hook_str = 'location_event'

        if hook_str and hook_str in plugins.keys():
            print(plugins)
            hook_list = plugins[hook_str]
            if isinstance(hook_list, list):
                for plugin in hook_list:
                    if plugin['toggle']:
                        plugin_class = plugin['plugin_class']
                        result = await plugin_class(request).run(msg)
                        if result:
                            return result
        else:
            return False