from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from app.schemas.courses import CourseSummary
from pydantic.alias_generators import to_camel

Season = Literal["fall", "spring", "summer"]

class PlanCourseCreate(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel,
                              populate_by_name=True)

    course_id: int
    year: int = Field(ge=1)
    season: Season

class PlanCourseUpdate(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel,
                              populate_by_name=True)

    year: int = Field(ge=1)
    season: Season

class PlanCourseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True,
                              alias_generator=to_camel,
                              populate_by_name=True)

    id: int
    course: CourseSummary
    year: int = Field(ge=1)
    season: Season