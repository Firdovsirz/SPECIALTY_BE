from app.services.auth import *
from app.db.session import get_db
from fastapi import APIRouter, Depends
from app.api.v1.schemas.auth import SignUp
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.post("signup")
async def signup_endpoint(
    user: SignUp,
    db: AsyncSession = Depends(get_db)
):
    return await signup(user, db)