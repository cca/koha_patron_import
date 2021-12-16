import csv
import json

from requests.exceptions import HTTPError

from koha_patron.config import config
from koha_patron.patron import PATRON_READ_ONLY_FIELDS
from koha_patron.request_wrapper import request_wrapper


def create_prox_map(proxfile):
    # this assumes a nicely formed CSV with a single header row & no prologue
    with open(proxfile, mode='r') as infile:
        reader = csv.reader(infile)
        # skip header row
        next(reader)
        # Universal ID => prox number mapping
        # Prox report Univ IDs have varying number of leading zeroes e.g.
        # "001000001", "010000001", so we strip by casting to int & back to str
        map = {str(int(rows[0])): str(int(rows[1])) for rows in reader if int(rows[1]) != 0}
        return map


def update_patron(koha, workday, prox):
    print('Updating phone and cardnumber for {} {} (borrowernumber {})'.format(
        koha['firstname'],
        koha['surname'],
        koha['patron_id'],
    ))

    # backup old cardnumber in "sort2" field
    koha['statistics_2'] = koha['cardnumber']
    koha['phone'] = koha['phone'] or workday.get('work_phone') or workday.get('mobile_phone') or ''
    koha['cardnumber'] = prox
    # must do this or PUT request fails b/c we can't edit these fields
    for field in PATRON_READ_ONLY_FIELDS:
        koha.pop(field, None)

    response = http.put('{}/patrons/{}'.format(
        config['api_root'],
        koha['patron_id'],
    ), json=koha)

    try:
        response.raise_for_status()
    except HTTPError:
        totals["error"] += 1
        print('Error', response)
        print('HTTP Response Headers', response.headers)
        print(response.text)
        print('Error for patron {} ({} {}) with prox number {}'.format(
            workday['username']),
            workday['first_name'],
            workday['last_name'],
            prox
        )
        return False

    totals["updated"] += 1
    return True


def missing_patron(workday):
    totals["missing"] += 1
    print('Could not find any patrons with a userid of "{}"'.format(workday['username']))
    missing.append(workday)


def main():
    prox_map = create_prox_map('data/prox.csv')
    with open('data/student_data.json', 'r') as file:
        people = json.load(file)["Report_Entry"]

    # global vars that other functions need to access
    global missing
    missing = []
    global totals
    totals = { "missing": 0, "error": 0, "updated": 0, "no_prox": 0}
    global http
    http = request_wrapper()

    # uncomment the next line to test on just Libraries staff
    # people = [p for p in people if p.get('department', None) == 'Libraries']
    for workday in people:
        if workday['universal_id'] in prox_map:
            prox = prox_map[workday['universal_id']]
            response = http.get('{}/patrons?userid={}'.format(
                config['api_root'],
                workday['username'],
            ))
            try:
                response.raise_for_status()
            except HTTPError:
                totals["error"] += 1
                print('Error', response)
                print('HTTP Response Headers', response.headers)
                print(response.text)
                print('Error for patron {} ({} {}) with prox number {}'.format(
                    workday['username'],
                    workday['first_name'],
                    workday['last_name'],
                    prox,
                ))
            patrons = response.json()

            # patrons is a dict if we had an error above, list otherwise
            if type(patrons) == list:
                if len(patrons) == 0:
                    missing_patron(workday)

                elif len(patrons) == 1:
                    update_patron(patrons[0], workday, prox)

                else:
                    # multiple patrons returned (e.g. look at results for userid = nchan
                    # which is a substring of another username)
                    patrons = [p for p in patrons if p['userid'] == workday['username']]
                    if len(patrons) == 0:
                        missing_patron(workday)
                    elif len(patrons) == 1:
                        update_patron(patrons[0], workday, prox)
                    else:
                        # this probably isn't possible...
                        raise Exception(('Found multiple patrons with the username "{}", '
                                        'something has gone horribly wrong. Patron records: {}')
                                        .format(workday['username'], patrons))

        else:
            totals["no_prox"] += 1
            print('{} {} ({}) has universal ID {} and no prox number'.format(
                workday['first_name'],
                workday['last_name'],
                workday['username'],
                workday['universal_id'],
            ))

    if len(missing) > 0:
        # write missing patrons to a file so we can add them later
        with open('missing-patrons.json', 'w') as file:
            json.dump(missing, file)

if __name__ == '__main__':
    main()
    print("Summary:\n\t- {}\n\t- {}\n\t- {}\n\t- {}".format(
        "Updated Patrons: " + str(totals["updated"]),
        "No Prox number: " + str(totals["no_prox"]),
        "Missing from Koha: " + str(totals["missing"]),
        "Errors: " + str(totals["error"]),
    ))
