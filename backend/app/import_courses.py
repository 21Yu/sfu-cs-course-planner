import argparse

from app.config import settings
from app.db import SessionLocal
from app.services.course_import import import_courses
from app.services.sfu_courses import SFUCoursesClient


def main():
    parser = argparse.ArgumentParser(description="Import SFU courses into the database")
    parser.add_argument(
        "--dept",
        nargs="+",
        default=["CMPT"],
        help="One or more department codes, e.g. --dept MACM MATH STAT CMPT",
    )
    args = parser.parse_args()

    courses = []



    with SFUCoursesClient(
        base_url=settings.sfu_courses_api_base_url,
        timeout_seconds=settings.sfu_courses_api_timeout_seconds,
    ) as client:
        for dept in args.dept:
            courses.extend(client.get_courses(dept=dept))

    with SessionLocal() as db:
        stats = import_courses(db, courses)
    print(stats)


if __name__ == "__main__":
    main()
