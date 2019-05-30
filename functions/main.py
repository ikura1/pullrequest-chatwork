# -*- encoding: utf-8 -*-
import os
import requests
import json
import emoji

CHAT_API_TOKEN = os.getenv("CHATWORKTOKEN", "localhost")
CHAT_ROOM_ID = os.getenv("ROOM_ID", "4649")
CHAT_BASE_URL = "https://api.chatwork.com/v2"
USERS = json.loads(os.getenv("USERS", "{}"))


def get_user_name(user_object):
    if "username" in user_object:
        return user_object["username"]
    if "account_id" in user_object and user_object["account_id"] in USERS:
        return user_object["account_id"]
    return f"{user_object.get('display_name')}: {user_object.get('account_id')}"


def manage_event(request):
    headers = request.headers
    request_json = request.get_json()
    event = headers.get("X-Event_Key")
    if not request_json:
        return "False"
    if event in ["pullrequest:created", "pullrequest:approved"]:
        mentions, message = pullrequest(event, request_json)
    elif event in ["repo:commit_status_updated"]:
        mentions, message = commit(request_json)
    else:
        return "False"
    message = emoji.emojize(message, use_aliases=True)
    return str(send_message(mentions, message))


def commit(request_json):
    commit_info = request_json["commit_status"]
    repository = request_json["repository"]["name"]
    commit_type = commit_info["type"]
    commit_state = commit_info["state"]
    author_name = get_user_name(commit_info["commit"]["author"]["user"])
    description = commit_info["description"]
    title = commit_info["name"]
    url = commit_info["url"]
    mentions, message = create_commit_message(
        author_name, repository, title, description, url, commit_type, commit_state
    )
    return mentions, message


def pullrequest(event, request_json):
    pullrequest_info = request_json["pullrequest"]
    repository = request_json["repository"]["name"]
    author_name = get_user_name(pullrequest_info["author"])
    description = pullrequest_info["description"]
    title = pullrequest_info["title"]
    reviewers = [get_user_name(user) for user in pullrequest_info["reviewers"]]
    url = pullrequest_info["links"]["html"]["href"]
    destination_branch = pullrequest_info["destination"]["branch"]["name"]
    source_branch = pullrequest_info["source"]["branch"]["name"]
    if event == "pullrequest:created":
        mentions, message = create_create_message(
            author_name,
            reviewers,
            repository,
            destination_branch,
            source_branch,
            title,
            description,
            url,
        )
    elif event == "pullrequest:approved":
        participants = {
            get_user_name(user["user"]): user["approved"]
            for user in pullrequest_info["participants"]
        }
        mentions, message = create_approval_message(
            author_name,
            reviewers,
            participants,
            repository,
            destination_branch,
            source_branch,
            title,
            url,
        )
    return mentions, message


def create_commit_message(
    author_name, repository, title, description, url, type_, state
):
    mentions = [f"{{{author_name}}}"] if author_name in USERS else [author_name]
    state_emoji = {
        "INPROGRESS": ":arrows_counterclockwise:",
        "SUCCESSFUL": ":white_check_mark:",
        "FAILED": ":x:",
    }
    info_list = [
        f"詳細: {description}",
        f"状況: {state}{state_emoji[state]}",
        f"url: {url}",
    ]
    info_message = "\n".join(info_list)
    message = (
        f"[info][title][{type_}]{repository}: {title}[/title]{info_message}[/info]"
    )
    return mentions, message


def create_approval_message(
    author_name,
    reviewers,
    participants,
    repository,
    destination_branch,
    source_branch,
    title,
    url,
):
    mentions = [f"{{{author_name}}}"] if author_name in USERS else [author_name]
    info_list = [
        f"レポジトリ: {repository}",
        f"ブランチ: {source_branch} → {destination_branch}",
        f"url: {url}",
    ]
    reviewers.extend([k for k, v in participants.items() if v and k not in reviewers])
    approval_stats = [
        f"{':+1:' if participants[user] else ':thinking_face:'} : {f'{{{user}}}'if user in USERS else user}"
        for user in reviewers
    ]

    info_list.extend(approval_stats)
    info_message = "\n".join(info_list)
    message = f"[info][title][プルリク]{title}[/title]{info_message}[/info]"
    return mentions, message


def create_create_message(
    author_name,
    reviewers,
    repository,
    destination_branch,
    source_branch,
    title,
    description,
    url,
):
    mentions = [f"{{{user}}}" if user in USERS else user for user in reviewers]
    info_list = [
        f"作成者: {{{author_name}}}" if author_name in USERS else f"作成者: {author_name}",
        f"レポジトリ: {repository}",
        f"ブランチ: {source_branch} → {destination_branch}",
        f"url: {url}",
    ]
    info_message = "\n".join(info_list)
    message = f"[info][title][プルリク]{title}[/title]{info_message}[/info]"
    return mentions, message


def send_message(mentions, message, room_id=None):
    if room_id is None:
        room_id = CHAT_ROOM_ID
    base_url = CHAT_BASE_URL
    token = CHAT_API_TOKEN
    user_dict = USERS
    mention_template = "[To:{id}] {name}さん"
    mention_templates = {
        k: mention_template.format_map(v) for k, v in user_dict.items()
    }

    mention_text = "\n".join(
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
    test_data = json.loads(open("../test_create_rp.json").read())
    c, m = pullrequest("pullrequest:created", test_data)
    print(emoji.emojize(m, use_aliases=True))

