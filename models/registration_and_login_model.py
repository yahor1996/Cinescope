from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict
import datetime
import re
from typing import List
from pydantic import BaseModel, Field, field_validator
from Cinescope.constants.roles import Roles

class UserLogin(BaseModel):
    id: str
    email: str = Field(pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", description="Email пользователя")
    fullName: str = Field(min_length=1, max_length=100, description="Полное имя пользователя")
    roles: List[Roles]


class RegisterAndLoginUserResponse(BaseModel):
    user: UserLogin
    accessToken: str
    refreshToken: str
    expiresIn: int