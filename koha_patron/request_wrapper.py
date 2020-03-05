import urllib3

import requests

from .oauth import get_token


# ByWater's SSL cert causes problems so every request has verify=False
# and we do this to silence printed warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def request_wrapper():
    # get a new OAuth token if there isn't one in the global namespace
    if not "token" in globals():
        global token
        token = get_token()
    headers = {
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
    }
    session = requests.Session()
    session.verify = False
    session.headers.update(headers)
    return session
