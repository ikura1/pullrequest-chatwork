# -*- coding: utf-8 -*-
from flask import Blueprint
from server import config
import requests


# apiをファイルごとに分割する場合、Blueprintを使う
# 大きくない場合、__init__に直接書いてしまっても良い
app = Blueprint('view', __name__)


@app.route('/', methods=['GET'])
def hello():
    return 'Hello, World'


@app.route('/test', methods=['POST'])
def send_message():
    base_url = config.BASE_URL
    room_id = config.ROOM_ID
    token = config.API_TOKEN

    message = ('[To:{user_id}] {user_name}さん\n'
               '{comment}\n'
               '{url}')

    post_message_url = '{0}/rooms/{1}/messages'.format(base_url, room_id)

    headers = {'X-ChatWorkToken': token}
    params = {'body': message}
    print(post_message_url, headers, params)
    r = requests.post(post_message_url,
                      headers=headers,
                      params=params)
    print(r)


if __name__ == '__main__':
    send_message()
