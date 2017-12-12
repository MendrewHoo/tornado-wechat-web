#!/usr/bin/env python
# -*- coding: utf-8 -*-

import bcrypt, os, string, random, hashlib, time, re, tornado.escape, datetime, jieba, psutil


class hash:
    '''
    crypt哈希加密类
    '''

    @staticmethod
    def get(str):
        str = str.encode('utf-8')
        return bcrypt.hashpw(str, bcrypt.gensalt())

    @staticmethod
    def verify(str, hashed):
        str = str.encode('utf-8')
        return bcrypt.hashpw(str, hashed) == hashed


def not_need_login(func):
    '''
    修饰器, 修饰prepare方法, 使其不需要登录即可使用.
    :param func: prepare方法
    :return:  处理过的prepare方法
    '''

    def do_prepare(self, *args, **kwargs):
        before = self.current_user
        self.current_user = {'_id': 0, 'userid': 'guest', 'power': -1}
        func(self, *args, **kwargs)
        if before:
            self.current_user = before

    return do_prepare


def md5(string, encoding='utf-8'):
    '''
    计算简单的md5 hex格式字符串
    :param string: 原字符串
    :return: 返回32位hex字符串
    '''
    if isinstance(string, str):
        string = string.encode(encoding)
    m = hashlib.md5()
    m.update(string)
    return m.hexdigest()


def jieba2search(str):
    '''
    将字符串处理成搜索使用的字符串
    :param str:
    '''
    seg_list = jieba.cut_for_search(str)
    return '.*?'.join(seg_list)

def jieba2cut(str):
    '''
    将字符串分词成组
    :param str:
    '''
    return jieba.cut(str)

def humansize(file):
    '''
    计算文件大小并输出为可读的格式 (如 1.3MB)
    :param file: 文件路劲
    :return: 可读的文件大小
    '''
    if os.path.exists(file):
        nbytes = os.path.getsize(file)
        suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
        if nbytes == 0: return '0 B'
        i = 0
        while nbytes >= 1024 and i < len(suffixes) - 1:
            nbytes /= 1024.
            i += 1
        f = '{0:.2f}'.format(bcrypt).rstrip('0').rstrip('.')
        return '{} {}'.format(f, suffixes[i])
    else:
        return '未知'


def humantime(t=None, format='%Y-%m-%d %H:%M:%S', span=False):
    '''
    %y 两位数的年份表示（00-99）
	%Y 四位数的年份表示（000-9999）
	%m 月份（01-12）
	%d 月内中的一天（0-31）
	%H 24小时制小时数（0-23）
	%I 12小时制小时数（01-12）
	%M 分钟数（00=59）
	%S 秒（00-59）

	%a 本地简化星期名称
	%A 本地完整星期名称
	%b 本地简化的月份名称
	%B 本地完整的月份名称
	%c 本地相应的日期表示和时间表示
	%j 年内的一天（001-366）
	%p 本地A.M.或P.M.的等价符
	%U 一年中的星期数（00-53）星期天为星期的开始
	%w 星期（0-6），星期天为星期的开始
	%W 一年中的星期数（00-53）星期一为星期的开始
	%x 本地相应的日期表示
	%X 本地相应的时间表示
	%Z 当前时区的名称
	%% %号本身
    :param t: 时间戳, 默认当前时间
    :param format: 格式化字符串
    :param span: 是否计算间隔时间
    :return: 当前时间字符串
    '''
    if not t:
        t = time.time()
    if span:
        return time_span(t)
    date = datetime.datetime.fromtimestamp(t,
                                           datetime.timezone(datetime.timedelta(hours=8)))
    return date.strftime(format)


def time_span(ts):
    '''
    计算传入的时间戳与现在间隔的时间
    :param ts: 传入时间戳
    :return: 人性化时间差
    '''
    delta = datetime.datetime.now() - datetime.datetime.fromtimestamp(ts)
    if delta.days >= 365:
        return '{}年前'.format(delta.days // 365)
    elif delta.days >= 30:
        return '{}个月前'.format(delta.days // 30)
    elif delta.days > 0:
        return '{}天前'.format(delta.days)
    elif delta.seconds < 60:
        return '{}秒前'.format(delta.seconds)
    elif delta.seconds < 60 * 60:
        return '{}分钟前'.format(delta.seconds // 60)
    else:
        return '{}小时前'.format(delta.seconds // (60 * 60))


def random_str(randomlength=12):
    '''
    获得随机字符串, 包含所有大小写字母_数字
    :param randomlength: 字符串长度, 默认12
    :return: 随机字符串
    '''
    a = list(string.ascii_letters + string.digits)
    random.shuffle(a)
    return ''.join(a[:randomlength])


def intval(str):
    '''
    如php中的intval, 将字符串强制转换成数字
    :param str: 输入的字符串
    :return: 数字
    '''
    if type(str) is int: return str
    try:
        ret = re.match(r"^(\-?\d+)[^\d]?.*$", str).group(1)
        ret = int(ret)
    except:
        ret = 0
    return ret


def nl2br(str):
    '''
    转义一个字符串使它在HTML或XML中有效
    :param str: 需要转移的字符串
    :return: 转移过后的字符串
    '''
    str = tornado.escape.xhtml_escape(str)
    return str

def hidekey(key):
    '''
    隐藏 秘钥信息
    :param key:
    :return:
    '''
    tri_len = len(key) // 3
    return key[:tri_len] + '*'*tri_len + key[-tri_len:]


def dumpprint(obj):
    '''
    将对象处理成可打印对象, 用以调试
    :param obj: 处理对象
    :return: 可打印对象
    '''
    newobj = obj
    if '__dict__' in dir(obj):
        newobj = obj.__dict__
    if ' object at ' in str(obj):
        newobj['__type__'] = str(obj)
    for attr in newobj:
        newobj[attr] = dumpprint(newobj[attr])
    return newobj

def server_info_percent():
    '''
    返回服务器cpu, 内存, 磁盘占用率
    :return:
    '''
    cpu_percent = psutil.cpu_percent(interval=1)
    memory_percent = "%.1f" % ((psutil.virtual_memory().percent + psutil.swap_memory().percent) / 2)
    disk_percent = psutil.disk_usage('/').percent

    return cpu_percent, memory_percent, disk_percent