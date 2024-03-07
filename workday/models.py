from typing import Literal, Optional

from pydantic import BaseModel, EmailStr

etypes = Literal[
    "Student", "Faculty", "Instructors", "Staff", "Contingent Employees/Contractors"
]


class Employee(BaseModel):
    active_status: bool
    department: Optional[str] = None
    etype_future: Optional[str] = None
    etype: Optional[etypes] = None
    first_name: str
    is_contingent: bool
    job_profile: Optional[str] = None
    last_name: str
    program: Optional[str] = None
    universal_id: str
    username: str
    work_email: Optional[EmailStr] = None
    work_phone: Optional[str] = None


class Student(BaseModel):
    username: str
