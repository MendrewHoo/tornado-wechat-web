#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymongo, yaml, sys , time

sys.path.append('..')
from util.function import hash

def createAdmin(db):
    userid = input('input admin userid: ')
    password = input('input admin password: ')
    password = hash.get(password)
    user = {
        'userid': userid,
        'password': password,
        'power': 20,
        'registertime': time.time(),
        'faceurl': '/static/assets/img/user04.png'
    }
    member = db.admin.insert(user)
    print(member)

def create_index(db):
    db.admin.create_index('userid', unique = True)

if __name__ == '__main__':
    try:
        with open('../config.yaml', 'r') as fin:
            config = yaml.load(fin)
    except:
        print('cannot find config file')
        sys.exit(0)

    dbset = config['database']
    client = pymongo.MongoClient(dbset['config'])
    db = client[dbset['db']]
    isdo = input('create a admin user(Y/n): ')
    if isdo not in ('N', 'n'):
        createAdmin(db)
    create_index(db)
