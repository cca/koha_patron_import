#!/usr/bin/env python
"""
Usage: patch_prox_num.py <prox> <jsonfile>

Iterates over the user accounts in the provided JSON file (which can be a
student or employee export from Workday) and checks their prox number against
their cardnumber in Koha. If the numbers differ, updates the patron record.
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


# Universal IDs of patrons who should not have their prox numbers updated
# e.g. because the prox report seems to have the wrong number for them
PROX_EXCEPTIONS = ["1458769"]


def create_prox_map(proxfile):
    """Create a dict of { CCA ID : prox number } so we can look up patrons'
    card numbers by their ID. Prox report does not have other identifiers like
    username or email so we use CCA (universal, not student) ID.

    Args:
        proxfile (str|Path): path to the prox report CSV

    Raises:
        RuntimeError: if the CSV is not in the expected format

    Returns:
        dict: map of CCA IDs to prox numbers
    """
    with open(proxfile, mode="r") as file:
        # check the first line, which we'll always skip, to ensure CSV format
        first_line = file.readline()
        if "List of Changed Secondary Account Numbers" in first_line:
            # skip the first 3 lines ("List of", empty line, then header row)
            file.readline()
            file.readline()
        elif (
            '"Universal ID","Prox ID","Student ID","Last Name","First Name"'
            in first_line
        ):
            # we already skipped the header row
            pass
        else:
            raise RuntimeError(
                f'The CSV of prox numbers "{proxfile}" was in an unexpected format. It should be a CSV export from OneCard either unmodified or with the two preamble rows removed but the header row present. Double-check the format of the file.'
            )
        # read rows from the rest of the CSV
        reader = csv.reader(file)
        # Universal ID => prox number mapping
        # Prox report Univ IDs have varying number of leading zeroes e.g.
        # "001000001", "010000001", so we strip them
        map = {
            rows[0].lstrip("0"): rows[1].lstrip("0").rstrip()
            for rows in reader
            if int(rows[1]) != 0
        }
        return map


def log_http_error(response, workday, prox):
    """log info about HTTP error"""
    totals["error"] += 1
    print(colored("Error", "red"), response)
    print("HTTP Response Headers", response.headers)
    print(response.text)
    print(
        colored(
            f"""Error for patron {workday['username']} """
            f"""({workday['first_name']} {workday['last_name']}) with prox """
            f"""number {prox}"""
        ),
        "red",
    )


def update_patron(koha, workday, prox):
    print(
        f"""Updating cardnumber for {koha['userid']} ({koha['firstname']} """
        f"""{koha['surname']}, borrowernumber {koha['patron_id']})"""
    )

    # backup old cardnumber in "sort2" field
    koha["statistics_2"] = koha["cardnumber"]
    # koha['phone'] = koha['phone'] or workday.get('work_phone') or workday.get('mobile_phone', '')
    koha["cardnumber"] = prox
    # must do this or PUT request fails b/c we can't edit these fields
    for field in PATRON_READ_ONLY_FIELDS:
        koha.pop(field, None)

    response = http.put(
        "{}/patrons/{}".format(
            config["api_root"],
            koha["patron_id"],
        ),
        json=koha,
    )

    try:
        response.raise_for_status()
    except HTTPError:
        log_http_error(response, workday, prox)
        return False

    totals["updated"] += 1
    return True


def missing_patron(workday):
    totals["missing"] += 1
    print(
        'Could not find any patrons with a userid of "{}"'.format(workday["username"])
    )
    missing.append(workday)


def prox_unchanged(wd):
    totals["prox unchanged"] += 1
    print(
        f"Prox number unchanged for {wd['first_name']} {wd['last_name']} ({wd['username']})"
    )


def no_prox(wd):
    totals["no prox"] += 1
    print(
        f"""{wd['first_name']} {wd['last_name']} ({wd['username']}) has """
        f"""universal ID {wd['universal_id']} and no prox number"""
    )


def check_prox(workday, prox):
    """Try to find Koha account given WD profile. If cardnumber and prox don't
    match, pass the new prox num to update_patron(koha, wd, prox).

    Args:
        workday (dict): Workday object of personal info
        prox (int): card number
    """
    response = http.get(
        "{}/patrons?userid={}&_match=exact".format(
            config["api_root"],
            workday["username"],
        )
    )
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
            if patrons[0]["cardnumber"] == prox:
                prox_unchanged(workday)
            else:
                update_patron(patrons[0], workday, prox)


def is_contractor(wd):
    return (
        wd.get("etype", None) == "Contingent Employees/Contractors"
        or wd.get("job_profile", None) == "Temporary System/Campus Access"
        or False
    )


def mk_missing_file(missing):
    """write missing patrons to JSON file so we can add them later

    Args:
        missing (list): list of workday people objects
    """
    mfilename = f"{date.today().isoformat()}-missing-patrons.json"
    # filter out temp/contractor positions
    missing = [m for m in missing if not is_contractor(m)]
    with open(mfilename, "w") as file:
        json.dump(missing, file, indent=2)
        print(f"Wrote {len(missing)} missing patrons to {mfilename}")


def main(arguments):
    # global vars that other functions need to access
    global missing
    missing = []
    global totals
    totals = {"missing": 0, "error": 0, "updated": 0, "no prox": 0, "prox unchanged": 0}
    global http
    http = request_wrapper()

    prox_map = create_prox_map(arguments["<prox>"])

    with open(arguments["<jsonfile>"], "r") as file:
        people = json.load(file)["Report_Entry"]

    for workday in people:
        if not workday["universal_id"] in PROX_EXCEPTIONS:
            if not workday["universal_id"] in prox_map:
                no_prox(workday)
            else:
                check_prox(workday, prox_map[workday["universal_id"]])

    if len(missing) > 0:
        mk_missing_file(missing)


if __name__ == "__main__":
    arguments = docopt(__doc__, version="Patch Prox Number 1.1")
    main(arguments)
    print(
        f"""
Summary:
    - Updated Patrons: {totals['updated']}
    - No Prox number: {totals['no prox']}
    - Missing from Koha: {totals['missing']}
    - Errors: {totals['error']}
    - Prox unchanged: {totals['prox unchanged']}"""
    )
