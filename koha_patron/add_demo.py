"""create patron record via Koha REST API"""

import os
from typing import Any

# import urllib3
import requests
from config import config

# ByWater's SSL cert used to cause problems, this silences printed warnings
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
verify: bool = bool(os.environ.get("SSL_VERIFY", True))


def get_oauth_token() -> str:
    """Acquire an OAuth token for Koha

    returns: OAuth token (string)"""
    data: dict[str, str] = {
        "client_id": config["client_id"],
        "client_secret": config["client_secret"],
        "grant_type": "client_credentials",
    }
    response: requests.Response = requests.post(
        config["api_root"] + "/oauth/token",
        data=data,
        verify=verify,
    )
    token = str(response.json()["access_token"])
    return token


def add_patron(patron, token: None | str) -> requests.Response:
    """Create a Koha Patron using the API

    patron: dict describing patron. Required to contain surname, address, city,
    library_id, category_id properties. We almost always want to add firstname,
    email, and userid as well.
    token: Oauth token (string)

    returns: HTTP response object from requests
    """
    if token is None:
        token = get_oauth_token()

    headers: dict[str, Any] = {
        "Accept": "application/json",
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json",
    }
    # TODO try/except block to work around OAuth token expiring
    response: requests.Response = requests.post(
        config["api_root"] + "/patrons",
        json=patron,
        headers=headers,
        verify=verify,
    )
    return response


# surname, address, city, library_id, category_id are all required
# this outlines, more or less, our idea of a minimum viable record
patron = {
    "address": "",
    "category_id": "STAFF",
    "city": "San Francisco",
    "email": "testy@cca.edu",
    "firstname": "Testy",
    "library_id": "SF",
    "state": "CA",
    "surname": "McTesterson",
    "userid": "testy",
}

token: str = get_oauth_token()
add_patron(patron, token)
print(f"Added patron {patron['firstname']} {patron['surname']} ({patron['userid']})")
