"""Course search endpoints backed by the SFU course data service."""

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy import select, or_
from sqlalchemy.orm import Session


from ..config import settings
from ..schemas.course import Course
from ..services.sfu_courses import (
    SFUCoursesAPIError,
    SFUCoursesClient,
    SFUCoursesTimeoutError,
)
from ..db import get_db
from ..models.courses import Course as CourseModel
from ..schemas.course_responses import CourseSummary

router = APIRouter(prefix="/api/courses", tags=["courses"])


@router.get("/external", response_model=list[Course], summary="Search external course outlines")
def get_courses(
    dept: str | None = Query(default=None, min_length=2, max_length=8),
    number: str | None = Query(default=None, min_length=1, max_length=8),
) -> list[Course]:
    """Return course outlines, optionally filtered by department and number."""
    try:
        with SFUCoursesClient(
            base_url=settings.sfu_courses_api_base_url,
            timeout_seconds=settings.sfu_courses_api_timeout_seconds,
        ) as client:
            return client.get_courses(dept=dept, number=number)
    except SFUCoursesTimeoutError as exc:
        raise HTTPException(status_code=504, detail="Course data provider timed out") from exc
    except SFUCoursesAPIError as exc:
        raise HTTPException(status_code=502, detail="Course data provider request failed") from exc


@router.get("", response_model = list[CourseSummary], summary = "Search courses")
def search_courses(
    q: str | None = Query(default = None, min_length = 1, max_length = 100),
    subject: str | None = Query(default = None, min_length = 2, max_length = 8),
    limit: int | None = Query(default = None, ge = 1, le = 500),
    offset: int = Query(default = 0, ge=0),
    db: Session = Depends(get_db)
):
    statement = select(CourseModel)

    if q:
        pattern = f"%{q}%"
        statement = statement.where(
            or_(
                CourseModel.course_code.ilike(pattern),
                CourseModel.title.ilike(pattern)
            )
        )

    if subject:
        statement = statement.where(CourseModel.dept.ilike(subject))

    if limit is not None:
        statement = statement.limit(limit)

    statement = statement.offset(offset)
    return db.execute(statement).scalars().all()