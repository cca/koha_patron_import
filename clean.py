from datetime import date
import os

# ! this script is _very_ slow, maybe because of this import? Could copy-paste files dict instead
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
