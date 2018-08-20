# -*- coding: utf-8 -*-
import os

# configファイル
# os.getenvで環境変数から取得にしているが、プライベートなら直接書いてしまっても良い
DEBUG = True

API_TOKEN = os.getenv('CHATWORKTOKEN', 'localhost')
ROOM_ID = os.getenv('ROOMID', '4649')
BASE_URL = 'https://api.chatwork.com/v2'
