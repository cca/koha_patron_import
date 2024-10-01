import requests

from .config import config


def get_token():
    """Acquire an OAuth token for Koha

    returns: OAuth token (string)"""
    data = {
        "client_id": config["client_id"],
        "client_secret": config["client_secret"],
        "grant_type": "client_credentials",
    }
    response = requests.post(
        config["api_root"] + "/oauth/token", data=data, verify=False
    )
    token = str(response.json()["access_token"])
    return token
