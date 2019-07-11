# Bulk Import Patron Data into Koha ILS

CCA's outline of adding new patrons before the semester:

- Run Informer report to get new student list in CSV format
- Use "create-student-csv.py" to convert the Informer output into Koha's CSV schema
- [Batch import the patron CSV](https://library-staff.cca.edu/cgi-bin/koha/tools/import_borrowers.pl) on Koha's staff side

## Setup

1. Set up a python virtual environment & install dependencies

```sh
> virtualenv . -p python3
> source bin/activate # enter virtualenv, do activate.fish for fish shell
> pip install -r requirements.txt
```

2. Obtain access to CCA Integrations data in Google Cloud (contact Integration Engineer). There should be JSON files present for employees, students, and courses for the following term.

## Details

Run Informer Report "LIB-EP New Students for ILS Import" & set the Start Term to the upcoming semester. In the CSV export, ensure **Columns Headers** is checked & that the **Multivalue Handler** is "List by comma". Then, on the command line, navigate to the directory with the "create-student-csv.py" script on it & run:

```
python create-student-csv.py -o output.csv -e 2016-12-14 input.csv
```

Where _output.csv_ is the name of the file you want created, _2016-12-14_ is the expiration date for the created patron records, & _input.csv_ is the Informer report used as input. All of this information is contained in the help flag of create-student-csv.py; run `python create-student-csv.py -h`. If your file names have spaces in them, you can wrap them in quotation marks.

Inside Koha's staff side, select **Tools** & then **[Import Patrons](https://library-staff.cca.edu/cgi-bin/koha/tools/import_borrowers.pl)**. Use the following settings:

- Import file is the CSV we just created
- "Field to use for record matching" is "Username"
- We can leave all of the default values blank
- "If matching record is already in the borrowers table:" should be "Ignore this one, keep the existing one" (the default)
- Select "Replace only included patron attributes" below that
- Click the **Import** button

After import, Koha informs you exactly how many patrons records were created, overwritten, & if any rows in the import CSV were malformed.

## Faculty details

Use the included "faculty.sql" query in the Portal integrations instance to retrieve a list of all faculty teaching this semester (update the `term_id` to the current term). Export the SQL query as a CSV, then trim off the header row. Finally, mimic the rest of the steps from the instructions for students above but using the "create-faculty-csv.py" script.

## Testing

Included is a sample CSV export from Informer which can be used for test runs. All of the test records have surnames that begin with "ZTEST" so after a successful test, one can easily remove all the fake records like so:

- run the [Test Patrons](https://library-staff.cca.edu/cgi-bin/koha/reports/guided_reports.pl?reports=62&phase=Run%20this%20report) report (just queries borrowers table `WHERE surname LIKE 'ZTEST%'`)
- click each patron's link to open their details tab
- select the **More** button & then **Delete**

## API

Koha has a budding REST API which already has a fully fledged `/patrons` endpoint. We should eventually migrate to creating new patrons via the API rather than CSV upload. You can read some rather sparse documentation at https://library-staff.cca.edu/api/v1/.html

To use the API:

- sign into the Koha staff side, find your patron record, go to **More** > **Manage API Keys**
- copy the included example.config.json file to config.json
- insert the client ID and secret into config.json (also edit the `api_root` if need be)
- run a script similar to add_patron.py (WIP)

It appears that one limitation of the API is that patron attributes cannot be created nor modified. We use this for student major and faculty department so that's a dealbreaker right now.

# LICENSE

[ECL Version 2.0](https://opensource.org/licenses/ECL-2.0)
