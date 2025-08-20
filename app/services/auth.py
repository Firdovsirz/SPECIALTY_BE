import random
from sqlalchemy import select
from app.models.auth import Auth
from app.db.session import get_db
from fastapi import Depends, status
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse
from app.utils.jwt import encode_auth_token
from app.utils.security import hash_password
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.password_validator import validate_password
from app.api.v1.schemas.auth import SignUp, SignIn, ValidateOTP

def generateOtp(length: int = 6) -> str:
    otp = ''.join(str(random.randint(0, 9)) for _ in range(length))
    return otp

async def signup(
    user: SignUp,
    db: AsyncSession = Depends(get_db)
):
    try:
        fetched_exist_user = await db.execute(
            select(Auth)
            .where(Auth.fin_kod == user.fin_kod)
        )

        exist_user = fetched_exist_user.scalar_one_or_none()

        if exist_user:
            return JSONResponse(
                content={
                    "statusCode": 409,
                    "message": "Fin kod in use.",
                }, status_code=status.HTTP_409_CONFLICT
            )
        
        validate_password(user.password)

        otp = generateOtp()
        hashed_otp = hashed_password(otp)
        hashed_password = hash_password(user.password)
        
        new_user = Auth(
            university_code = user.university_code,
            fin_kod = user.fin_kod,
            password = hashed_password,
            role = 2,
            otp = hashed_otp,
            approved = False,
            created_at = datetime.utcnow(),
            updated_at = None,
            otp_expires_at = datetime.utcnow() + timedelta(minutes=5),
            otp_validated = False
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return JSONResponse(
            content={
                "statusCode": 201,
                "message": "User temporary saved",
            }, status_code=status.HTTP_201_CREATED
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "statusCode": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def signin(
    credentials: SignIn,
    db: AsyncSession = Depends(get_db)
):
    try:
        fetched_exist_user = await db.execute(
            select(Auth)
            .where(Auth.fin_kod == credentials.fin_kod)
        )

        exist_user = fetched_exist_user.scalar_one_or_none()

        if not exist_user:
            return JSONResponse(
                content={
                    "statusCode": 401,
                    "message": "UNAUTHORIZED"
                }, status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        # fetched_user = await db.execute(
        #     select(User)
        #     .where(User.fin_kod == credentials.fin_kod)
        # )

        # user = fetched_user.scalar_one_or_none()
        
        if hash_password(credentials.password) != exist_user.password:
            return JSONResponse(
                content={
                    "statusCode": 401,
                    "message": "UNAUTHORIZED"
                }, status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        token = encode_auth_token(exist_user.fin_kod, exist_user.role, exist_user.approved)

        return JSONResponse(
            content={
                "statusCode": 200,
                "message": "AUTHORIZED",
                "token": token,
                # "user": {
                #     "name": user.name
                # }
            }
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "statusCode": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def validate_otp(
    credentials: ValidateOTP,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(
            select(Auth)
            .where(Auth.fin_kod == credentials.fin_kod)
        )

        user = result.scalar_one_or_none()

        if not user:
            return JSONResponse(
                content={
                    "statusCode": 404,
                    "message": "User not found"
                }, status_code=status.HTTP_404_NOT_FOUND
            )
        
        hashed_otp = hash_password(credentials.otp)
        
        if user.otp_expires_at < datetime.utcnow() or hashed_otp != credentials.otp:
            return JSONResponse(
                content={
                    "statusCode": 401,
                    "message": "Expired otp"
                }, status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        user.otp_validated = True
        user.otp = None
        user.otp_expires_at = None

        await db.commit()
        await db.refresh(user)
        
        return JSONResponse(
            content={
                "status_code": 200,
                "message": "AUTHORIZED"
            }, status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return JSONResponse(
            content={
                "statusCode": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )