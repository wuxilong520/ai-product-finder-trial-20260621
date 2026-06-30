from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_current_user
from app.core.runtime import AppError
from app.schemas.auth import (
    LoginResponse,
    PasswordResetRequest,
    SendCodeRequest,
    SendCodeResponse,
    UserCreate,
    UserRead,
    UserRegisterRequest,
    VerifyChallengeRequest,
    VerifyCodeLoginRequest,
)
from app.services.auth import auth_service


router = APIRouter()


@router.post("/register", response_model=UserRead)
def register(payload: UserRegisterRequest, db: Session = Depends(db_session)):
    return auth_service.register_user(db, payload)


@router.post("/send-code", response_model=SendCodeResponse)
def send_code(payload: SendCodeRequest, db: Session = Depends(db_session)):
    result = auth_service.send_verification_code(
        db,
        email=payload.email,
        purpose=payload.purpose,
        challenge_token=payload.challenge_token,
        challenge_answer=payload.challenge_answer,
    )
    return SendCodeResponse(**result)


@router.post("/login", response_model=LoginResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(db_session)):
    user = auth_service.authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise AppError("LOGIN_FAILED", "账号或密码错误", "auth", 401)

    token = auth_service.create_login_token(user)
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        user=UserRead.model_validate(user),
    )


@router.post("/login/code", response_model=LoginResponse)
def login_with_code(payload: VerifyCodeLoginRequest, db: Session = Depends(db_session)):
    user = auth_service.login_with_code(db, email=payload.email, code=payload.code)
    token = auth_service.create_login_token(user)
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        user=UserRead.model_validate(user),
    )


@router.post("/password/reset")
def reset_password(payload: PasswordResetRequest, db: Session = Depends(db_session)):
    auth_service.reset_password(db, email=payload.email, code=payload.code, new_password=payload.new_password)
    return {"success": True, "message": "密码已重置，请使用新密码登录"}


@router.get("/me", response_model=UserRead)
def me(current_user=Depends(get_current_user)):
    return UserRead.model_validate(current_user)
