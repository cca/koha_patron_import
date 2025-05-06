"""Deletes files involved in the patron load process."""

from datetime import date
import os

from create_koha_csv import files

today: str = date.today().isoformat()
files["prox"] = "data/prox.csv"
files["missing_employees"] = f"{today}-missing-employees.json"
files["missing_students"] = f"{today}-missing-students.json"

for file in files.values():
    try:
        os.remove(file)
        print(f"Deleted {file}")
    except:
        print(f"Couldn't find {file} to delete")
