#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json, asyncio
from tornado.httpclient import AsyncHTTPClient
from tornado.httputil import url_concat
from tornado.platform import asyncio as todoasyncio
import urllib.parse, re
from util.function import md5

class HttpApi():

    def __init__(self, apikey):
        self.http_client = AsyncHTTPClient()
        self.apikey = apikey

    def __del__(self):
        self.http_client.close()

    async def getHeWeather_now(self, location, key=None):
        key = key if key else self.apikey['heweather']
        url = 'https://free-api.heweather.com/s6/weather/now?location={}&key={}'
        url = url.format(location, key)
        response = await todoasyncio.to_asyncio_future(self.http_client.fetch(url))
        return json.loads(response.body)

    async def getHeWeather_forecast(self, location, key=None):
        key = key if key else self.apikey['heweather']
        url = 'https://free-api.heweather.com/s6/weather/forecast?location={}&key={}'
        url = url.format(location, key)
        response = await todoasyncio.to_asyncio_future(self.http_client.fetch(url))
        print(response.body)
        return json.loads(response.body)

    async def bdMapReverse(self, location, key=None, sk=None):
        key = key if key else self.apikey['bdmap']
        sk = sk if sk else self.apikey['bdmap_sk']
        params = {
            'callback': 'renderReverse',
            'location': location,
            'output': 'json',
            'ak': key
        }
        url = 'http://api.map.baidu.com/geocoder/v2/'
        url = url_concat(url, params)
        # sn 方式验证
        sn = self.cal_bdsn(sk, url)
        url = url_concat(url, {'sn': sn})
        response = await todoasyncio.to_asyncio_future(self.http_client.fetch(url))
        re_body = response.body.decode('utf-8')
        json_data = re.search(r"^.*?\((.*)\)$", re_body).group(1)
        return json.loads(json_data)

    def cal_bdsn(self, sk, queryStr):
        '''
        bd计算sn值
        '''
        queryStr = urllib.parse.unquote(queryStr).replace('http://api.map.baidu.com', '')

        # 对queryStr进行转码，safe内的保留字符不转换
        encodedStr = urllib.parse.quote(queryStr, safe="/:=&?#+!$;'@()*[]")

        # 在最后直接追加上yoursk
        rawStr = encodedStr + sk

        # 计算sn
        return md5(urllib.parse.quote_plus(rawStr))
