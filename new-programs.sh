#!/usr/bin/env bash
jq '.Report_Entry[].primary_program' student_data.json | sort | uniq > "data/$(date "+%Y-%m-%d")-student-majors.txt"
jq '.Report_Entry[].program' employee_data.json | sort | uniq | sed '/null/d' > "data/$(date "+%Y-%m-%d")-staff-depts.txt"
jq '.Report_Entry[].department' employee_data.json | sort | uniq | sed '/null/d' >> "data/$(date "+%Y-%m-%d")-staff-depts.txt"

echo -e "\nSTAFF DEPTS DIFF:\n"
git diff --no-index --color-words data/*-staff-depts.txt

echo -e "\nSTUDENT MAJORS DIFF:\n"
git diff --no-index --color-words data/*-student-majors.txt
