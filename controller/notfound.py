#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .base import BaseHandler
from tornroutes import route

@route(r"/")
class IndexHandler(BaseHandler):
    def prepare(self):
        super().prepare()
        if self.power == 'admin':
            self.redirect('/manage/index')
        else:
            self.redirect('/login')

@route(r".*")
class NotFoundHandler(BaseHandler):

    def prepare(self):
        super().prepare()
        if self.power == 'admin':
            print('no-found')
            self.redirect('/manage/404')
        else:
            self.redirect('/login')