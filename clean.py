"""Deletes files involved in the patron load process."""

import os
from datetime import date

from rich.console import Console

console = Console(highlight=False)
today: str = date.today().isoformat()

for file in [
    f"{today}-missing-employees.json",
    "employee_data.json",
    f"{today}-missing-students.json",
    "student_data.json",
    "patron_bulk_import.csv",
    "data/prox.csv",
]:
    try:
        os.remove(file)
        console.print("[bold green]Deleted[/bold green]", file)
    except FileNotFoundError:
        console.print("[red]Couldn't find[/red]", file, "to delete")
