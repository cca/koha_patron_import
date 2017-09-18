#!/usr/bin/env python
"""
This script takes a CSV of faculty members, probably derived from portal stage,
and maps it into a format appropriate for import into Koha.

We should run once per semester just prior to the semester's
beginning. Note that a few things should be manually checked:

    - ensure mapping (faculty department) hasn't changed (see mapping.py)
    - look up last day of the semester (a week afterwards is the expiration date, captured in the "-e" flag when the script is run)
    - ensure CSV columns align the `reader_fields`
"""

import csv  # docs.python.org/2/library/csv.html
from mapping import fac_depts  # map Informer info into Koha codes
import datetime
import argparse  # docs.python.org/2.7/library/argparse.html

parser = argparse.ArgumentParser(
    description='Convert exported Informer report into Koha patron import CSV')
parser.add_argument('file', type=str, help='CSV from Informer')
parser.add_argument('-o', '--out', type=str, default='import.csv',
                    help='Name for output file')
# hard-coding in Fall 2016 expiration as default
parser.add_argument('-e', '--expiry', type=str, default='2016-12-16',
                    help='Patron record expiration date in ISO-8601 YYYY-MM-DD format')
args = parser.parse_args()

# used for dateenrolled later
today = datetime.date.today()

# CSV we're reading from
reader_fields = ['userid', 'firstname', 'surname', 'ID', 'program']
reader = csv.DictReader(open(args.file, 'r'), fieldnames=reader_fields)

# list of patron fields we'll populate initially
# see "koha_starter.csv" for the full list
writer_fields = ['cardnumber', 'surname', 'firstname', 'email', 'branchcode', 'categorycode', 'patron_attributes', 'dateenrolled', 'dateexpiry', 'userid']
writer = csv.DictWriter(open(args.out, 'w'), fieldnames=writer_fields)
writer.writeheader()

for row in reader:
    patron = {}  # will become row in output CSV

    # these are easy
    for key in ['userid', 'firstname', 'surname']:
        patron[key] = row[key]

    # we don't know barcode when we import, fill in University ID instead
    patron['cardnumber'] = row['ID']

    patron['email'] = row['userid'] + '@cca.edu'

    # everyone defaults to home branch = Oakland
    patron['branchcode'] = 'OAK'

    patron['categorycode'] = 'FACULTY'

    # patron attributes are formatted "KEY1:value,KEY2:value2"
    # we have at least 2 for every patron, always use University ID
    patron['patron_attributes'] = 'UNIVID:' + row['ID']

    # map Portal program to Koha faculty department
    dept_code = fac_depts.get(row['program'], None)
    if dept_code is not None:
        patron['patron_attributes'] += ',FACDEPT:' + str(dept_code)
    elif row['program'] != '' and row['program'] != 'All Faculty':
        print('I don\'t have a mapping for department %s for faculty %s'
        % (row['program'], patron['firstname'] + ' ' + patron['surname']))

    patron['dateenrolled'] = today.isoformat()
    patron['dateexpiry'] = args.expiry

    writer.writerow(patron)
