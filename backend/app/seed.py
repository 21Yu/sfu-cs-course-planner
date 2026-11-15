from sqlalchemy import select

from app.db import SessionLocal
from app.models import Course, Prerequisite, Term

def get_or_create_course(db, dept, number, title, credits):
    course = db.scalar(select(Course).where(Course.dept == dept, Course.number == number))
    if course is None:
        course = Course(dept=dept, number=number, course_code=f"{dept} {number}",
                        title=title, credits=credits)
        db.add(course)
        db.flush() 
    return course

def seed():
    with SessionLocal() as db:
        for code, year, season in [(1261, 2026, "spring"), (1264, 2026, "summer"), (1267, 2026, "fall")]:
            if db.get(Term, code) is None:
                db.add(Term(code=code, year=year, season=season))

        c120 = get_or_create_course(db, "CMPT", "120", "Introduction to Computing Science and Programming I", 3)
        c125 = get_or_create_course(db, "CMPT", "125", "Introduction to Computing Science and Programming II", 3)
        get_or_create_course(db, "CMPT", "225", "Data Structures and Programming", 3)

        exists = db.scalar(select(Prerequisite).where(
            Prerequisite.course_id == c125.id, Prerequisite.required_course_id == c120.id))
        if exists is None:
            db.add(Prerequisite(course_id=c125.id, required_course_id=c120.id, group_number=1))

        db.commit()
    print("Seed data loaded.")


if __name__ == "__main__":
    seed()