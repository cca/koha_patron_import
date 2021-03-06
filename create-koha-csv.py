#!/usr/bin/env python
"""
This script takes JSON data from Workday and maps it into a format appropriate
for import into Koha. We run it once per semester just prior to the semester's
start. Note that a few things should be manually checked:

    - ensure mappings (patron category, student major) haven't changed
        (see koha_mappings.py)
    - look up last day of the semester (this is the expiration date, captured
        in the "-e" flag when the script is run)
"""
import argparse
import csv
import datetime
import json
import os

from koha_mappings import category, fac_depts, sf_depts, stu_major

parser = argparse.ArgumentParser(
    description='Convert Workday JSON into Koha patron import CSV')
parser.add_argument('-s', '--student-expiry', type=str, default='2020-05-08',
                    help='Student record expiration date in YYYY-MM-DD format')
parser.add_argument('-e', '--employee-expiry', type=str, default='2020-05-31',
                    help='Employee record expiration date in YYYY-MM-DD format')
args = parser.parse_args()

today = datetime.date.today()
emp_file = 'employee_data.json'
stu_file = 'student_data.json'
out_file = str(today.isoformat()) + '-koha-patrons.csv'
koha_fields = [ 'branchcode', 'cardnumber', 'categorycode', 'dateenrolled',
'dateexpiry', 'email', 'firstname', 'patron_attributes', 'surname', 'userid', ]


def make_student_row(student):
    # some students don't have CCA emails, skip them
    if student.get("inst_email") is None:
        return None

    patron = {
        "branchcode": ('SF' if student["academic_level"] == 'Graduate'
            or student["primary_program"] in sf_depts else 'OAK'),
        "categorycode": category[student["academic_level"]],
        # patrons don't have a barcode yet, fill in university ID
        "cardnumber": student["student_id"],
        "dateenrolled": today.isoformat(),
        "dateexpiry": args.student_expiry,
        "email": student["inst_email"],
        "firstname": student["first_name"],
        "patron_attributes": "UNIVID:{},STUID:{}".format(student["universal_id"], student["student_id"]),
        "surname": student["last_name"],
        "userid": student["username"],
    }

    # handle student major (additional patron attribute)
    major = None
    if student["primary_program"] in stu_major:
        major = str(stu_major[student["primary_program"]])
        patron["patron_attributes"] += ',STUDENTMAJ:{}'.format(major)
    else:
        for cred in student["program_credentials"]:
            if cred["program"] in stu_major:
                major = str(stu_major[cred["program"]])
                patron["patron_attributes"] += ',STUDENTMAJ:{}'.format(major)
                break
    # we couldn't find a major, print a warning
    if major is None:
        print("""Unable to parse major for student {},
        primary program: {}, program credentials: {}""".format(
            student["username"],
            student["primary_program"],
            vars(student["program_credentials"])
        ))

    return patron


def make_employee_row(person):
    # skip 1) people who are inactive (usually hire date hasn't arrived yet),
    # 2) people w/o emails, 3) the one random record for a student
    if (person["active_status"] == "0" or not person.get("work_email")
        or person["etype"] == "Students"):
        return None

    # create a hybrid program/department field
    # some people have neither (tend to be adjuncts or special programs staff)
    person["prodep"] = None
    if person.get("program"):
        person["prodep"] = person["program"]
    elif person.get("department"):
        person["prodep"] = person["department"]

    # we assume etype=Instructors => special programs faculty
    if (person["etype"] == "Instructors"
        and person["job_profile"] != "Special Programs Instructor"):
        print('Warning: Instructor {} is not a Special Programs Instructor, \
        check record.'.format(person["username"]))

    patron = {
        "branchcode": ('SF' if person["prodep"] in sf_depts else 'OAK'),
        "categorycode": category[person["etype"]],
        # patrons don't have a barcode yet, fill in university ID
        "cardnumber": person["universal_id"],
        "dateenrolled": today.isoformat(),
        "dateexpiry": args.employee_expiry,
        "email": person["work_email"],
        "firstname": person["first_name"],
        "patron_attributes": "UNIVID:" + person["universal_id"],
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

    return patron

if os.path.exists(stu_file):
    print('Adding students to Koha patron CSV.')
    with open(stu_file, 'r') as file:
        students = json.load(file)["Report_Entry"]
        with open(out_file, 'w') as output:
            writer = csv.DictWriter(output, fieldnames=koha_fields)
            writer.writeheader()
            for student in students:
                row = make_student_row(student)
                if row: writer.writerow(row)

if os.path.exists(emp_file):
    print('Adding Faculty/Staff to Koha patron CSV.')
    with open(emp_file, 'r') as file:
        employees = json.load(file)["Report_Entry"]
        # open in append mode & don't add header row
        with open(out_file, 'a') as output:
            writer = csv.DictWriter(output, fieldnames=koha_fields)
            for employee in employees:
                row = make_employee_row(employee)
                if row: writer.writerow(row)

print('Done! Upload the CSV at \
https://library-staff.cca.edu/cgi-bin/koha/tools/import_borrowers.pl')
path = input('Where would you like to archive the data files? (e.g. data/2019FA) ')
if path.strip() != '':
    # ensure directory exists
    if not os.path.isdir(path):
        try:
            os.mkdir(path)
        except:
            print('Error: unable to create directory at path "{}"'.format(path))
            exit(1)

    for name in [stu_file, emp_file, out_file]:
        os.renames(name, os.path.join(path, name))
else:
    print('Files were not archived.')
