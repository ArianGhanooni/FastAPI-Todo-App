from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from user.schemas import UserLoginSchema, UserSignupSchema, UserRefreshTokenSchema
from user.models import UserModel, TokenModel
from sqlalchemy.orm import Session
from core.database import get_db
from auth.jwt_auth import generate_access_token, refresh_access_token, decode_refresh_token
import secrets


router = APIRouter(tags=["users"], prefix="/users")


def generate_token(length = 32):
    return secrets.token_hex(length)


@router.post("/login")
async def user_login(request: UserLoginSchema, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter_by(username=request.username).first()
    if not user or not user.verify_password(request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    token_obj = TokenModel(user_id=user.id, token=generate_token())
    db.add(token_obj)
    db.commit()
    db.refresh(token_obj)

    access_token = generate_access_token(user.id)
    refresh_token = refresh_access_token(user.id)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Login successful", "token": token_obj.token, "user_id": user.id, "access_token":access_token, "refresh_token":refresh_token}
    )


@router.post("/signup")
async def user_signup(request: UserSignupSchema, db: Session = Depends(get_db)):
    if db.query(UserModel).filter_by(username=request.username).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )

    user_obj = UserModel(username=request.username)
    user_obj.set_password(request.password)

    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "User registered successfully", "user_id": user_obj.id}
    )


@router.post("/refresh_token")
def user_refresh_token(request: UserRefreshTokenSchema, db: Session = Depends(get_db)):
    user_id = decode_refresh_token(request.refresh_token)
    access_token = generate_access_token(user_id)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "User registered successfully", "Refresh_Token": access_token}
    )