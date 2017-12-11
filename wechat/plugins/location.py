#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .base import BasePlugin

__type__ = ("location_event",)
__className__ = "LocationPlugin"


class LocationPlugin(BasePlugin):
    name = "处理位置信息事件插件"
    description = "处理位置信息事件插件"
    version = "0.1"
    author = "Mendrew"

    async def run(self, msg=None):
        location_data = {
            'wechatid': msg.source,
            'latitude': msg.latitude,
            'longitude': msg.longitude,
            'precision': msg.precision
        }
        location = '%s,%s' % (msg.latitude, msg.longitude)
        bdmap_data = await self.request.httpapi.bdMapReverse(location)
        if bdmap_data['status'] is 0:
            result = bdmap_data['result']
            location_data['last_location'] = '%s %s %s' % (result['addressComponent']['province'],
                                                           result['addressComponent']['city'],
                                                           result['addressComponent']['district'])
            location_data['last_address'] = result['formatted_address']
        await self.request.db.wechat_user.update({
            'wechatid': msg.source
        }, {
            '$set': location_data
        })
