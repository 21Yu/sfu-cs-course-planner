"""Plan endpoints. Every route only sees the signed-in user's own plans."""

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_owned_plan
from app.db import get_db
from app.models import Plan, User
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
