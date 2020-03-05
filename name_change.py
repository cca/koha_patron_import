""" change a patron's name via the REST API """
import json
import urllib3

import requests


with open('config.json', 'r') as f:
    config = json.load(f)

# ByWater's SSL cert causes problems so every request has verify=False
# and we do this to silence printed warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

read_only_patron_fields = ("anonymized", "restricted")


def remove_readonly_fields(patron):
    for field in read_only_patron_fields:
        patron.pop(field, None)
    return patron


def get_token():
    """ Acquire an OAuth token for Koha

    returns: OAuth token (string) """
    data = {
        "client_id": config["client_id"],
        "client_secret": config["client_secret"],
        "grant_type": "client_credentials",
    }
    response = requests.post(config['api_root'] + '/oauth/token',
                    data=data, verify=False)
    token = str(response.json()['access_token'])
    return token


def name_change(patron_id, name, token=None):
    """ Change a Patron's name via the Koha API

    arguments:
        patron_id (int): patron's Koha ID (borrowernumber)
        name (dict): hash of new name values in this format
            { "firstname": "new firstname",
            "surname": "new surname" }
            You only need to provide changed name fields, not both.
        token (str): OAuth access token

    returns:
        HTTP response object from requests

    throws:
        HTTP exceptions from Requests
    """
    if token is None:
        token = get_token()

    headers = {
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
    }
    r = requests.get(config['api_root'] + '/patrons/{}'.format(str(patron_id)),
        headers=headers, verify=False)
    r.raise_for_status()
    patron = remove_readonly_fields(r.json())

    # edit name fields
    if name.get("firstname"):
        patron["firstname"] = name["firstname"]
    if name.get("surname"):
        patron["surname"] = name["surname"]

    response = requests.put(config['api_root'] + '/patrons/{}'.format(str(patron_id)),
        json=patron, headers=headers, verify=False)
    # response.raise_for_status()
    return response


if __name__ == '__main__':
    # "TEST Undergrad" patron
    # library-staff.cca.edu/cgi-bin/koha/members/moremember.pl?borrowernumber=14831
    token = get_token()
    r = name_change(14831, {"firstname": "TESTnewname", "surname": "Smith"}, token)
    print('Name changed, Koha API response:')
    print(r, r.status_code, r.text)
    print('Changing name back now...')
    # change it back
    name_change(14831, {"firstname": "TEST", "surname": "Undergrad"}, token)
