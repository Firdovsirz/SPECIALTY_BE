from app.db.session import get_db
from app.services.cafedra import *
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.get("/cafedras")
async def list_cafedras(
    db: AsyncSession = Depends(get_db)
):
    return await get_cafedras(db)