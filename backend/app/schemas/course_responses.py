from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

class CourseSummary(BaseModel):
    """Small version of a course. Used in search results and nested in other schemas."""
    model_config = ConfigDict(from_attributes=True,
                              alias_generator=to_camel,
                              populate_by_name=True)

    id: int                                     
    course_code: str = Field(examples=["CMPT 225"])
    title: str
    credits: int


class PrerequisiteRead(BaseModel):
    """One required course, from your Prerequisite model."""
    model_config = ConfigDict(from_attributes=True,
                              alias_generator=to_camel,
                              populate_by_name=True)

    group_number: int
    required_course: CourseSummary             


class CourseResponse(CourseSummary):            
    """Full course details, for GET /api/courses/{courseCode}."""
    description: Optional[str] = None
    degree_level: Optional[str] = None
    designation: Optional[str] = None
    corequisites_text: Optional[str] = None
    prerequisites_text: Optional[str] = None
    outline_url: Optional[str] = None
    prerequisites: list[PrerequisiteRead] = [] 


class ErrorResponse(BaseModel):
    detail: str
