#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .base import wechatBase

class wechatMenu(wechatBase):

    def create_menu(self):
        self.client.menu.create({
            "button": [
                {
                    "type": "click",
                    "name": "歌手简介",
                    "key": "V1001_TODAY_SINGER"
                },
                {
                    "name": "天气",
                    "sub_button": [
                        {
                            "type": "click",
                            "name": "实时天气",
                            "key": "weather_now"
                        },
                        {
                            "type": "click",
                            "name": "天气预报",
                            "key": "weather_forecast"
                        }
                    ]
                }
            ]
        })

