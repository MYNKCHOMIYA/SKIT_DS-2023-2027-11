from pydantic import BaseModel
from typing import List


class DepartmentStat(BaseModel):
    department: str
    faculty_count: int
    publication_count: int


class DashboardAnalytics(BaseModel):
    total_faculty: int
    total_publications: int
    department_stats: List[DepartmentStat]


class SkillCount(BaseModel):
    skill: str
    count: int
