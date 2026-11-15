from pydantic import BaseModel, ConfigDict

from app.schemas.course_responses import CourseSummary

from pydantic.alias_generators import to_camel

class ProgramRequirementCourseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True,
                              alias_generator=to_camel,
                              populate_by_name=True)

    course: CourseSummary