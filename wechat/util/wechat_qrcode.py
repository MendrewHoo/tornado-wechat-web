#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .base import wechatBase

login_qrcode = 'auth_login'
binding_qrcode = 'auth_binding'

class wechatQrcode(wechatBase):

    def create_qrcode(self, value, expire_seconds=1800):
        if isinstance(value, int):
            action_name = 'QR_SCENE'
            scene = {'scene_id': value}
        elif isinstance(value, str):
            action_name = 'QR_STR_SCENE'
            scene = {'scene_str': value}
        else:
            raise ValueError
        return self.client.qrcode.create({
            'expire_seconds': expire_seconds,
            'action_name': action_name,
            'action_info': {
                'scene': scene,
            }
        })

    def create_limit_qrcode(self, value):
        if isinstance(value, int):
            action_name = 'QR_LIMIT_SCENE'
            scene = {'scene_id': value}
        elif isinstance(value, str):
            action_name = 'QR_LIMIT_STR_SCENE'
            scene = {'scene_str': value}
        else:
            raise ValueError
        return self.client.qrcode.create({
            'action_name': action_name,
            'action_info': {
                'scene': scene,
            }
        })
