# -*- encoding: utf-8 -*-
import config
import json
import requests


CHAT_API_TOKEN = os.getenv('CHATWORKTOKEN', 'localhost')
CHAT_ROOM_ID = os.getenv('ROOM_ID_DEV', '4649')
CHAT_BASE_URL = 'https://api.chatwork.com/v2'
USERS = {'ikuda': {'id': '3081799', 'name': 'おくだ'},
         'yoshitaka_minami': {'id': '958229', 'name': 'みなみ'}
         }


def hello(request):
    return 'Hello, Functions'


def message_hello(request):
    send_message(request, [], 'Hello, ChatWork')
    return {'stats': True}


def pullrequest(request):
    request_json = request.get_json() if request else json.loads(JSON)
    if not request_json:
        return {'stats': False}
    if request_json['event'] != 'pullrequest:created':
        return {'stats': False}

    data = request_json['data']['pullrequest']
    repository = request_json['data']['repository']['name']
    actor_name = request_json['data']['actor']['username']
    description = data['description']
    title = data['title']
    reviewers = [user['username'] for user in data['reviewers']]
    url = data['links']['html']['href']
    destination_branch = data['destination']['branch']['name']
    source_branch = data['source']['branch']['name']

    mentions, message = create_message(actor_name, reviewers, repository,
                                       destination_branch, source_branch,
                                       title, description, url)
    # print(message)
    send_message(mentions, message)
    return


def create_message(actor_name, reviewers,
                   repository, destination_branch, source_branch,
                   title, description, url):
    mentions = [f'{{{user}}}' for user in reviewers]
    message = ['作成者:',
               f'    {{{actor_name}}}',
               'レポジトリ:',
               f'    {repository}',
               f'ブランチ:',
               f'    {source_branch} → {destination_branch}',
               f'タイトル:',
               f'    {title}',
               f'説明:',
               f'    {description}',
               f'url:',
               f'    {url}'
               ]
    return mentions, '\n'.join(message)


    base_url = CHAT_BASE_URL
    room_id = CHAT_ROOM_ID
    token = CHAT_API_TOKEN
    user_dict = USERS
    mention_template = '[To:{id}] {name}さん\n'
    mention_templates = {k: mention_template.format_map(v) for k, v in user_dict.items()}

    mention_text = ''.join([mention.format_map(mention_templates) for mention in mentions])
    message = message.format_map({k: v['name'] for k, v in user_dict.items()})
    message = mention_text + message
    post_message_url = '{0}/rooms/{1}/messages'.format(base_url, room_id)

    headers = {'X-ChatWorkToken': token}
    params = {'body': message}
    # print(post_message_url, headers, params)
    print(message)
    r = requests.post(post_message_url,
                      headers=headers,
                      params=params)
    return r
