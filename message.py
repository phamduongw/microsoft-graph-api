import requests
import json


def sendAttachment(
    accessToken, chatIds, attachmentId, attachmentURL, attachmentName, gitUrl, gitCommit
):
    gitCommitURL = f'{gitUrl.split(".git")[0]}/commit/{gitCommit}'
    gitRepository = f'{gitUrl.split("/")[-1].split(".")[0]}/{gitCommit}'

    headers = {
        "Authorization": f"Bearer {accessToken}",
        "Content-Type": "application/json",
    }

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


def sendErrorMessage(accessToken, chatIds, jobName, jenkinsUrl, buildId):
    job = jobName.split("/")
    log = f"{jenkinsUrl}/job/{job[0]}/job/{job[1]}/{buildId}/console"

    headers = {
        "Authorization": f"Bearer {accessToken}",
        "Content-Type": "application/json",
    }

    message = {
        "body": {
            "contentType": "html",
            "content": f'❌ CI/CD Pipeline ❌<br/>- Job: <a href="{log}" target=_blank>{jobName}/{buildId}</a><br/>- Status: <span style="color:red;">FAILED</span/>',
        },
    }

    payload = json.dumps(message)

    for chatId in chatIds:
        url = f"https://graph.microsoft.com/v1.0/chats/{chatId}/messages"
        response = requests.post(url, headers=headers, data=payload)

        if response.status_code == 401:
            return False

    return True
