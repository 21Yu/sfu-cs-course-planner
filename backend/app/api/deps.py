"""Shared request dependencies: who is signed in, and which plans they own."""

from fastapi import Cookie, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.config import settings
from app.db import get_db
from app.models import Plan, PlanCourse, User
from app.services.auth import get_user_by_session_token


def get_current_user(
    session_token: str | None = Cookie(default=None, alias=settings.session_cookie_name),
    db: Session = Depends(get_db),
) -> User:
    """Return the signed-in user, or respond 401."""
    user = get_user_by_session_token(db, session_token) if session_token else None
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


def get_owned_plan(
    plan_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Plan:
    """Return the plan if it belongs to the signed-in user.

    Someone else's plan gets the same 404 as a plan that doesn't exist, so the API
    never confirms that a plan ID is in use. Every route that takes a plan ID
    should depend on this instead of loading the plan itself.
    """
    plan = db.scalar(
        select(Plan)
        .options(selectinload(Plan.plan_courses).selectinload(PlanCourse.course))
        .where(Plan.id == plan_id, Plan.user_id == user.id)
    )
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan
