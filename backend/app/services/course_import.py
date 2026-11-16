from app.models import Prerequisite, Course as CourseRow
from app.schemas.course import Course as CourseData
from datetime import datetime, timezone
from dataclasses import dataclass
from sqlalchemy import select, delete
from sqlalchemy.orm import Session

@dataclass
class ImportStats:
    created: int = 0
    updated: int = 0
    prerequisites: int = 0

def normalize_dept(raw: str) -> str:
    return raw.strip().upper()

def normalize_number(raw: str) -> str:
    return raw.strip().upper()

def normalize_title(raw: str) -> str:
    return " ".join(raw.split())

def make_course_code(dept: str, number: str) -> str:
    return normalize_dept(dept)+" "+normalize_number(number)

def empty_to_none(value: str | None) -> str | None:
    return value or None

def parse_credits(units: str | None) -> int:
    try:
        return int(units)
    except (TypeError, ValueError):
        return 0

def prerequisite_groups(tree) -> list[list[str]]:
    if tree is None:
        return []
    if tree.type == "course":
        return [[tree.id]]
    if tree.type == "and":
        groups = []
        for child in tree.children:
            if child.type == "course":
                groups.append([child.id])
            elif child.type == "or":
                groups.extend(prerequisite_groups(child))
        return groups
    if tree.type == "or":
        group = []
        for child in tree.children:
            if child.type == "course":
                group.append(child.id)
            else:
                return []
        return [group]
    return []

def upsert_course(db: Session, data: CourseData) -> tuple[CourseRow, bool]:
    dept = normalize_dept(data.dept)
    number = normalize_number(data.number)
    is_created = False
    row = db.scalar(
        select(CourseRow).where(CourseRow.dept == dept, CourseRow.number == number)   
    )
    if row is None:
        row = CourseRow(dept=dept, number=number)
        db.add(row)
        is_created = True

    row.course_code = make_course_code(dept, number)
    row.title = normalize_title(data.title)
    row.credits = parse_credits(data.units)
    row.description = empty_to_none(data.description)
    row.prerequisites_text = empty_to_none(data.prerequisites)
    row.corequisites_text = empty_to_none(data.corequisites)
    row.last_synced_at = datetime.now(timezone.utc)
    db.flush()
    return row, is_created

def import_courses(db: Session, courses: list[CourseData]) -> ImportStats:
    stats = ImportStats()
    rows = {}
    unique = {make_course_code(c.dept, c.number): c for c in courses}

    try:
        for course in unique.values():
            row, is_created = upsert_course(db, course)
            rows[row.course_code] = row
            if is_created:
                stats.created +=1
            else:
                stats.updated +=1

        for course in unique.values():
            row = rows[make_course_code(course.dept, course.number)]
            db.execute(delete(Prerequisite).where(Prerequisite.course_id == row.id))
            groups = prerequisite_groups(course.prerequisite_tree)
            for group_number, group in enumerate(groups, start=1):
                for code in group:
                    required = rows.get(code) or db.scalar(select(CourseRow).where(CourseRow.course_code == code))
                    if required is None:
                        continue
                    if required.id == row.id:
                        continue
                    prereq = Prerequisite(course_id=row.id, required_course_id=required.id, group_number=group_number)
                    stats.prerequisites +=1
                    db.add(prereq)

        db.commit()
        return stats
    except Exception:
        db.rollback()
        raise