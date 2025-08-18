from fastapi import Depends
from app.db.session import get_db
from sqlalchemy.future import select
from app.models.cafedra import Cafedra
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

async def get_cafedras(
    db: AsyncSession = Depends(get_db)
):
    try:
        fetched_data = await db.execute(select(Cafedra))
        cafedras = fetched_data.scalars().all()

        if not cafedras:
            return JSONResponse(
                content={
                    "statusCode": 200,
                    "message": "No cafedra found.",
                    "cafedras": []
                }, status_code=200
            )
        
        return JSONResponse(
            content={
                "statusCode": 200,
                "message": "Cafedras fetched successfully.",
                "cafedras" : [
                    {
                        "university_code": cafedra.university_code,
                        "faculty_code": cafedra.faculty_code,
                        "cafedra_code": cafedra.cafedra_code,
                        "cafedra_name": cafedra.cafedra_name,
                        "created_at": str(cafedra.created_at) if cafedra.created_at else None,
                        "updated_at": str(cafedra.updated_at) if cafedra.updated_at else None
                    } for cafedra in cafedras
                ]
            }
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "statusCode": 500,
                "error": str(e)
            }
        )