# -*- encoding: utf-8 -*-
import os
import requests
import json
import emoji

CHAT_API_TOKEN = os.getenv("CHATWORKTOKEN", "localhost")
CHAT_ROOM_ID = os.getenv("ROOM_ID", "4649")
CHAT_BASE_URL = "https://api.chatwork.com/v2"
USERS = json.loads(os.getenv("USERS", ""))


def pullrequest(request):
    target_events = ["pullrequest:created", "pullrequest:approved"]
    headers = request.headers
    request_json = request.get_json()
    event = headers.get("X-Event_Key")
    if not request_json:
        return "False"
    if event not in target_events:
        return "False"

    pullrequest_info = request_json["pullrequest"]

    repository = request_json["repository"]["name"]
    actor_name = request_json["actor"]["username"]
    description = pullrequest_info["description"]
    title = pullrequest_info["title"]
    reviewers = [user["username"] for user in pullrequest_info["reviewers"]]
    url = pullrequest_info["links"]["html"]["href"]
    destination_branch = pullrequest_info["destination"]["branch"]["name"]
    source_branch = pullrequest_info["source"]["branch"]["name"]
    if event == "pullrequest:created":
        mentions, message = create_create_message(
            actor_name,
            reviewers,
            repository,
            destination_branch,
            source_branch,
            title,
            description,
            url,
        )
    if event == "pullrequest:approved":
        participants = {
            user["username"]: user["approved"]
            for user in pullrequest_info["participants"]
        }
        mentions, message = create_approval_message(
            actor_name,
            reviewers,
            participants,
            repository,
            destination_branch,
            source_branch,
            title,
            url,
        )
    return str(send_message(mentions, message))


def create_approval_message(
    actor_name,
    reviewers,
    participants,
    repository,
    destination_branch,
    source_branch,
    title,
    url,
):
    mentions = [f"{{{actor_name}}}"]
    info_list = [
        f"レポジトリ: {repository}",
        f"ブランチ: {source_branch} → {destination_branch}",
        f"url: {url}",
    ]
    approval_stats = [
        f"{':+1:' if participants[user] else ':thinking_face:'} : {{{user}}}"
        for user in reviewers
    ]
    info_list.extend(approval_stats)
    info_message = "\n".join(info_list)
    message = f"[info][title][PullRequest]{title}[/title]{info_message}[/info]"
    return mentions, emoji.emojize(message, use_aliases=True)


def create_create_message(
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
    info_list = [
        f"作成者: {{{actor_name}}}",
        f"レポジトリ: {repository}",
        f"ブランチ: {source_branch} → {destination_branch}",
        f"url: {url}",
    ]
    info_message = "\n".join(info_list)
    message = f"[info][title][PullRequest]{title}[/title]{info_message}[/info]"
    return mentions, message


def send_message(mentions, message, room_id=None):
    if room_id is None:
        room_id = CHAT_ROOM_ID
    base_url = CHAT_BASE_URL
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


if __name__ == "__main__":
    print(USERS)
