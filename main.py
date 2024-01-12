import re
import sys
import requests

from localStoragePy import localStoragePy
from secret import getData
from message import send, sendLogMessage

localStorage = localStoragePy("micrsoft-graph-api")

VAULT_URL = sys.argv[1]
VAULT_TOKEN = sys.argv[2]
ASSET_PATH = sys.argv[3]
GIT_URL = sys.argv[4]
GIT_COMMIT = sys.argv[5]

ASSET_NAME = None
try:
    ASSET_NAME = sys.argv[6]
except IndexError:
    ASSET_NAME = ASSET_PATH.split("/")[-1]

SECRET_DATA = getData(VAULT_URL, VAULT_TOKEN)
CHAT_IDS = SECRET_DATA["chat-ids"].split(",")


def updateToken(accessToken, refreshToken):
    localStorage.setItem("accessToken", accessToken)
    localStorage.setItem("refreshToken", refreshToken)


def getAccessToken():
    url = f"https://login.microsoftonline.com/{SECRET_DATA['tenant-id']}/oauth2/token"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }

    payload = {
        "grant_type": "password",
        "client_id": SECRET_DATA["client-id"],
        "client_secret": SECRET_DATA["client-secret"],
        "resource": "https://graph.microsoft.com",
        "username": SECRET_DATA["username"],
        "password": SECRET_DATA["password"],
    }

    response = requests.post(url, headers=headers, data=payload)
    data = response.json()

    updateToken(data["access_token"], data["refresh_token"])


def refreshAccessToken():
    if not localStorage.getItem("refreshToken"):
        return getAccessToken()

    url = f"https://login.microsoftonline.com/{SECRET_DATA['tenant-id']}/oauth2/v2.0/token"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }

    payload = {
        "grant_type": "refresh_token",
        "client_id": SECRET_DATA["client-id"],
        "client_secret": SECRET_DATA["client-secret"],
        "refresh_token": localStorage.getItem("refreshToken"),
    }

    response = requests.post(url, headers=headers, data=payload)
    data = response.json()

    print(response.text)

    updateToken(data["access_token"], data["refresh_token"])


def createUploadSession():
    url = f"https://graph.microsoft.com/v1.0/sites/{SECRET_DATA['site-id']}/drive/items/{SECRET_DATA['parent-id']}:/{ASSET_NAME}:/createUploadSession"

    headers = {"Authorization": f"Bearer {localStorage.getItem('accessToken')}"}

    responve = requests.post(url, headers=headers)

    if responve.status_code == 401:
        refreshAccessToken()
        return createUploadSession()

    return responve.json()["uploadUrl"]


def uploadFile():
    uploadUrl = createUploadSession()

    with open(ASSET_PATH, "rb") as file:
        fileData = file.read()

    headers = {
        "Authorization": f"Bearer {localStorage.getItem('accessToken')}",
        "Content-Length": str(len(fileData)),
        "Content-Range": "bytes 0-{}/{}".format(len(fileData) - 1, len(fileData)),
    }

    data = requests.put(uploadUrl, headers=headers, data=fileData).json()

    return {
        "id": re.search(r"{(.*?)}", data["eTag"]).group(1),
        "url": data["webUrl"],
    }


def main():
    attachment = uploadFile()

    send(
        localStorage.getItem("accessToken"),
        CHAT_IDS,
        attachment["id"],
        attachment["url"],
        ASSET_NAME,
        GIT_URL,
        GIT_COMMIT,
    )

    sendLogMessage(localStorage.getItem("accessToken"), CHAT_IDS, sys.argv[7])


if __name__ == "__main__":
    main()
