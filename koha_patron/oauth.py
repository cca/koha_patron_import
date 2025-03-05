import os

import requests

from .config import config


# ByWater's SSL cert used to cause problems, this allows a workaround
verify: bool = bool(os.environ.get("SSL_VERIFY", True))


def get_token():
    """Acquire an OAuth token for Koha

    returns: OAuth token (string)"""
    data = {
        "client_id": config["client_id"],
        "client_secret": config["client_secret"],
        "grant_type": "client_credentials",
    }
    response = requests.post(
        config["api_root"] + "/oauth/token", data=data, verify=verify
    )
    token = str(response.json()["access_token"])
    return token
