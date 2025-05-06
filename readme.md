# Bulk Import Patron Data into Koha ILS

CCA's outline of adding new patrons before the semester:

- Download JSON from "CCA Integrations" Google Cloud
- Use "create_koha_csv.py" to convert the Informer output into Koha's CSV schema
- [Batch import the patron CSV](https://library-staff.cca.edu/cgi-bin/koha/tools/import_borrowers.pl) on Koha's staff side

## Setup

1. Install `gcloud` globally to get `gsutil` (`brew install google-cloud-sdk`)
1. Set up a python virtual environment & install dependencies: `uv install`
1. Obtain access to CCA Integrations data in Google Cloud (contact the Integrations Engineer). There should be JSON files present for employees, students, pre-college students, and courses for recent terms.
1. Obtain access to the "Active Accounts with Prox IDs" report in OneCard/TouchNet. Contact AIS <ais@cca.edu>.
1. Go to your Koha staff side, find your patron record, go to **More** > **Manage API Keys** and create a new key.
1. Copy koha_patron/example.config.py to koha_patron/config.py and fill in your API key's client ID and secret.

## Sync Names & Card Numbers

On a regular basis, we sync names from Workday and card number changes from the TouchNet report to Koha, so that patrons who changed their preferred names or lost or changed their CCA ID cards don't have to update their account themselves.

1. Download the latest report of active account prox numbers from TouchNet
1. Download Workday JSON files from Google Cloud with `uv run python koha_patron/dl_int_json.py`
1. Run `uv run ./patron_update.py -p prox_report.csv -w data.json | tee -a prox_update.log` where data.json is one of the (employee or student) Workday files.
1. The script prints status messages, a summary of what was updated, and creates a JSON file of patrons who are missing from Koha (which can be used in the step below).

## Loading New Patrons

Before each semester, we load new patron accounts using data sourced from Workday to create a CSV that's then batch loaded into Koha.

1. Download JSON files from Google Cloud with `uv run python koha_patron/dl_int_json.py`. For a summer term, get pre-college students too with `uv run python koha_patron/dl_int_json.py --pc`. Our scripts expect the JSON files to retain their names, e.g. "student_data.json". Download the report of "Prox" numbers (Custom Reports > "Accounts with Prox IDs").

1. Check that there are no new student majors not represented in "koha_mappings.py". The script "new-programs.sh" (requires [jq](https://stedolan.github.io/jq/)) parses the employee/student data and writes all major/department values to text files in the data directory, then it runs `git diff` against its own prior iterations.

1. Run the main script `uv run python create_koha_csv.py prox_report.csv --end 2023-12-12` where the CSV is the prox report and the `--end` parameter is the last day of the semester (see Portal's [Academic Calendar](https://portal.cca.edu/calendar)). Expiration dates for all account types (staff, student, faculty) are based on the end date. The script prints diagnostic messages for users with ambiguous accounts, often hourly or special programs instructors. We need to double check that these accounts either already exist or aren't needed.

1. On Koha's staff side, select **Tools** & then **[Import Patrons](https://library-staff.cca.edu/cgi-bin/koha/tools/import_borrowers.pl)**. Use the following settings:

    - Import file is the CSV we just created
    - **Create a patron list** (useful for reversing mistakes)
    - **Field to use for record matching** is "Username"
    - Leave all of the default values blank
    - Set **If matching record is already in the borrowers table:** to "Ignore this one, keep the existing one" and "Replace only included patron attributes" below that. These are the defaults.
    - Send the welcome email to new patrons
    - Click the **Import** button

After import, Koha informs you how many patrons were created & if any rows in the import CSV were malformed. You can copy the full text output of this page and save it into the data directory. You may need to check some duplicate card numbers; username changes not reflected in Koha is a common issue.

There's a `clean.py` script to delete the data files after the import is done.

## API

Koha has a REST API with a `/patrons` endpoint. Read its documentation at https://library-staff.cca.edu/api/v1/.html

We could use a script similar to koha_patron/add_demo.py (WIP) to add patrons to Koha one-by-one with the API rather than in bulk with a CSV. Rather than use two scripts, patron_update.py could simply create missing patrons on the fly.

The API previously had a limitation that patron extended attributes could not be created nor modified. We use attributes to record student major and faculty department, so that curbed the API's usefulness. Luckily, a new `/patron/{id}/extended_attributes` route (see [bug #23666](https://bugs.koha-community.org/bugzilla3/show_bug.cgi?id=23666)) was added in Koha 21.05. We use the API in the "patron_update.py" script to update existing patron records without overwriting them entirely.

If we do the logical thing of `GET`ting a patron record from the API, modifying it, then `PUT`ting it back, Koha throws an error because there are read-only fields in the record. Remove them before sending the record back:

```py
from koha_patron.patron import PATRON_READ_ONLY_FIELDS
for field in PATRON_READ_ONLY_FIELDS:
    patron.pop(field) # patron = dict of the patron record
```

## LICENSE

[ECL Version 2.0](https://opensource.org/licenses/ECL-2.0)
