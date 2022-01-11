# Bulk Import Patron Data into Koha ILS

CCA's outline of adding new patrons before the semester:

- Download JSON from "CCA Integrations" Google Cloud
- Use "create_koha_csv.py" to convert the Informer output into Koha's CSV schema
- [Batch import the patron CSV](https://library-staff.cca.edu/cgi-bin/koha/tools/import_borrowers.pl) on Koha's staff side

Formerly, we used separate scripts for faculty and student accounts. The data source was also Informer reports (for students) and SQL queries on the Portal database (for faculty), but now we use integrations data from Workday.

## Setup

1. Set up a python virtual environment & install dependencies: `pipenv --three && pipenv shell
&& pipenv install`

1. Obtain access to CCA Integrations data in Google Cloud (contact the Integration Engineer). There should be JSON files present for employees, students, and courses for recent terms.

## Details

1. Download JSON files from Google Cloud to the root of this project e.g. `gsutil cp gs://int_files_source/employee_data.json . && gsutil cp gs://int_files_source/student_data.json .`. The script expects them to retain their names, "student_data.json" and "employee_data.json". Download the report of "Prox" (ID card) numbers and save it as "prox.csv" in the root of this project.

1. Check that there are no new student majors not represented in "koha_mappings.py". I wrote a shell script "new-programs.sh" (requires [jq](https://stedolan.github.io/jq/)) to parse the employee/student data and write all major/department values to text files in the data directory. You can diff the results of this against its last iteration to find any new or modified values.

1. Run the main script `python create_koha_csv.py -s 2021-12-14` where the `-s` parameter is the last day of the semester (see Portal's [Academic Calendar](https://portal.cca.edu/calendar)). The due dates for all account types (staff, student, faculty) are calculated based on this date. The script prints diagnostic messages for users with ambiguous accounts, often hourly or special programs instructors. We need to double check that these accounts either already exist or aren't needed.

1. In Koha's staff side, select **Tools** & then **[Import Patrons](https://library-staff.cca.edu/cgi-bin/koha/tools/import_borrowers.pl)**. Use the following settings:

    - Import file is the CSV we just created
    - **Create a patron list** (useful for reversing mistakes)
    - **Field to use for record matching** is "Username"
    - Leave all of the default values blank
    - Set **If matching record is already in the borrowers table:** to "Ignore this one, keep the existing one" and "Replace only included patron attributes" below that. These are the defaults.
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

# LICENSE

[ECL Version 2.0](https://opensource.org/licenses/ECL-2.0)
