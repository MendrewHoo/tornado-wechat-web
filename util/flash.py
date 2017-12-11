#!/usr/bin/env python
# -*- coding: utf-8 -*-

class flash(dict):
    '''
    session 临时存储数据
    '''
    def __init__(self, request):
        super().__init__(self)
        self.request = request

    def __getitem__(self, item):
        item = 'flash_{}'.format(item)
        if item in self.request.session:
            value = self.request.session.get(item)
            self.request.session.delete(item)
        else:
            value = ''
        return value

    def get(self, k, d=None):
        return self.__getitem__(k)

    def __delattr__(self, item):
        item = 'flash_{}'.format(item)
        self.request.session.delete(item)

    def __setitem__(self, key, value):
        key = 'flash_{}'.format(key)
        self.request.session[key] = value