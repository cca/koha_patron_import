#!/usr/bin/env python
"""
This script takes a CSV export from Informer and maps it
into a format appropriate for import into Koha.

We should run it once per semester just prior to the semester's
beginning. Note that a few things should be manually checked:

    - ensure mappings (patron category, studnet major) haven't changed (see mapping.py)
    - look up last day of the semester (this will account expiration date, which is captured in the "-e" flag when the script is run)
    - ensure Informer export column names are consistent with keys in the "row" dict (the script will throw exceptions if not)
"""

import csv  # docs.python.org/2/library/csv.html
from mapping import category, major  # map Informer info into Koha codes
import datetime
import argparse  # docs.python.org/2.7/library/argparse.html

parser = argparse.ArgumentParser(
    description='Convert exported Informer report into Koha patron import CSV')
parser.add_argument('file', type=str, help='CSV from Informer')
parser.add_argument('term', type=str, choices=['F', 'sp', 'Su', 'PC'],
                    help='Term or season of present semester')
parser.add_argument('-o', '--out', type=str, default='import.csv',
                    help='Name for output file')
# hard-coding in Fall 2016 expiration as default
parser.add_argument('-e', '--expiry', type=str, default='2016-12-16',
                    help='Patron record expiration date in ISO-8601 YYYY-MM-DD format')
args = parser.parse_args()

# used later to construct notes
today = datetime.date.today()
yr = str(today.year)[2:]

# files
reader = csv.DictReader(open(args.file, 'r'))
# list of patron fields we must/can populate initially
# see "koha_starter.csv" for the full list
fields = ['cardnumber', 'surname', 'firstname', 'othernames', 'email', 'branchcode', 'categorycode', 'patron_attributes', 'dateenrolled', 'dateexpiry', 'userid', 'contactnote']
writer = csv.DictWriter(open(args.out, 'w'), fieldnames=fields)
writer.writeheader()

for row in reader:
    patron = {}  # will become row in output CSV

    # we don't know barcode when we import, fill in University ID instead
    patron['cardnumber'] = row['ID']

    # standard 1-1 mappings
    patron['surname'] = row['Family Name']
    patron['firstname'] = row['Given Name']
    patron['othernames'] = row['Preferred Name']
    patron['email'] = row['CCA Email']  # will be empty for pre-college

    # everyone defaults to home branch = Oakland
    patron['branchcode'] = 'OAK'

    # patron attributes are formatted "KEY1:value,KEY2:value2"
    # we have at least 2 for every patron, always use University ID
    patron['patron_attributes'] = 'UNIVID:' + row['ID']
    # map Academic Level "GR", "UG" to appropriate patron category
    # work around fact that PRECO students have no "Academic Level" value
    programs = row['Programs'].split(', ')
    if 'PRECO' in programs:
        patron['categorycode'] = 'SPECIALSTU'  # pre-college student
    elif row['Academic Level'] in category:
        patron['categorycode'] = category[row['Academic Level']]
        # take first listed program & map to patron attribute authorized value
        patron['patron_attributes'] += ',STUDENTMAJ:' + str(major[programs[0]])
    else:
        raise Exception("Not pre-college & not a recognizable Academic Level, \
        I don't know what patron category to use!", row)

    patron['dateenrolled'] = today.isoformat()
    patron['dateexpiry'] = args.expiry

    # username is first part of "username@cca.edu" address
    # but pre-college students will not have a CCA email so use their ID number
    un = row['CCA Email'].split('@cca.edu')[0]
    if un == '':
        patron['userid'] = row['ID']
    else:
        patron['userid'] = un

    # note about expiration semester like "F16"
    # @TODO is "contactnote" the right field for this?
    patron['contactnote'] = args.term + yr

    writer.writerow(patron)
