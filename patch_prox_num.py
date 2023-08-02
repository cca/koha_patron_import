#!/usr/bin/env python
"""
Usage: patch_prox_num.py <prox> <jsonfile> [<old_prox>]

Iterates over the user accounts in the provided JSON file (which can be a
student or employee export from Workday) and, if their prox number isn't in
Koha, adds it. If you provide a previous iteration of the prox number report
then the script will only check the Koha record if we have a new prox number.
"""
import csv
from datetime import date
import json

from docopt import docopt
from requests.exceptions import HTTPError
from termcolor import colored

from koha_patron.config import config
from koha_patron.patron import PATRON_READ_ONLY_FIELDS
from koha_patron.request_wrapper import request_wrapper


def create_prox_map(proxfile):
    # this assumes a nicely formed CSV with a single header row & no prologue
    # @TODO check the file for the prologue & remove it if present
    with open(proxfile, mode='r') as infile:
        reader = csv.reader(infile)
        # skip header row
        next(reader)
        # Universal ID => prox number mapping
        # Prox report Univ IDs have varying number of leading zeroes e.g.
        # "001000001", "010000001", so we strip them
        map = {rows[0].lstrip("0"): rows[1].lstrip("0") for rows in reader if int(rows[1]) != 0}
        return map


def log_http_error(response, workday, prox):
    """ log info about HTTP error """
    totals["error"] += 1
    print(colored('Error', 'red'), response)
    print('HTTP Response Headers', response.headers)
    print(response.text)
    print(colored(f"""Error for patron {workday['username']} """
        f"""({workday['first_name']} {workday['last_name']}) with prox """
        f"""number {prox}"""), 'red')


def update_patron(koha, workday, prox):
    print(f"""Updating cardnumber for {koha['userid']} ({koha['firstname']} """
          f"""{koha['surname']}, borrowernumber {koha['patron_id']})""")

    # backup old cardnumber in "sort2" field
    koha['statistics_2'] = koha['cardnumber']
    # koha['phone'] = koha['phone'] or workday.get('work_phone') or workday.get('mobile_phone', '')
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
        log_http_error(response, workday, prox)
        return False

    totals["updated"] += 1
    return True


def missing_patron(workday):
    totals["missing"] += 1
    print('Could not find any patrons with a userid of "{}"'.format(workday['username']))
    missing.append(workday)


def prox_unchanged(wd):
    totals["prox unchanged"] += 1
    print(f"Prox number unchanged for {wd['first_name']} {wd['last_name']} ({wd['username']})")


def no_prox(wd):
    totals["no prox"] += 1
    print(f"""{wd['first_name']} {wd['last_name']} ({wd['username']}) has """
          f"""universal ID {wd['universal_id']} and no prox number""")


def prox_changed(workday, prox):
    """ we have a new or changed prox number for a patron, try to find their
    Koha account and pass the new prox num to update_patron(koha, wd, prox)

    Args:
        workday (dict): Workday object of personal info
        prox (int): card number
    """
    response = http.get('{}/patrons?userid={}'.format(
        config['api_root'],
        workday['username'],
    ))
    try:
        response.raise_for_status()
    except HTTPError:
        log_http_error(response, workday, prox)
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


def is_contractor(wd):
    return wd.get('etype', None) == 'Contingent Employees/Contractors' or wd.get('job_profile', None) == 'Temporary System/Campus Access' or False


def mk_missing_file(missing):
    """ write missing patrons to JSON file so we can add them later

    Args:
        missing (list): list of workday people objects
    """
    mfilename = f'{date.today().isoformat()}-missing-patrons.json'
    # filter out temp/contractor positions
    missing = [m for m in missing if not is_contractor(m)]
    with open(mfilename, 'w') as file:
        json.dump(missing, file, indent=2)
        print(f"Wrote {len(missing)} missing patrons to {mfilename}")


def main(arguments):
    # global vars that other functions need to access
    global missing
    missing = []
    global totals
    totals = { "missing": 0, "error": 0, "updated": 0, "no prox": 0}
    global http
    http = request_wrapper()

    prox_map = create_prox_map(arguments['<prox>'])
    if arguments['<old_prox>']:
        old_prox_map = create_prox_map(arguments['<old_prox>'])
        totals["prox unchanged"] = 0

    with open(arguments['<jsonfile>'], 'r') as file:
        people = json.load(file)["Report_Entry"]

    # uncomment the next line to test on just Libraries staff
    # people = [p for p in people if p.get('department', None) == 'Libraries']
    for workday in people:
        if not workday['universal_id'] in prox_map:
            no_prox(workday)
        else:
            prox = prox_map[workday['universal_id']]
            if old_prox_map and old_prox_map.get(workday['universal_id'], None) == prox:
                prox_unchanged(workday)
            else:
                prox_changed(workday, prox)

    if len(missing) > 0:
        mk_missing_file(missing)


if __name__ == '__main__':
    arguments = docopt(__doc__, version='Patch Prox Number 1.0')
    main(arguments)
    print(f"""
Summary:
    - Updated Patrons: {totals["updated"]}
    - No Prox number: {totals["no prox"]}
    - Missing from Koha: {totals["missing"]}
    - Errors: {totals["error"]}""")
    if totals.get("prox unchanged", False):
        print(f"""\
    - Prox unchanged: {totals['prox unchanged']}""")
