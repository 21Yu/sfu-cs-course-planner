"""Plan endpoints. Every route only sees the signed-in user's own plans."""

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.api.deps import get_current_user, get_owned_plan
from app.db import get_db
from app.models import Plan, User, PlanCourse, Course
from app.schemas.plan_courses import PlanCourseCreate, PlanCourseRead, PlanCourseUpdate
from app.schemas.course_responses import ErrorResponse
from app.schemas.plan import PlanCreate, PlanDetailResponse, PlanResponse, PlanUpdate


router = APIRouter(
    prefix="/api/plans",
    tags=["plans"],
    responses={401: {"model": ErrorResponse}},
)


@router.get("", response_model=list[PlanResponse], summary="List my plans")
def list_plans(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Plan]:
    return list(db.scalars(select(Plan).where(Plan.user_id == user.id).order_by(Plan.id)))


@router.post("", status_code=201, response_model=PlanDetailResponse, summary="Create a plan")
def create_plan(
    payload: PlanCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Plan:
    plan = Plan(user_id=user.id, name=payload.name, start_term_code=payload.start_term_code)
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan

@router.post(
    "/{plan_id}/courses",
    status_code=201,
    response_model=PlanCourseRead,
)
def add_course(
    payload: PlanCourseCreate,
    plan: Plan = Depends(get_owned_plan),
    db: Session = Depends(get_db),
) -> PlanCourse:
    course = db.get(Course, payload.course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")

    existing = db.scalar(
        select(PlanCourse).where(
            PlanCourse.plan_id == plan.id,
            PlanCourse.course_id == payload.course_id,
        )
    )
    if existing is not None:
        raise HTTPException(
            status_code=409,
            detail="Course is already in the plan",
        )

    plan_course = PlanCourse(
        plan_id=plan.id,
        course_id=course.id,
        course=course,
        year=payload.year,
        season=payload.season,
    )

    db.add(plan_course)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Course is already in the plan",
        )

    db.refresh(plan_course)
    return plan_course


@router.get(
    "/{plan_id}",
    response_model=PlanDetailResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Get one of my plans",
)
def get_plan(plan: Plan = Depends(get_owned_plan)) -> Plan:
    return plan


@router.patch(
    "/{plan_id}",
    response_model=PlanResponse,
    responses={404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}},
    summary="Rename a plan or change its start term",
)
def update_plan(
    payload: PlanUpdate,
    plan: Plan = Depends(get_owned_plan),
    db: Session = Depends(get_db),
) -> Plan:
    values: dict = {"name": payload.name}
    if "start_term_code" in payload.model_fields_set:
        values["start_term_code"] = payload.start_term_code

    # One UPDATE that only matches the version the client saw, so two edits made
    # at the same time can't both succeed.
    result = db.execute(
        update(Plan)
        .where(Plan.id == plan.id, Plan.version == payload.version)
        .values(**values, version=Plan.version + 1)
        .execution_options(synchronize_session=False)
    )
    if result.rowcount == 0:
        db.rollback()
        raise HTTPException(
            status_code=409, detail="Plan was changed elsewhere. Reload it and try again"
        )
    db.commit()
    db.refresh(plan)
    return plan


@router.patch(
    "/{plan_id}/courses/{course_id}",
    response_model=PlanCourseRead,
    responses={404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}},
    summary="Update a course in my plan",
)
def update_course(
    plan: Plan = Depends(get_owned_plan),
    course_id: int,
    payload: PlanCourseUpdate,
    db: Session = Depends(get_db),
) -> PlanCourse:
    plan_course = db.get(PlanCourse, (plan.id, course_id))
    if plan_course is None:
        raise HTTPException(status_code=404, detail="Course not found in plan")

    values: dict = {}
    if "year" in payload.model_fields_set:
        values["year"] = payload.year
    if "season" in payload.model_fields_set:
        values["season"] = payload.season

    # Only update the version the client expects, to avoid lost updates.
    result = db.execute(
        update(PlanCourse)
        .where(PlanCourse.plan_id == plan.id, PlanCourse.course_id == course_id, PlanCourse.version == payload.version)
        .values(**values, version=PlanCourse.version + 1)
        .execution_options(synchronize_session=False)
    )
    if result.rowcount == 0:
        db.rollback()
        raise HTTPException(
            status_code=409, detail="Course was changed elsewhere. Reload it and try again"
        )

    db.commit()
    db.refresh(plan_course)
    return plan_course


@router.patch(
    "/{plan_id}/courses/{plan_course_id}",
    response_model=PlanCourseRead,
    responses={404: {"model": ErrorResponse}},
)
def update_plan_course(
    plan_course_id: int,
    payload: PlanCourseUpdate,
    plan: Plan = Depends(get_owned_plan),
    db: Session = Depends(get_db),
) -> PlanCourse:
    plan_course = db.scalar(
        select(PlanCourse).where(
            PlanCourse.id == plan_course_id,
            PlanCourse.plan_id == plan.id,
        )
    )
    if plan_course is None:
        raise HTTPException(status_code=404, detail="Plan course not found")

    plan_course.year = payload.year
    plan_course.season = payload.season
    db.commit()
    db.refresh(plan_course)
    return plan_course


@router.delete(
    "/{plan_id}",
    status_code=204,
    responses={404: {"model": ErrorResponse}},
    summary="Delete a plan",
)
def delete_plan(plan: Plan = Depends(get_owned_plan), db: Session = Depends(get_db)) -> Response:
    db.delete(plan)
    db.commit()
    return Response(status_code=204)



