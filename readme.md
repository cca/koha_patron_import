# Bulk Import Patron Data into Koha ILS

CCA's outline of adding new patrons before the semester:

- Download JSON from "CCA Integrations" Google Cloud
- Use "create-koha-csv.py" to convert the Informer output into Koha's CSV schema
- [Batch import the patron CSV](https://library-staff.cca.edu/cgi-bin/koha/tools/import_borrowers.pl) on Koha's staff side

Formerly, we used separate scripts for faculty and student accounts. The data source was also Informer reports (for students) and SQL queries on the Portal database (for faculty), but now we use integrations data straight from Workday.

## Setup

1. Set up a python virtual environment & install dependencies

```sh
> virtualenv . -p python3
> source bin/activate # enter virtualenv, do activate.fish for fish shell
> pip install -r requirements.txt
```

1. Obtain access to CCA Integrations data in Google Cloud (contact Integration Engineer). There should be JSON files present for employees, students, and courses for the following term.

## Details

(WIP)

1. Download JSON files from Google Cloud to the root of this project. The script expects them to retain their exact names, "student_data.json" and "employee_data.json".

1. Run the script

```
python create-koha-csv.py -e 2019-12-15
```

where _2019-12-15_ is the expiration date for newly created patron records.

1. Inside Koha's staff side, select **Tools** & then **[Import Patrons](https://library-staff.cca.edu/cgi-bin/koha/tools/import_borrowers.pl)**. Use the following settings:

- Import file is the CSV we just created
- **Create a patron list** this can be useful for reversing mistakes
- **Field to use for record matching** is "Username"
- Leave all of the default values blank
- Set **If matching record is already in the borrowers table:** to "Ignore this one, keep the existing one" (the default)
- Select "Replace only included patron attributes" below that
- Click the **Import** button

After import, Koha informs you exactly how many patrons records were created, overwritten, & if any rows in the import CSV were malformed. Koha doesn't allow duplicate records and checks against two factors: username and the University ID patron attribute.

## Testing

Included is a sample CSV export from Informer which can be used for test runs. All of the test records have surnames that begin with "ZTEST" so after a successful test, one can easily remove all the fake records like so:

- run the [Test Patrons](https://library-staff.cca.edu/cgi-bin/koha/reports/guided_reports.pl?reports=62&phase=Run%20this%20report) report (just queries borrowers table `WHERE surname LIKE 'ZTEST%'`)
- click each patron's link to open their details tab
- select the **More** button & then **Delete**

## API

Koha has a budding REST API which already has a fully fledged `/patrons` endpoint. You can read some documentation at https://library-staff.cca.edu/api/v1/.html

To use the API:

- sign into the Koha staff side, find your patron record, go to **More** > **Manage API Keys**
- copy the included example.config.json file to config.json
- insert the client ID and secret into config.json (also edit the `api_root` if need be)
- run a script similar to add_patron.py (WIP)

One limitation of the API is that patron attributes cannot be created nor modified. We use this to record student major and faculty department, so that's a dealbreaker right now. We're also not in a position to fund this development, but it's worth keeping in mind should the situation change.

# LICENSE

[ECL Version 2.0](https://opensource.org/licenses/ECL-2.0)
