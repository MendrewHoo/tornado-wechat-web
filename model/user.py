#!/usr/bin/env python
# -*- coding: utf-8 -*-

from model.base import BaseModel

class UserModel(BaseModel):
    _table = 'admin'
    _needcheck = ('userid')
    _invalid = {
        'userid': {
            '_name': '用户id',
            'type': str,
            'max_length': 36,
            'min_length': 1,
            'pattern': r"^[a-zA-z0-9_\-]+$",
        }
    }