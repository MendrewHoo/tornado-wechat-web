#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

class BaseModel:
    _table = ''
    _invalid = {}
    _msg = {
        "type": "{name}错误",
        "max_length": "{name}长度太长",
        "min_length": "{name}长度太短",
        "max": "{name}过大",
        "min": "{name}过小",
        "email": "{name}格式错误",
        "number": "{name}必须是数字",
        "url": "{name}格式错误",
        "pattern": "{name}格式错误",
        "in_list": "{name}不在预设范围内"
    }
    error_msg = ''
    _needcheck = ()
    def __call__(self, *args, **kwargs):
        '''
        校验数据是否符合设定
        '''
        data = args[0]
        for k, value in data.items():
            if k not in self._needcheck:
                continue
            for field, limit in self._invalid[k].items():
                if field[0] == '_': continue
                func = '_check_{}'.format(field)
                if hasattr(self, func):
                    ret = getattr(self, func)(limit, value)
                    if not ret:
                        self.error_msg = self._msg[field].format(name=self._invalid[k]['_name'])
                        return False
        return True

    def _check_type(self, valid, value):
        return type(value) is valid

    def _check_max_length(self, valid, value):
        return len(value) <= valid

    def _check_min_length(self, valid, value):
        return len(value) >= valid

    def _check_max(self, valid, value):
        return value <= valid

    def _check_min(self, valid, value):
        return value >= valid

    def _check_email(self, valid, value):
        return re.match(r"^(\w)+(\.\w+)*@(\w)+(\.\w+)+$", value)

    def _check_number(self, valid, value):
        return re.match(r"^\d+$", value)

    def _check_url(self, valid, value):
        return value.startswith('http://') or value.startswith('https://')

    def _check_pattern(self, valid, value):
        return re.match(valid, value)

    def _check_in_list(self, valid, value):
        return (value in valid)