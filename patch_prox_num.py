import csv
import json

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


prox_map = create_prox_map('prox.csv')
with open('employee_data.json', 'r') as file:
    people = json.load(file)["Report_Entry"]

missing = []
libraries = [p for p in people if p.get('department', None) == 'Libraries']
# libraries = [p for p in people if p.get('username') == 'ephetteplace']
print('There are {} Library staff.'.format(len(libraries)))
http = request_wrapper()


def update_patron(koha):
    print('Updating phone and cardnumber for {} {} (borrowernumber {})'.format(
        koha['firstname'],
        koha['surname'],
        koha['patron_id'],
    ))
    # @TODO this somehow sets everyone's birthday to the current date
    koha['phone'] = koha['phone'] or workday.get('work_phone') or workday.get('mobile_phone') or ''
    koha['cardnumber'] = prox
    # must do this or PUT request fails b/c we can't edit these fields
    for field in PATRON_READ_ONLY_FIELDS:
        koha.pop(field, None)
    response = http.put('{}/patrons/{}'.format(
        config['api_root'],
        koha['patron_id'],
    ), json=koha)
    response.raise_for_status()


def missing_patron(workday):
    print('Could not find any patrons with a userid of "{}"'.format(workday['username']))
    missing.append(workday)


# clarify where data is coming from/going to with dict names
for workday in libraries:
    if workday['universal_id'] in prox_map:
        prox = prox_map[workday['universal_id']]
        response = http.get('{}/patrons?userid={}'.format(
            config['api_root'],
            workday['username'],
        ))
        response.raise_for_status()
        patrons = response.json()

        if len(patrons) == 0:
            missing_patron(workday)

        elif len(patrons) == 1:
            update_patron(patrons[0])

        else:
            # multiple patrons returned (e.g. look at results for userid=nchan)
            patrons = [p for p in patrons if p['userid'] == workday['username']]
            if len(patrons) == 0:
                missing_patron(workday)
            elif len(patrons) == 1:
                update_patron(patrons[0])
            else:
                raise Exception('Found multiple patrons with the username "{}", something has gone horribly wrong. Patron records: {}'.format(workday['username'], patrons))

    else:
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
