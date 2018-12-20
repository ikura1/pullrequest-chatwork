# -*- encoding: utf-8 -*-
import os
import requests
import json

CHAT_API_TOKEN = os.getenv("CHATWORKTOKEN", "localhost")
CHAT_ROOM_ID = os.getenv("ROOM_ID_DEV", "4649")
CHAT_BASE_URL = "https://api.chatwork.com/v2"
USERS = json.loads(os.getenv("USERS", ""))


def pullrequest(request):
    headers = request.headers
    request_json = request.get_json()
    if headers.get("X-Event_Key") != "pullrequest:created":
        return "False"
    if not request_json:
        return "False"
    data = request_json["pullrequest"]
    repository = request_json["repository"]["name"]
    actor_name = request_json["actor"]["username"]
    description = data["description"]
    title = data["title"]
    reviewers = [user["username"] for user in data["reviewers"]]
    url = data["links"]["html"]["href"]
    destination_branch = data["destination"]["branch"]["name"]
    source_branch = data["source"]["branch"]["name"]
    mentions, message = create_message(
        actor_name,
        reviewers,
        repository,
        destination_branch,
        source_branch,
        title,
        description,
        url,
    )
    return send_message(mentions, message)


def create_message(
    actor_name,
    reviewers,
    repository,
    destination_branch,
    source_branch,
    title,
    description,
    url,
):
    mentions = [f"{{{user}}}" for user in reviewers]
    message = [
        "作成者: {{{actor_name}}}",
        "レポジトリ: {repository}",
        f"ブランチ: {source_branch} → {destination_branch}",
        f"タイトル: {title}",
        f"url: {url}",
    ]
    return mentions, "\n".join(message)


def send_message(mentions, message):
    base_url = CHAT_BASE_URL
    room_id = CHAT_ROOM_ID
    token = CHAT_API_TOKEN
    user_dict = USERS
    mention_template = "[To:{id}] {name}さん\n"
    mention_templates = {
        k: mention_template.format_map(v) for k, v in user_dict.items()
    }

    mention_text = "".join(
        [mention.format_map(mention_templates) for mention in mentions]
    )
    message = message.format_map({k: v["name"] for k, v in user_dict.items()})
    message = mention_text + message
    post_message_url = "{0}/rooms/{1}/messages".format(base_url, room_id)

    headers = {"X-ChatWorkToken": token}
    params = {"body": message}
    r = requests.post(post_message_url, headers=headers, params=params)
    return r
