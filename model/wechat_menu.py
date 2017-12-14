#!/usr/bin/env python
# -*- coding: utf-8 -*-

from model.base import BaseModel

class WechatMenuModel(BaseModel):
    _table = 'wechat_menu'
    _needcheck = ('name', 'type')
    _invalid = {
        'name': {
            '_name': '菜单名',
            'type': str,
            'max_length': 36,
            'min_length': 1,
        },
        'type': {
            '_name': '菜单类型',
            'type': str,
            'in_list': ('supmenu', 'click', 'view')
        }
    }