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


class UserRegisterRequest(UserCreate):
    verification_code: str = Field(
        min_length=4,
        max_length=8,
        description="邮箱验证码",
    )


class SendCodeRequest(BaseModel):
    email: EmailStr
    purpose: str = Field(default="login")
    challenge_token: str | None = None
    challenge_answer: str | None = None


class VerifyCodeLoginRequest(BaseModel):
    email: EmailStr
    code: str = Field(min_length=4, max_length=8)


class PasswordResetRequest(BaseModel):
    email: EmailStr
    code: str = Field(min_length=4, max_length=8)
    new_password: str = Field(min_length=8)


class AuthChallengeResponse(BaseModel):
    required: bool = True
    challenge_token: str
    challenge_question: str
    expires_in_seconds: int


class VerifyChallengeRequest(BaseModel):
    challenge_token: str
    answer: str = Field(min_length=1, max_length=50)


class SendCodeResponse(BaseModel):
    success: bool
    message: str
    challenge: AuthChallengeResponse | None = None


class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None = None
    role: str
    workspace_id: int | None = None
    is_active: bool
    is_superuser: bool
    last_login_at: datetime | None = None
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
