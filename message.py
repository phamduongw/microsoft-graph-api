import requests
import json


def send(
    accessToken, chatIds, attachmentId, attachmentURL, attachmentName, gitUrl, gitCommit
):
    headers = {
        "Authorization": f"Bearer {accessToken}",
        "Content-Type": "application/json",
    }

    gitCommitURL = f'{gitUrl.split(".git")[0]}/commit/{gitCommit}'
    gitRepository = f'{gitUrl.split("/")[-1].split(".")[0]}/{gitCommit}'

    if "." in attachmentName:
        message = {
            "body": {
                "contentType": "html",
                "content": f'Latest build of <a href="{gitCommitURL}" target=_blank>{gitRepository}</a><attachment id="{attachmentId}"></attachment>',
            },
            "attachments": [
                {
                    "id": attachmentId,
                    "contentType": "reference",
                    "contentUrl": attachmentURL,
                    "name": attachmentName,
                }
            ],
        }
    else:
        message = {
            "body": {
                "contentType": "html",
                "content": f'<p>Latest build of <a href="{gitCommitURL}" target=_blank>{gitRepository}</p><a href="{attachmentURL}" target="_blank">Click here to download</a>',
            },
        }

    payload = json.dumps(message)

    for chatId in chatIds:
        url = f"https://graph.microsoft.com/v1.0/chats/{chatId}/messages"
        requests.post(url, headers=headers, data=payload)


def sendLogMessage(accessToken, chatIds, content):
    headers = {
        "Authorization": f"Bearer {accessToken}",
        "Content-Type": "application/json",
    }
    message = {
        "body": {
            "contentType": "html",
            "content": content,
        },
    }

    payload = json.dumps(message)

    for chatId in chatIds:
        url = f"https://graph.microsoft.com/v1.0/chats/{chatId}/messages"
        requests.post(url, headers=headers, data=payload)
