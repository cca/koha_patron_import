"""
change a patron's name via the REST API
usage:
    python name_change.py changes.csv
"""
from koha_patron.config import config
from koha_patron.oauth import get_token
from koha_patron.request_wrapper import request_wrapper

# set a global OAUTH token that all requests can use
token = get_token()


def remove_readonly_fields(patron):
    """ remove readonly fields from patron dict
    must run patron records through this fn before PUTting to Koha """
    read_only_patron_fields = ("anonymized", "restricted", "updated_on")
    for field in read_only_patron_fields:
        patron.pop(field, None)
    return patron


def get_patron(username):
    """ Get a complete patron record given a username

    arguments:
        username (str): patron's Koha (same as CCA) username
    returns:
        patron (dict): patron dict from Koha API
    throws:
        HTTP exceptions from Requests
    """
    s = request_wrapper()
    # _match parameter can be "contains", "starts_with", "ends_with", or "exact"
    response = s.get('{}/patrons?userid={}&_match=exact'.format(config.api_root, username))
    # we cannot rfs because sometimes API returns 500 error when it should send an empty array
    # response.raise_for_status()
    data = response.json()
    if len(data["errors"]):
        print('Errors in Koha API response. It is likely that there is no patron with a "{}" username.'.format(username))
    if len(data) == 1:
        return data[0]
    else:
        # => len(response.json()) == 0
        print('No patron with username "{}".'.format(username))
        return None


def name_change(patron_id, name):
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
    s = request_wrapper()
    r = s.get(config.api_root + '/patrons/{}'.format(str(patron_id)))
    r.raise_for_status()
    patron = remove_readonly_fields(r.json())

    # edit name fields
    if name.get("firstname"):
        patron["firstname"] = name["firstname"]
    if name.get("surname"):
        patron["surname"] = name["surname"]

    response = s.put(config.api_root + '/patrons/{}'.format(str(patron_id)),
        json=patron)
    response.raise_for_status()
    return response


# CSV I've seen so far has rows named User ID,First Name - Proposed,Last Name - Proposed
def handle_csv_row(row):
    # row is a dict, "User ID" is formatted "username / Givenname Surname"
    patron = get_patron(row["User ID"].split(' / ')[0])
    if patron is not None:
        name_change(patron["patron_id"], {
            "firstname": row["First Name - Proposed"],
            "surname": row["Last Name - Proposed"]
        })
        print('Changed user #{} name "{} {}" => "{} {}"'.format(
            patron["patron_id"], patron["firstname"], patron["surname"],
            row["First Name - Proposed"], row["Last Name - Proposed"]
        ))


if __name__ == '__main__':
    import csv, sys
    if '.csv' in sys.argv[2]:
        filename = sys.argv[2]
        print('Processing rows in {} file...'.format(filename))
        with open(filename, 'r') as fh:
            for row in csv.DictReader(fh):
                handle_csv_row(row)
    else:
        # test change on "TEST Undergrad" patron
        # library-staff.cca.edu/cgi-bin/koha/members/moremember.pl?borrowernumber=14831
        r = name_change(14831, {"firstname": "TESTnewname", "surname": "Smith"})
        print('Name changed, Koha API response:')
        print(r, r.status_code, r.text)
        print('\nKoha patron record:')
        print(get_patron('stest1'))
        print('Changing name back now...')
        # change it back
        name_change(14831, {"firstname": "TEST", "surname": "Undergrad"})
        print('\nKoha patron record:')
        print(get_patron('stest1'))
