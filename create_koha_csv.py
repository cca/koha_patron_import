#!/usr/bin/env python
"""
This script takes JSON data from Workday and maps it into a format appropriate
for import into Koha. We run it once per semester just prior to the semester's
start. Note that a few things should be manually checked:

    - ensure mappings (patron category, student major) haven't changed
        (see koha_mappings.py and new-programs.sh)
    - look up last day of the semester (this is the expiration date, captured
        in the "-s" flag when the script is run)
"""
import argparse
import csv
from datetime import date, timedelta
import json
import os

from koha_mappings import category, fac_depts, stu_major

today = date.today()


def strip_first_n_lines(filename, n=0):
    index = 0
    with open(filename, 'r+') as fh:
        while index < n:
            fh.readline()
            index += 1
        data = fh.read()
        fh.seek(0)
        fh.write(data)
        fh.truncate()


def create_prox_map(proxfile):
    # Prox report CSV is invalid with a title line & an empty line, we strip
    # the header row too or else conversion to int() below breaks
    strip_first_n_lines(proxfile, 3)
    with open(proxfile, mode='r') as infile:
        reader = csv.reader(infile)
        # Universal ID => prox number mapping
        # Numbers in prox report have a varying number of leading zeroes, e.g.
        # "001000001", "010000001", so we strip by casting to int & back to str
        map = {str(int(rows[0])): str(int(rows[1])) for rows in reader if int(rows[1]) != 0}
        return map


def make_student_row(student):
    # some students don't have CCA emails, skip them
    # one student record in Summer 2021 lacked a last_name
    if student.get("inst_email") is None or student.get("last_name") is None:
        return None

    patron = {
        "branchcode": 'SF',
        "categorycode": category[student["academic_level"]],
        # fill in Prox number if we have it, or default to UID
        "cardnumber": prox_map.get(student["universal_id"],
                                   student["universal_id"]).strip(),
        "dateenrolled": today.isoformat(),
        "dateexpiry": args.semester_end,
        "email": student["inst_email"],
        "firstname": student["first_name"],
        "patron_attributes": "UNIVID:{},STUID:{}".format(
            student["universal_id"], student["student_id"]),
        "phone": student.get("phone", ''),
        "surname": student["last_name"],
        "userid": student["username"],
    }

    # handle student major (additional patron attribute)
    major = None
    if student["primary_program"] in stu_major:
        major = str(stu_major[student["primary_program"]])
        patron["patron_attributes"] += ',STUDENTMAJ:{}'.format(major)
    else:
        for program in student["programs"]:
            if program["program"] in stu_major:
                major = str(stu_major[program["program"]])
                patron["patron_attributes"] += ',STUDENTMAJ:{}'.format(major)
                break
    # we couldn't find a major, print a warning
    if major is None:
        print("""Unable to parse major for student {},
        primary program: {}, program credentials: {}""".format(
            student["username"],
            student["primary_program"],
            vars(student["programs"])
        ))

    return patron


def expirationDate(person):
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
    type = person.get('etype') or person.get('etype_future')
    if not type:
        print(('Warning: employee {} does not have an etype nor a etype_future.'
               ' They will be assigned the Staff expiration date.'
               .format(person["username"])))
        type = 'Staff'
    d = date.fromisoformat(args.semester_end)
    if type == 'Staff' or type == 'Instructors':
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
        # @TODO how do we handle Summer?
        else:
            raise Exception('Summer expiration dates for faculty not implemented yet.')
    pass


def make_employee_row(person):
    # skip 1) people who are inactive (usually hire date hasn't arrived yet),
    # 2) people w/o emails, 3) the one random record for a student
    if (person["active_status"] == "0" or not person.get("work_email") or person["etype"] == "Students"):
        return None

    # create a hybrid program/department field
    # some people have neither (tend to be adjuncts or special programs staff)
    person["prodep"] = None
    if person.get("program"):
        person["prodep"] = person["program"]
    elif person.get("department"):
        person["prodep"] = person["department"]
    elif person["job_profile"] in fac_depts:
        person["prodep"] = person["job_profile"]

    # skip inactive special programs faculty
    if person["job_profile"] == "Special Programs Instructor (inactive)":
        return None
    # we assume etype=Instructors => special programs faculty
    if (person["etype"] == "Instructors" and person["job_profile"] != "Special Programs Instructor" and person["job_profile"] not in fac_depts):
        print(('Warning: Instructor {} is not a Special Programs Instructor, '
               'check record.').format(person["username"]))

    patron = {
        "branchcode": 'SF',
        "categorycode": category[person["etype"]],
        # fill in Prox number if we have it, or default to UID
        "cardnumber": prox_map.get(person["universal_id"],
                                   person["universal_id"]).strip(),
        "dateenrolled": today.isoformat(),
        # @TODO this date varies by categorycode now
        "dateexpiry": expirationDate(person),
        "email": person["work_email"],
        "firstname": person["first_name"],
        "patron_attributes": "UNIVID:" + person["universal_id"],
        "phone": person.get("phone", ''),
        "surname": person["last_name"],
        "userid": person["username"],
    }

    # handle faculty/staff department (additional patron attribute)
    if person["prodep"] and person["prodep"] in fac_depts:
        code = str(fac_depts[person["prodep"]])
        patron["patron_attributes"] += ',FACDEPT:{}'.format(code)
    elif person["prodep"]:
        # there's a non-empty program/department value we haven't accounted for
        print("""No mapping in koha_mappings.fac_depts for faculty/staff prodep
        "{}", see patron {}""".format(person["prodep"], person["username"]))

    if person["prodep"] is None:
        print('Warning: employee {} has no academic program or department:'
              .format(person["username"]))
        print(person)

    return patron


def main():
    EMP_FILE = 'employee_data.json'
    STU_FILE = 'student_data.json'
    PROX_FILE = 'prox.csv'
    for file in [EMP_FILE, STU_FILE, PROX_FILE]:
        if not os.path.exists(file):
            raise Exception('Expected to find file "{}" in project root.'
                            .format(file))

    global prox_map
    prox_map = create_prox_map(PROX_FILE)

    OUT_FILE = str(today.isoformat()) + '-koha-patrons.csv'
    koha_fields = ['branchcode', 'cardnumber', 'categorycode', 'dateenrolled',
                   'dateexpiry', 'email', 'firstname', 'patron_attributes',
                   'surname', 'userid', 'phone' ]

    print('Adding students to Koha patron CSV.')
    with open(STU_FILE, 'r') as file:
        students = json.load(file)["Report_Entry"]
        with open(OUT_FILE, 'w') as output:
            writer = csv.DictWriter(output, fieldnames=koha_fields)
            writer.writeheader()
            for stu in students:
                row = make_student_row(stu)
                if row:
                    writer.writerow(row)

    print('Adding Faculty/Staff to Koha patron CSV.')
    with open(EMP_FILE, 'r') as file:
        employees = json.load(file)["Report_Entry"]
        # open in append mode & don't add header row
        with open(OUT_FILE, 'a') as output:
            writer = csv.DictWriter(output, fieldnames=koha_fields)
            for employee in employees:
                row = make_employee_row(employee)
                if row:
                    writer.writerow(row)

    print('Done! Upload the CSV at '
    'https://library-staff.cca.edu/cgi-bin/koha/tools/import_borrowers.pl')
    path = input('Where would you like to archive the data files? (e.g. '
                 'data/2019FA) ')
    if path.strip() != '' and path.strip().lower() != 'n':
        # ensure directory exists
        if not os.path.isdir(path):
            try:
                os.mkdir(path)
            except PermissionError:
                print('Unable to create directory at path "{}".'.format(path))
                exit(1)

        for name in [STU_FILE, EMP_FILE, PROX_FILE, OUT_FILE]:
            os.renames(name, os.path.join(path, name))
    else:
        print('Files were not archived.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Convert Workday JSON into Koha patron import CSV')
    parser.add_argument('-s', '--semester-end', type=str, required=True,
                        help='Last day of the semester in YYYY-MM-DD format')
    args = parser.parse_args()
    main()
