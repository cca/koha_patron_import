from typing import Literal

from pydantic import BaseModel, EmailStr

etypes = Literal[
    "Student", "Faculty", "Instructors", "Staff", "Contingent Employees/Contractors"
]


class Employee(BaseModel):
    active_status: bool
    department: str | None = None
    employee_id: str
    etype_future: str | None = None
    etype: etypes | None = None
    first_name: str
    is_contingent: bool
    job_profile: str | None = None
    last_name: str
    program: str | None = None
    universal_id: str
    username: str
    work_email: EmailStr | None = None
    work_phone: str | None = None


class Student(BaseModel):
    academic_level: Literal["Undergraduate", "Graduate", "Pre-College"]
    first_name: str
    inst_email: EmailStr | None = None
    last_name: str
    primary_program: str
    # programs always have program, program_type, sometimes has credentials (but not for nondegree)
    programs: list[dict[str, str]]
    student_id: str
    universal_id: str
    username: str


# Just used for type hints
Person = Employee | Student
