"""Deletes files involved in the patron load process."""

import os
from datetime import date

today: str = date.today().isoformat()

for file in [
    f"{today}-missing-employees.json",
    "employee_data.json",
    f"{today}-missing-students.json",
    "student_data.json",
    "student_pre_college_data.json",
    "patron_bulk_import.csv",
    "data/prox.csv",
]:
    try:
        os.remove(file)
        print(f"Deleted {file}")
    except FileNotFoundError:
        print(f"Couldn't find {file} to delete")
