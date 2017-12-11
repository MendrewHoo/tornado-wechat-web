#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .base import BasePlugin
from util.function import jieba2cut

__type__ = ("receive_message", "click_event")
__className__ = "WeatherPlugin"

class WeatherPlugin(BasePlugin):
    name = "天气插件"
    description = "天气插件"
    version = "0.1"
    author = "Mendrew"

    weather_now_str = '{location}的实时天气\n{cond_txt} {wind_dir}, 当前温度 {tmp}℃, 体感温度 {fl}℃'
    weather_forecast_str = '{location}的明天天气\n/:sun{cond_txt_d} /:moon{cond_txt_n}, 温度在 {tmp_min}~{tmp_max}℃ 之间'

    async def run(self, msg=None):
        location = text = result = None
        # 作为预处理
        if msg.type == 'event' and msg.event == 'click' and msg.key[:7] == 'weather':
            event = msg.key
        elif msg.type == 'text':
            str_list = msg.content.split(' ', 1)
            if str_list[0] in ('天气', '天气预报'):
                if str_list[0] == '天气':
                    event = 'weather_now'
                else:
                    event = 'weather_forecast'
            else:
                return None
            if len(str_list) > 1:
                # 指定地址的查询 分割城市, 地区
                seg_list = jieba2cut(str_list[1])
                seg_list = [seg for seg in seg_list if seg not in (' ', ',', '，')]
                location = seg_list[1] if len(seg_list) == 2 else seg_list[0]
                results = await self.getweather(event, location)  # 城市获取多条
                result = results[0]
                # 指定城市地区的筛选
                if len(results) > 1 and len(seg_list) == 2:
                    for res in results:
                        if res['basic']['parent_city'] == seg_list[0]:
                            result = res
        else:
            return None

        # 没有指定location的查询将从数据库读取location信息
        if location is None:
            user = await self.request.db.wechat_user.find_one({
                'wechatid': msg.source
            })
            if user and 'latitude' in user:
                location = '%s,%s' % (user['latitude'], user['longitude'])
                result = await self.getweather(event, location)
                result = result[0]  # 坐标获取结果为一条
            else:
                text = '没有获取你的位置信息, 请同意分享位置信息或者输入\n"天气 地区"\n进行查询\n例如:\n天气 深圳南山'

        # 结果处理成回文
        if result and result['status'] == 'ok':
            location = result['basic']['parent_city']
            if location != result['basic']['location']:
                location += result['basic']['location']
            if event == 'weather_now':
                cond_txt = result['now']['cond_txt']
                tmp = result['now']['tmp']
                fl = result['now']['fl']
                wind_dir = result['now']['wind_dir']
                text = self.weather_now_str.format(location=location, cond_txt=cond_txt, tmp=tmp, fl=fl,
                                                   wind_dir=wind_dir)
            elif event == 'weather_forecast':
                cond_txt_d = result['daily_forecast'][1]['cond_txt_d']
                cond_txt_n = result['daily_forecast'][1]['cond_txt_n']
                tmp_min = result['daily_forecast'][1]['tmp_min']
                tmp_max = result['daily_forecast'][1]['tmp_max']
                text = self.weather_forecast_str.format(location=location, cond_txt_d=cond_txt_d, cond_txt_n=cond_txt_n,
                                                   tmp_min=tmp_min, tmp_max=tmp_max)
        else:
            text = '获取天气失败'
        return {'type': 'text', 'content': text}

    async def getweather(self, event, location):
        '''
        从api中获取天气情况
        :param event:
        :param location:
        :return:
        '''
        if event == 'weather_now':
            result = await self.request.httpapi.getHeWeather_now(location)
        elif event == 'weather_forecast':
            result = await self.request.httpapi.getHeWeather_forecast(location)
        else:
            return None
        return result['HeWeather6']
