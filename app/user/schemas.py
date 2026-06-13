from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional


class UserLoginSchema(BaseModel):
    username: str = (Field(..., max_length=250, min_length=5, description="Username of the user"))
    password: str = (Field(..., description="Password of the user"))


class UserSignupSchema(BaseModel):
    username: str = (Field(..., max_length=250, min_length=5, description="Username of the user"))
    password: str = (Field(..., description="Password of the user"))
    password_confirm: str = (Field(..., description="Confirm Password of the user"))

    @field_validator("password_confirm")
    def password_validator(cls, password_confirm, validators):
        if not password_confirm == validators.data.get("password"):
            raise ValueError("Password does not match")
        return password_confirm


class UserRefreshTokenSchema(BaseModel):
    refresh_token: str = (Field(..., description="REFRESH TOKEN"))
