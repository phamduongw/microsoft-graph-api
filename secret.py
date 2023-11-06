import requests


def getData(url, vault_token):
    headers = {"X-Vault-Token": vault_token}

    response = requests.get(url, headers=headers)

    return response.json()["data"]
