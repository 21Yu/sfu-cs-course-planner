from sqlalchemy import String, ForeignKey, Integer, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

class PlanCourse(Base):
    __tablename__ = "plan_courses"
    __table_args__ = (
        UniqueConstraint("plan_id", "course_id", name="unique_plan_course"),
        CheckConstraint("season IN ('fall', 'spring', 'summer')", name="ck_plan_courses_season"),
        CheckConstraint("year >= 1", name="ck_plan_courses_year"),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id")
    )

    course: Mapped["Course"] = relationship()

    plan_id: Mapped[int] = mapped_column(
        ForeignKey("plans.id", ondelete="CASCADE")
    )

    plan: Mapped["Plan"] = relationship(
        back_populates="plan_courses"
    )

    year: Mapped[int] = mapped_column(
        Integer
    )

    season: Mapped[str] = mapped_column(
        String(10)
    )