#!/usr/bin/env python
import csv
import json
import subprocess
from datetime import date
from pathlib import Path
from typing import Any

import click
from requests import Response
from requests.exceptions import HTTPError
from rich.console import Console
from rich.progress import Progress

from koha_patron.config import config
from koha_patron.patron import PATRON_READ_ONLY_FIELDS
from koha_patron.request_wrapper import request_wrapper
from workday.models import Employee, Person, Student
from workday.utils import get_entries

console = Console()
# abstract over console.print vs progress.console.print so we can use one fn everywhere
println = console.print
# global var other functions update
results: dict[str, Any] = {
    "missing": [],
    "totals": {
        "missing": 0,
        "error": 0,
        "updated": 0,
        "unchanged": 0,
        "name change": 0,
        "prox change": 0,
    },
}


# Universal IDs of patrons who should not have their prox numbers updated
# e.g. because the prox report seems to have the wrong number for them
PROX_EXCEPTIONS: list[str] = ["1458769"]
NAME_EXCEPTIONS: list[str] = []  # not needed yet


def check_cca_dns() -> bool:
    """GlobalProect VPN adds 2 cca.edu DNS resolvers"""
    result = subprocess.run(["scutil", "--dns"], capture_output=True, text=True)
    return "cca.edu" in result.stdout


def create_prox_map(prox_file: str | Path) -> dict[str, str]:
    """Create a dict of { CCA ID : prox number } so we can look up patrons'
    card numbers by their ID. Prox report does not have other identifiers like
    username or email so we use CCA (universal, not student) ID.

    Args:
        prox_file (str|Path): path to the prox report CSV

    Raises:
        RuntimeError: if the CSV is not in the expected format

    Returns:
        dict: map of CCA IDs to prox numbers
    """
    with open(prox_file, mode="r") as file:
        # check the first line, which we'll always skip, to ensure CSV format
        first_line: str = file.readline()
        if "Active Accounts with Prox IDs" in first_line:
            # skip the first 3 lines ("List of", empty line, then header row)
            file.readline()
            file.readline()
        elif (
            '"Universal ID","Student ID","Prox ID","Last Name","First Name","End Date","IsInactive"'
            in first_line
        ):
            # we already skipped the header row
            pass
        else:
            raise RuntimeError(
                f'The CSV of prox numbers "{prox_file}" was in an unexpected format. It should be a CSV export from OneCard either unmodified or with the two preamble rows removed but the header row present. Double-check the format of the file.'
            )
        # read rows from the rest of the CSV
        reader = csv.reader(file)
        # Universal ID => prox number mapping
        # Prox report Univ IDs have varying number of leading zeroes e.g.
        # "001000001", "010000001", so we strip them
        map: dict[str, str] = {}
        for row in reader:
            # normalize IDs to be last 5 digits
            prox = row[2].rstrip()[4:]
            if prox != "" and int(prox) != 0:
                map[row[0].lstrip("0")] = prox
        return map


def handle_http_error(response: Response, workday: Person, prox: str | None) -> None:
    try:
        response.raise_for_status()
    except HTTPError:
        """log info about HTTP error"""
        results["totals"]["error"] += 1
        println("[bold red]Error[/bold red]", response)
        println("[dim]HTTP Response Headers[/dim]", response.headers)
        println(response.text)
        println(
            f"[bold red]Error for patron {workday.username} "
            f"({workday.first_name} {workday.last_name}) with prox "
            f"number {prox}[/bold red]"
        )


def missing_patron(workday: dict) -> None:
    println(
        f"[yellow]Could not find a patron with a userid of {workday['username']} in Koha.[/yellow]"
    )
    results["totals"]["missing"] += 1
    results["missing"].append(workday)


def has_changed(koha: dict, workday: Person, prox: str | None) -> bool:
    return (
        (prox and koha["cardnumber"] != prox)
        or koha["firstname"] != workday.first_name
        or koha["surname"] != workday.last_name
    )


def skipped_employee(wd: Employee) -> bool:
    return (
        wd.etype == "Contingent Employees/Contractors"
        or wd.job_profile == "Temporary System/Campus Access"
        or wd.job_profile == "Temporary: Hourly"
        or False
    )


def check_patron(workday: Person, prox: str | None, dry_run: bool):
    """Try to find Koha account given WD profile.
    If cardnumber or name have changed,
    pass the new prox num to update_patron(koha, wd, prox).

    Args:
        workday (dict): Workday object of personal info
        prox (int): card number
    """
    if not http:
        raise Exception("Failed to create HTTP session")
    response: Response = http.get(
        f"{config['api_root']}/patrons?userid={workday.username}&_match=exact"
    )
    handle_http_error(response, workday, prox)
    patrons: list | dict = response.json()

    # patrons is a dict if we had an error above, list otherwise
    if isinstance(patrons, list):
        if len(patrons) == 0:
            missing_patron(workday.model_dump(mode="json"))
        elif len(patrons) == 1:
            if has_changed(patrons[0], workday, prox):
                update_patron(patrons[0], workday, prox, dry_run)
            else:
                results["totals"]["unchanged"] += 1
        else:
            # theoretically impossible with _match=exact
            raise RuntimeError(
                f"Multiple patrons found for username {workday.username}: {patrons}"
            )


def update_patron(koha: dict, workday: Person, prox: str | None, dry_run: bool) -> None:
    message: str = f"[cyan]Updating {koha['userid']}[/cyan]"

    message += f" {koha['firstname']} {koha['surname']}"
    # name change
    if (
        koha["firstname"] != workday.first_name
        or koha["surname"] != workday.last_name
        and workday.universal_id not in NAME_EXCEPTIONS
    ):
        message += f" [bold]=> {workday.first_name} {workday.last_name}[/bold]"
        koha["firstname"] = workday.first_name
        koha["preferred_name"] = workday.first_name
        koha["surname"] = workday.last_name
        results["totals"]["name change"] += 1

    message += f" Cardnumber {koha['cardnumber']}"
    # new prox number
    if (
        prox
        and koha["cardnumber"] != prox
        and workday.universal_id not in PROX_EXCEPTIONS
    ):
        message += f" [bold]=> {prox}[/bold]"
        # backup old cardnumber in "sort2" field
        koha["statistics_2"] = koha["cardnumber"]
        koha["cardnumber"] = prox
        results["totals"]["prox change"] += 1

    println(message)

    # ! must do this or PUT request fails b/c we can't edit these fields
    for field in PATRON_READ_ONLY_FIELDS:
        koha.pop(field)

    if not dry_run:
        if http is None:
            raise Exception("Failed to create HTTP session")
        response: Response = http.put(
            "{}/patrons/{}".format(
                config["api_root"],
                koha["patron_id"],
            ),
            json=koha,
        )
        handle_http_error(response, workday, prox)

    results["totals"]["updated"] += 1


def mk_missing_file(missing: list[Person], ptype: str) -> None:
    """write missing patrons to JSON file so we can add them later

    Args:
        missing (list): list of workday people objects
    """
    filename: str = f"{date.today().isoformat()}-missing-{ptype.lower()}s.json"
    with open(filename, "w") as file:
        json.dump(missing, file, indent=2)
        console.print(
            f"[green]Wrote {len(missing)} missing patrons to {filename}[/green]",
            highlight=False,
        )


def load_data(filename: Path) -> list[Person]:
    people_dicts: list[dict] = []
    with open(filename, "r") as file:
        people_dicts: list[dict] = get_entries(json.load(file))

        # check first dict for id of only the particular type of Person
        if people_dicts[0].get("employee_id"):
            return [Employee(**p) for p in people_dicts]
        elif people_dicts[0].get("student_id"):
            return [Student(**p) for p in people_dicts]
        else:
            raise RuntimeError(
                f"Could not determine the type of person from the first entry in the JSON file {filename}."
            )


def summary(totals: dict[str, int]) -> None:
    console.print(
        f"""\n[bold cyan]=== Summary ===[/bold cyan]
[cyan]- Total patrons: {totals["unchanged"] + totals["updated"] + totals["missing"]}[/cyan]
[red]- Errors: {totals["error"]}[/red]
[yellow]- Missing from Koha: {totals["missing"]}[/yellow]
[green]- Updated: {totals["updated"]}[/green]
[cyan]- Name changes: {totals["name change"]}[/cyan]
[cyan]- Cardnumber changes: {totals["prox change"]}[/cyan]"""
    )


@click.command()
@click.help_option("--help", "-h")
@click.option(
    "-w",
    "--workday",
    help="Workday JSON file",
    required=True,
    type=click.Path(dir_okay=False, exists=True, readable=True),
)
@click.option(
    "-p",
    "--prox",
    help="Prox CSV file",
    required=False,
    type=click.Path(dir_okay=False, exists=True, readable=True),
)
@click.option(
    "-d",
    "--dry-run",
    help="Do not update patrons, only check for changes",
    is_flag=True,
)
@click.option("-l", "--limit", help="Limit the number of patrons to check", type=int)
def main(
    workday: Path,
    dry_run: bool,
    limit: None | int,
    prox: Path | None = None,
):
    global http, println, results

    # Koha blocks external API requests, ensure we're using the VPN
    if not check_cca_dns():
        if not click.confirm(
            "You don't appear to be on the CCA network or VPN. Continue?"
        ):
            exit()

    http = request_wrapper()

    if prox:
        prox_map: dict[str, str] = create_prox_map(prox)
    else:
        println(
            "[yellow]No prox file provided, cardnumbers will not be updated.[/yellow]"
        )
        prox_map = {}

    if dry_run:
        println("[yellow]Dry run: no changes will be made.[/yellow]")

    data: list[Person] = load_data(workday)

    with Progress() as progress:
        println = progress.console.print
        task = progress.add_task("[cyan]Checking patrons...", total=limit or len(data))
        for i, person in enumerate(data):
            if limit and i >= limit:
                break
            # skip temp/contractor positions and
            # incomplete students (username = id when they haven't chosen one yet)
            if (isinstance(person, Employee) and skipped_employee(person)) or (
                isinstance(person, Student) and not person.inst_email
            ):
                progress.update(task, advance=1)
                continue
            check_patron(person, prox_map.get(person.universal_id), dry_run=dry_run)
            progress.update(task, advance=1)

    if len(results["missing"]) > 0:
        mk_missing_file(results["missing"], type(data[0]).__name__)

    summary(results["totals"])


if __name__ == "__main__":
    main()
