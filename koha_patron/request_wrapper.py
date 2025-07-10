import urllib3

import requests

from .oauth import get_token


# ByWater's SSL cert causes problems so every request has verify=False
# and we do this to silence printed warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def request_wrapper() -> requests.Session | None:
    token: str | None = get_token()
    if token:
        headers: dict[str, str] = {
            "Accept": "application/json",
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
        }
        session = requests.Session()
        session.verify = False
        session.headers.update(headers)
        return session
    return None
