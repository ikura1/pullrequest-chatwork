# -*- coding: utf-8 -*-
import os
# configファイル
API_TOKEN = os.getenv('CHATWORKTOKEN', 'localhost')
ROOM_ID = os.getenv('ROOMID', '4649')
BASE_URL = 'https://api.chatwork.com/v2'
USERS = {'hoge': {'id': '99', 'name': 'ほげ'},
         'hige': {'id': '88', 'name': 'ひげ'}
                 }