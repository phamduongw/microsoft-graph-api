import sys
import requests

from localStoragePy import localStoragePy
from secret import getData
from message import sendErrorMessage

localStorage = localStoragePy("microsoft-graph-api")

VAULT_URL = sys.argv[1]
VAULT_TOKEN = sys.argv[2]
JOB_NAME = sys.argv[3]
JENKINS_URL = sys.argv[4]
BUILD_ID = sys.argv[5]

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


def main():
    params = (
        localStorage.getItem("accessToken"),
        CHAT_IDS,
        JOB_NAME,
        JENKINS_URL,
        BUILD_ID,
    )

    if not sendErrorMessage(*params):
        refreshAccessToken()
        sendErrorMessage(*params)


if __name__ == "__main__":
    main()
