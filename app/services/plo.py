from fastapi import Depends
from fastapi.responses import JSONResponse
from app.db.session import get_db
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.plo import Plo
from app.models.plo_translations import PloTranslation
import sqlalchemy as sa
from app.api.v1.schemas.plo import CreatePlo

async def get_all_plos(db: AsyncSession):
    try:
        result = await db.execute(
            select(Plo, PloTranslation).join(PloTranslation, Plo.plo_code == PloTranslation.plo_code)
        )
        rows = result.all()

        plos = []
        for plo, translation in rows:
            plos.append({
                "id": plo.id,
                "university_code": plo.university_code,
                "specialty_code": plo.specialty_code,
                "plo_code": plo.plo_code,
                "language_code": translation.language_code,
                "plo_content": translation.plo_content
            })

        return JSONResponse(
            content={
                "statusCode": 200,
                "message": "All PLOs fetched successfully",
                "plos": plos
            },
            status_code=200
        )

    except Exception as e:
        return JSONResponse(
            content={"statusCode": 500, "error": str(e)},
            status_code=500
        )

# GET by specialty_code
async def get_plos_by_specialty(
        specialty_code: str,
        lang: str = "en",
        db: AsyncSession = Depends(get_db)
):
    try:
        query = (
            select(Plo, PloTranslation)
            .join(PloTranslation, Plo.plo_code == PloTranslation.plo_code)
            .where(PloTranslation.language_code == lang)
        )       

        result = await db.execute(query)
        rows = result.all()

        if not rows:
            return JSONResponse(
                content={
                    "statusCode": 200,
                    "message": "No PLO found for this specialty",
                    "plos": []
                },
                status_code=200
            )
        plos = []
        for plo, translation in rows:
            plos.append({
                "id": plo.id,
                "university_code": plo.university_code,
                "specialty_code": plo.specialty_code,
                "plo_code": plo.plo_code,
                "language_code": translation.language_code,
                "plo_content": translation.plo_content 
            })
        return JSONResponse(
            content={
                "statusCode": 200,
                "message":"PLOs fetched succesfully!",
                "plos": plos
            },
            status_code=200
        )

    except Exception as e:
        return JSONResponse(
            content={
                "statusCode":404,
                "error":str(e)
            },
            status_code=404
        )

# Create PLO with translations
async def create_plo(
        db: AsyncSession,
        plo_data
):
    try:
        db_plo = Plo(
            university_code = plo_data.university_code,
            specialty_code = plo_data.specialty_code,
            plo_code = plo_data.plo_code 
        )
        db.add(db_plo)
        await db.flush()

        for t in plo_data.translations:
            db_translation = PloTranslation(
                plo_code = db_plo.plo_code,
                language_code = t.language_code,
                plo_content = t.plo_content  
            )
            db.add(db_translation)

        await db.commit()
        await db.refresh(db_plo)

        return JSONResponse(
            content={
                "statusCode": 201,
                "message": "PLO created succesfully!",
                "plo_code": db_plo.plo_code
            },
            status_code=201
        )
    
    except Exception as e:
        await db.rollback()
        return JSONResponse(
            content={
                "statusCode": 404,
                "error":str(e)
            },
            status_code=404
        )

# DELETE PLO by plo_code
async def delete_plo(db: AsyncSession, plo_code: str):
    try:
        result = await db.execute(select(Plo).where(Plo.plo_code == plo_code))
        plo = result.scalars().first()
        if not plo:
            return JSONResponse({"statusCode": 404, "error": "PLO not found"}, status_code=404)

        await db.delete(plo)
        await db.commit()
        return JSONResponse({"statusCode": 200, "message": "PLO deleted successfully"}, status_code=200)

    except Exception as e:
        await db.rollback()
        return JSONResponse({"statusCode": 500, "error": str(e)}, status_code=500)

# UPDATE PLO by plo_code
async def update_plo(db: AsyncSession, plo_code: str, plo_data: CreatePlo):
    try:
        result = await db.execute(select(Plo).where(Plo.plo_code == plo_code))
        plo = result.scalars().first()
        if not plo:
            return JSONResponse({"statusCode": 404, "error": "PLO not found"}, status_code=404)

        plo.university_code = plo_data.university_code
        plo.specialty_code = plo_data.specialty_code
        plo.plo_code = plo_data.plo_code

        # update translations
        await db.execute(
            sa.delete(PloTranslation).where(PloTranslation.plo_code == plo_code)
        )
        for t in plo_data.translations:
            db.add(PloTranslation(
                plo_code = plo_data.plo_code,
                language_code = t.language_code,
                plo_content = t.plo_content
            ))

        await db.commit()
        await db.refresh(plo)
        return JSONResponse({"statusCode": 200, "message": "PLO updated successfully"}, status_code=200)

    except Exception as e:
        await db.rollback()
        return JSONResponse({"statusCode": 500, "error": str(e)}, status_code=500)











