from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.plo import get_plos_by_specialty, create_plo as create_plo_service, delete_plo, update_plo, get_all_plos as get_all_plos_service
from app.api.v1.schemas.plo import CreatePlo
from app.utils.language import get_language

router  = APIRouter(prefix="/plo", tags=["PLO"])

# GET all PLOs
@router.get("", response_model=None) 
async def get_all_plos(db: AsyncSession = Depends(get_db)):
    from app.services.plo import get_all_plos  
    return await get_all_plos_service(db)

@router.get('/{specialty_code}')
async def list_plos(
    specialty_code: str,
    lang: str = Depends(get_language),
    db: AsyncSession = Depends(get_db)
):
    return await get_plos_by_specialty(specialty_code, lang, db)

@router.post("")
async def create_plo(
    plo_data: CreatePlo,
    lang: str = Depends(get_language),
    db: AsyncSession = Depends(get_db)
):
    return await create_plo_service(db, plo_data)

@router.delete("/{plo_code}")
async def delete_plo_endpoint(plo_code: str, db: AsyncSession = Depends(get_db)):
    return await delete_plo(db, plo_code)

@router.put("/{plo_code}")
async def update_plo_endpoint(plo_code: str, plo_data: CreatePlo, db: AsyncSession = Depends(get_db)):
    return await update_plo(db, plo_code, plo_data)















