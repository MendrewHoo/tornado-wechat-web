#!/usr/bin/env python
# -*- coding: utf-8 -*-

import motor, sys, yaml, jinja2, redis
import tornado.log
from concurrent import futures
from tornado.options import define, options
from tornroutes import route, generic_route
from wechat.plugin_manager import PluginManager
from util.httpapi import HttpApi
from tornado_jinja2 import Jinja2Loader
from wechat.util.wechat_util import wechatUtil

define('port', default=7770, help='Run server on a specific port', type=int)
define('host', default='localhost', help='Run server on a specific host')
define('url', default=None, help='Url to show in HTML')
define('config', default='./config.yaml', help="config file's full path")
tornado.options.parse_command_line()

from tornado.platform import asyncio as todoasyncio

todoasyncio.AsyncIOMainLoop().install()

if not options.url:
    options.url = 'http://{}:{}'.format(options.host, options.port)

settings = {
    'base_url': options.url,
    'config_filename': options.config,
    'compress_response': True,
    'xsrf_cookies': False,
    'static_path': 'static',
    'template_path': 'templates',
    'session': {
        'driver': 'redis',
        'driver_settings': {
            'host': 'localhost',
            'prot': 6379,
            'db': 0
        },
        'force_persistence': False,
        'cache_driver': True,
        'session_lifetime': 1800,
        'cookie_config': {
            'httponly': True
        },
    },
    'thread_pool': futures.ThreadPoolExecutor(4)
}

# setting template engine is jinja2
jinja2_env = jinja2.Environment(loader=jinja2.FileSystemLoader(settings['template_path']), autoescape=False)
jinja2_loader = Jinja2Loader(jinja2_env)
settings['template_loader'] = jinja2_loader

# config file
config = {}
try:
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.load(f)
    settings.update(config['global'])
    # Token
    if 'wechat' in config and 'token' in config['wechat']:
        settings['wechat_token'] = config['wechat']['token']
    # session driver for redis
    if 'redis' in config and settings['session']['driver'] == 'redis':
        settings['session']['driver_settings'] = config['redis']
except Exception as e:
    print(e)
    print('cannot foround config.yaml file')
    sys.exit(0)

# httpapi
if 'apikey' in config:
    settings['httpapi'] = HttpApi(config['apikey'])

# mongodb connection
# format: mongodb://user:pass@host:port/
try:
    client = motor.MotorClient(config['database']['config'])
    database = client[config['database']['db']]
    settings['database'] = database
except:
    print('cannot connect mongodb, check the config.yaml')
    sys.exit(0)

# redis connection
# format: mongodb://user:pass@host:port/
try:
    redis = redis.Redis(**config['redis'], decode_responses=True)
    settings['redis'] = redis
except:
    print('cannot connect redis, check the config.yaml')
    sys.exit(0)

# wechat util init
try:
    wechat = wechatUtil(config['wechat']['appid'], config['wechat']['appsecret'], redis_client=redis)
    settings['wechat'] = wechat
except:
    print('cannot init wechat util, check the config.yaml')
    sys.exit(0)

# plugin init
try:
    plugin_manager = PluginManager().load_plugins(config['plugin_config'])
except Exception as e:
    print('Exception', e)
    print('cannot init plugin_manager, check the config.yaml')
    sys.exit(0)

from controller import *

application = tornado.web.Application(route.get_routes(), **settings)


# 修改log输出信息
class LogFormatter(tornado.log.LogFormatter):
    def __init__(self):
        super(LogFormatter, self).__init__(
            fmt='%(color)s[%(asctime)s %(filename)s:%(funcName)s:%(lineno)d %(levelname)s port:' + str(options.port) +
                ' %(levelname)s]%(end_color)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )


if __name__ == '__main__':
    try:
        application.listen(options.port)
        # [i.setFormatter(LogFormatter()) for i in logging.getLogger().handlers]
        tornado.ioloop.IOLoop.instance().start()
    except:
        import traceback

        print(traceback.print_exc())
    finally:
        sys.exit(0)
