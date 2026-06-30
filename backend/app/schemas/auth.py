from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr = Field(
        examples=["testuser01@example.com"],
        description="注册邮箱",
    )
    password: str = Field(
        min_length=8,
        examples=["Test@123456"],
        description="登录密码，至少 8 位",
    )
    full_name: str | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "testuser01@example.com",
                "password": "Test@123456",
                "full_name": "测试用户01",
            }
        }
    }


class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None = None
    role: str
    workspace_id: int | None = None
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserRead

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.example.token",
                "token_type": "bearer",
                "user": {
                    "id": 1,
                    "email": "testuser01@example.com",
                    "full_name": "测试用户01",
                    "is_active": True,
                    "is_superuser": False,
                    "created_at": "2026-06-20T10:00:00+08:00",
                    "updated_at": "2026-06-20T10:00:00+08:00",
                },
            }
        }
    }


class TokenPayload(BaseModel):
    sub: str
    workspace_id: int | None = None
    role: str | None = None
