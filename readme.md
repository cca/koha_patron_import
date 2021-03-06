# Bulk Import Patron Data into Koha ILS

CCA's outline of adding new patrons before the semester:

- Download JSON from "CCA Integrations" Google Cloud
- Use "create-koha-csv.py" to convert the Informer output into Koha's CSV schema
- [Batch import the patron CSV](https://library-staff.cca.edu/cgi-bin/koha/tools/import_borrowers.pl) on Koha's staff side

Formerly, we used separate scripts for faculty and student accounts. The data source was also Informer reports (for students) and SQL queries on the Portal database (for faculty), but now we use integrations data from Workday.

## Setup

1. Set up a python virtual environment & install dependencies: `pipenv --three && pipenv shell
&& pipenv install`

1. Obtain access to CCA Integrations data in Google Cloud (contact the Integration Engineer). There should be JSON files present for employees, students, and courses for recent terms.

## Details

1. Download JSON files from Google Cloud to the root of this project. The script expects them to retain their names, "student_data.json" and "employee_data.json".

1. Check that there are no new student majors not represented in "koha_mappings.py". I wrote a shell script "new-programs.sh" (requires [jq](https://stedolan.github.io/jq/)) to parse the employee/student data and write all major/department values to text files in the data directory. You can diff the results of this against its last iteration to find any new or modified values.

1. Run the main script `python create-koha-csv.py -s 2020-05-08 -e 2020-05-31` where the `-s` parameter is the expiration date for student records and `-e` is the one for employees.

1. Inside Koha's staff side, select **Tools** & then **[Import Patrons](https://library-staff.cca.edu/cgi-bin/koha/tools/import_borrowers.pl)**. Use the following settings:

    - Import file is the CSV we just created
    - **Create a patron list** this can be useful for reversing mistakes
    - **Field to use for record matching** is "Username"
    - Leave all of the default values blank
    - We want **If matching record is already in the borrowers table:** to be "Ignore this one, keep the existing one" and "Replace only included patron attributes" below that. These should be the defaults.
    - Click the **Import** button

After import, Koha informs you exactly how many patrons records were created, overwritten, & if any rows in the import CSV were malformed. You can copy the full text output of this page and save it into the data directory.

## Testing

Included is a sample CSV export from Informer which can be used for test runs. All of the test records have surnames that begin with "ZTEST" so after a successful test, one can easily remove all the fake records like so:

- run the [Test Patrons](https://library-staff.cca.edu/cgi-bin/koha/reports/guided_reports.pl?reports=62&phase=Run%20this%20report) report (just queries borrowers table `WHERE surname LIKE 'ZTEST%'`)
- click each patron's link to open their details tab
- select the **More** button & then **Delete**

## API

Koha has a budding REST API which already has a well-developed `/patrons` endpoint. You can read some documentation at https://library-staff.cca.edu/api/v1/.html

To use the API:

- sign into the Koha staff side, find your patron record, go to **More** > **Manage API Keys**
- copy the included example.config.json file to config.json
- insert the client ID and secret into config.json (also edit the `api_root` if need be)
- run a script similar to add_patron.py (WIP)

One limitation of the API is that patron extended attributes cannot be created nor modified. We use attributes to record student major and faculty department, so that greatly curbs the API's usefulness. Luckily, there was development recently (May, 2021) to add this functionality (see [bug #23666](https://bugs.koha-community.org/bugzilla3/show_bug.cgi?id=23666)) and it is included in Koha 21.05. We can revisit adding patrons via API when we upgrade, which should be early in 2022.

# LICENSE

[ECL Version 2.0](https://opensource.org/licenses/ECL-2.0)
