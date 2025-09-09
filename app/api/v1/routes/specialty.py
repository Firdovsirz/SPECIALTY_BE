from app.db.session import get_db
from app.services.specialty import *
from fastapi import APIRouter, Depends
from app.utils.language import get_language
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.schemas.specialty import CreateSpecialty

router = APIRouter()

@router.get("/specialties")
async def get_specialities_endpoint(
    lang_code: str = Depends(get_language),
    db: AsyncSession = Depends(get_db)
):
    return await get_specialties(lang_code, db)

@router.post("/specialty")
async def create_specialty_endpoint(
    specialty_details: CreateSpecialty,
    db: AsyncSession = Depends(get_db)
):
    return await add_specialty(specialty_details, db)