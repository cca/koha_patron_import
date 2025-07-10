import os

import requests
from requests.exceptions import HTTPError

from .config import config


# ByWater's SSL cert used to cause problems, this allows a workaround
verify: bool = bool(os.environ.get("SSL_VERIFY", True))


def get_token() -> str | None:
    """Acquire an OAuth token for Koha

    returns: OAuth token (str) or None if an error occurs"""
    data: dict[str, str] = {
        "client_id": config["client_id"],
        "client_secret": config["client_secret"],
        "grant_type": "client_credentials",
    }
    response: requests.Response = requests.post(
        config["api_root"] + "/oauth/token", data=data, verify=verify
    )
    try:
        response.raise_for_status()
    except HTTPError:
        """log info about HTTP error"""
        print(f"HTTP {response.status_code} Error")
        for name, value in response.headers.items():
            print(f"{name}: {value}")
        print(response.text)
        return None
    token = str(response.json()["access_token"])
    return token
