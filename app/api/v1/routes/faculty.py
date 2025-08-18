
from app.db.session import get_db
from app.services.faculty import *
from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.get("/faculties")
async def get_faculties_endpoint(
    db: AsyncSession = Depends(get_db)
):
    return await get_faculties(db)

@router.get("/faculties/{uni_code}")
async def get_uni_faculties_endpoint(
    uni_code: str = Path(...),
    db: AsyncSession = Depends(get_db)
):
    return await get_uni_faculties(uni_code, db)