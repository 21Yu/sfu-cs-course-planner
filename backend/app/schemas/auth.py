from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field
from pydantic.alias_generators import to_camel

#request
class RegisterRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel,
                              populate_by_name=True)

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class LoginRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel,
                              populate_by_name=True)

    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

#responses
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True,
                              alias_generator=to_camel,
                              populate_by_name=True)

    id: int
    email: str
    created_at: datetime
