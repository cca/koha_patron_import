# Bulk Import Patron Data into Koha ILS

CCA's outline of adding new patrons before the semester:

- Download JSON from "CCA Integrations" Google Cloud
- Use "create_koha_csv.py" to convert the Informer output into Koha's CSV schema
- [Batch import the patron CSV](https://library-staff.cca.edu/cgi-bin/koha/tools/import_borrowers.pl) on Koha's staff side

## Setup

1. Set up a python virtual environment & install dependencies: `pipenv install && pipenv shell`

1. Obtain access to CCA Integrations data in Google Cloud (contact the Integrations Engineer). There should be JSON files present for employees, students, and courses for recent terms.

1. Obtain access to the "Accounts with Prox IDs" report in OneCard/TouchNet. Contact AIS <ais@cca.edu>.

## Sync Card Number Changes

On a regular basis, we sync card number changes from the TouchNet report to Koha, so that patrons who lost or changed their CCA ID cards will be able to use the library without updating their account.

1. Download the latest report of prox numbers from TouchNet

1. Run `pipenv run ./patch_prox_num.py prox_report.csv data.json | tee -a prox_update.log` where data.json is one of the (employee or student) Workday data exports.

1. The script prints status messages, a summary of what was updated and possible problems, and creates a JSON file of patrons who are missing from Koha (which could then be used in the step below).

## Loading New Patrons

Before each semester, we load new patron accounts using data sourced from Workday to create a CSV that's then batch loaded into Koha.

1. Download JSON files from Google Cloud to the root of this project `gsutil cp gs://int_files_source/employee_data.json . && gsutil cp gs://int_files_source/student_data.json .`. For a summer term, also download pre-college data `gsutil cp gs://integration-success/student_pre_college_data.json .`. The script expects the JSON files to retain their names, e.g. "student_data.json". Download the report of "Prox" numbers (Custom Reports > "Accounts with Prox IDs").

1. Check that there are no new student majors not represented in "koha_mappings.py". The script "new-programs.sh" (requires [jq](https://stedolan.github.io/jq/)) parses the employee/student data and writes all major/department values to text files in the data directory, then it tries to `git diff` against its own prior iterations.

1. Run the main script `python create_koha_csv.py prox_report.csv --end 2023-12-12` where the CSV is Prox report and the `--end` parameter is the last day of the semester (see Portal's [Academic Calendar](https://portal.cca.edu/calendar)). Expiration dates for all account types (staff, student, faculty) are based on this. The script prints diagnostic messages for users with ambiguous accounts, often hourly or special programs instructors. We need to double check that these accounts either already exist or aren't needed.

1. In Koha's staff side, select **Tools** & then **[Import Patrons](https://library-staff.cca.edu/cgi-bin/koha/tools/import_borrowers.pl)**. Use the following settings:

    - Import file is the CSV we just created
    - **Create a patron list** (useful for reversing mistakes)
    - **Field to use for record matching** is "Username"
    - Leave all of the default values blank
    - Set **If matching record is already in the borrowers table:** to "Ignore this one, keep the existing one" and "Replace only included patron attributes" below that. These are the defaults.
    - Send the welcome email to new patrons
    - Click the **Import** button

After import, Koha informs you exactly how many patrons records were created, overwritten, & if any rows in the import CSV were malformed. You can copy the full text output of this page and save it into the data directory.

## API

Koha has a REST API with a `/patrons` endpoint. Read its documentation at https://library-staff.cca.edu/api/v1/.html

To use the API:

- sign into the Koha staff side, find your patron record, go to **More** > **Manage API Keys**
- copy koha_patron/example.config.py to koha_patron/config.py
- insert the client ID and secret into config.py (also edit the `api_root` if need be)
- run a script similar to add_patron.py (WIP)

The API previously had a limitation that patron extended attributes could not be created nor modified. We use attributes to record student major and faculty department, so that curbed the API's usefulness. Luckily, a new `/patron/{id}/extended_attributes` route (see [bug #23666](https://bugs.koha-community.org/bugzilla3/show_bug.cgi?id=23666)) was added in Koha 21.05. We used the API in the "patch_prox_num.py" script to update existing patron records with their prox numbers without overwriting them entirely.

## LICENSE

[ECL Version 2.0](https://opensource.org/licenses/ECL-2.0)
