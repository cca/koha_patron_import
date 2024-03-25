#!/usr/bin/env python
"""
Usage:
    create_koha_csv.py <prox_report.csv> --end <YYYY-MM-DD>

Options:
    --end=DATE  last day of the semester in YYYY-MM-DD format

Converts JSON data from Workday into Koha patron import CSV. We run it once per
semester just prior start. A couple things should be manually checked:

- Ensure mappings haven't changed (see koha_mappings.py and new-programs.sh)
- Look up last day of the semester for --end flag

The JSON files from Workday come from the integration-success bucket and the
script expects them to be in the root and keep their names, but you can
override them with the following environment variables:
STUDENT_DATA=student_data.json
PRECOLLEGE_DATA=student_pre_college_data.json
EMPLOYEE_DATA=employee_data.json
OUTPUT_FILE=YYYY-MM-DD-koha-patrons.csv
"""
import csv
from datetime import date, timedelta
import json
from math import prod
import os

from docopt import docopt
from termcolor import colored

from koha_mappings import category, fac_depts, stu_major
from koha_patron.utils import trim_first_two_lines
from workday.models import Employee, Student

today = date.today()
files = {
    "student": os.environ.get("STUDENT_DATA", "student_data.json"),
    "precollege": os.environ.get("PRECOLLEGE_DATA", "student_pre_college_data.json"),
    "employee": os.environ.get("EMPLOYEE_DATA", "employee_data.json"),
    "output": os.environ.get("OUTPUT_FILE", f"{today.isoformat()}-koha-patrons.csv"),
}
print(files)


def create_prox_map(proxfile) -> dict[str, str]:
    # Prox report CSV is invalid with a title line & an empty line
    trim_first_two_lines(proxfile, "List of Changed Secondary Account Numbers")
    with open(proxfile, mode="r") as infile:
        reader = csv.reader(infile)
        next(reader)  # skip header row
        # Universal ID => prox number mapping
        # Numbers in prox report have a varying number of leading zeroes, e.g.
        # "001000001", "010000001", so we strip them out
        map = {
            rows[0].lstrip("0"): rows[1].lstrip("0")
            for rows in reader
            if int(rows[1]) != 0
        }
        return map


def warn(string) -> None:
    print(colored("Warning: " + string, "red"))


def is_exception(user: Employee | Student) -> bool:
    exceptions = ["deborahstein", "sraffeld"]
    if user.username in exceptions:
        return True
    return False


def make_student_row(student) -> dict | None:
    student = Student(**student)

    if is_exception(student):
        return None

    # some students don't have CCA emails, skip them
    # one student record in Summer 2021 lacked a last_name
    if student.inst_email is None or student.last_name is None:
        return None

    patron = {
        "branchcode": "SF",
        "categorycode": category[student.academic_level],
        # fill in Prox number if we have it, or default to UID
        "cardnumber": prox_map.get(student.universal_id, student.universal_id).strip(),
        "dateenrolled": today.isoformat(),
        "dateexpiry": args["--end"],
        "email": student.inst_email,
        "firstname": student.first_name,
        "patron_attributes": "UNIVID:{},STUID:{}".format(
            student.universal_id, student.student_id
        ),
        # "phone": student.get("phone", ""),
        "surname": student.last_name,
        "userid": student.username,
    }

    # note for pre-college and skip student major calculation
    if student.academic_level == "Pre-College":
        patron["borrowernotes"] = f"Pre-college {today.year}"
    else:
        # handle student major (additional patron attribute)
        major = None
        if student.primary_program in stu_major:
            major = str(stu_major[student.primary_program])
            patron["patron_attributes"] += ",STUDENTMAJ:{}".format(major)
        else:
            for program in student.programs:
                if program["program"] in stu_major:
                    major = str(stu_major[program["program"]])
                    patron["patron_attributes"] += ",STUDENTMAJ:{}".format(major)
                    break
        # we couldn't find a major, print a warning
        if major is None:
            warn(
                f"""Unable to parse major for student {student.username}
Primary program: {student.primary_program}
Program credentials: {student.programs}"""
            )

    return patron


def expiration_date(person: Employee) -> str:
    """Calculate patron expiration date based on personnel data and the last
    day of the semester.

    Parameters
    ----------
    person : dict
        Dict of user data. "etype" and "future_etype" are most important here.

    Returns
    -------
    str (in YYYY-MM-DD format)
        The appropriate expiration date as an ISO-8601 date string. For faculty
        added during Fall, this is Jan 31 of the next year. For faculty added
        during Spring, this is May 31 of the current year. For staff, it is the
        last day of the last month of the impending semester.

    """
    # there are 3 etypes: Staff, Instructors, Faculty. Sometimes we do not have
    # an etype but _do_ have a "future_etype".
    etype = person.etype or person.etype_future
    if not etype:
        warn(
            (
                "Employee {} does not have an etype nor a etype_future. They "
                "will be assigned the Staff expiration date.".format(person.username)
            )
        )
        etype = "Staff"
    d = date.fromisoformat(args["--end"])
    if etype == "Staff" or etype == "Instructors":
        # go into next month then subtract the number of days from next month
        next_mo = d.replace(day=28) + timedelta(days=4)
        return str(next_mo - timedelta(days=next_mo.day))
    else:
        # implies faculty
        # Spring => May 31
        if d.month == 5:
            return str(d.replace(day=31))
        # Fall => Jan 31 of the following year
        if d.month == 12:
            return str(d.replace(year=d.year + 1, month=1, day=31))
        # TODO how do we handle Summer?
        else:
            raise Exception("Summer expiration dates for faculty not implemented yet.")
    pass


def make_employee_row(person) -> dict | None:
    person = Employee(**person)

    if is_exception(person):
        return None

    # skip inactive, people w/o emails, & the one random record for a student
    if (
        not person.active_status
        or not person.work_email
        or person.etype in ("Contingent Employees/Contractors", "Students")
    ):
        return None

    # create a hybrid program/department field
    # some people have neither (tend to be adjuncts or special programs staff)
    prodep = None
    if person.program:
        prodep = person.program
    elif person.department:
        prodep = person.department
    elif person.job_profile in fac_depts:
        prodep = person.job_profile

    # skip inactive special programs faculty
    if person.job_profile == "Special Programs Instructor (inactive)":
        return None
    # skip contingent employees
    if person.is_contingent == "1":
        return None
    # we assume etype=Instructors => special programs faculty
    if (
        person.etype == "Instructors"
        and person.job_profile != "Special Programs Instructor"
        and person.job_profile != "Atelier Instructor"
        and person.job_profile not in fac_depts
    ):
        warn(
            (
                "Instructor {} is not a Special Programs Instructor, check " "record."
            ).format(person.username)
        )

    patron = {
        "branchcode": "SF",
        "categorycode": category.get(person.etype or person.etype_future or "Staff"),
        # fill in Prox number if we have it, or default to UID
        "cardnumber": prox_map.get(person.universal_id, person.universal_id).strip(),
        "dateenrolled": today.isoformat(),
        "dateexpiry": expiration_date(person),
        "email": person.work_email,
        "firstname": person.first_name,
        "patron_attributes": "UNIVID:" + person.universal_id,
        "phone": person.work_phone,
        "surname": person.last_name,
        "userid": person.username,
    }

    # handle faculty/staff department (additional patron attribute)
    if prodep and prodep in fac_depts:
        code = str(fac_depts[prodep])
        patron["patron_attributes"] += ",FACDEPT:{}".format(code)
    elif prodep:
        # there's a non-empty program/department value we haven't accounted for
        warn(
            """No mapping in koha_mappings.fac_depts for faculty/staff prodep
        "{}", see patron {}""".format(
                prodep, person.username
            )
        )

    if prodep is None:
        warn(
            "Employee {} has no academic program or department:".format(person.username)
        )
        print(person)

    return patron


def file_exists(fn) -> bool:
    if not os.path.exists(fn):
        warn(f'Did not find "{fn}" file')
        return False
    return True


def get_users(data) -> list[dict]:
    if type(data) == list:
        return data
    elif data.get("Report_Entry"):
        return data["Report_Entry"]
    else:
        raise Exception(
            "Could not find list of users in JSON data—are you sure this is the right file?"
        )


def proc_students(pc=False) -> None:
    if pc:
        file = files["precollege"]
        prefix = " pre-college "
    else:
        file = files["student"]
        prefix = " "

    if file_exists(file):
        print(f"Adding{prefix}students to Koha patron CSV.")
        with open(file, "r") as file:
            students = get_users(json.load(file))
            with open(files["output"], "a") as output:
                writer = csv.DictWriter(output, fieldnames=koha_fields)
                for stu in students:
                    row = make_student_row(stu)
                    if row:
                        writer.writerow(row)


def proc_staff() -> None:
    if file_exists(files["employee"]):
        print("Adding Faculty/Staff to Koha patron CSV.")
        with open(files["employee"], "r") as file:
            employees = get_users(json.load(file))
            # open in append mode & don't add header row
            with open(files["output"], "a") as output:
                writer = csv.DictWriter(output, fieldnames=koha_fields)
                for employee in employees:
                    row = make_employee_row(employee)
                    if row:
                        writer.writerow(row)


def main() -> None:
    # write header row
    with open(files["output"], "w+") as output:
        writer = csv.DictWriter(output, fieldnames=koha_fields)
        writer.writeheader()
    proc_students()
    proc_students(pc=True)
    proc_staff()

    print(
        "Done! Upload the CSV at "
        "https://library-staff.cca.edu/cgi-bin/koha/tools/import_borrowers.pl"
    )


if __name__ == "__main__":
    args = docopt(__doc__, version="Create Koha CSV 1.0")
    PROX_FILE = args["<prox_report.csv>"]
    if not file_exists(PROX_FILE):
        exit(1)
    prox_map = create_prox_map(PROX_FILE)
    files["output"] = str(today.isoformat()) + "-koha-patrons.csv"
    koha_fields = [
        "branchcode",
        "cardnumber",
        "categorycode",
        "dateenrolled",
        "dateexpiry",
        "email",
        "firstname",
        "patron_attributes",
        "surname",
        "userid",
        "phone",
        "borrowernotes",
    ]
    main()
