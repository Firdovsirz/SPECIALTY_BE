from fastapi import Depends
from fastapi.responses import JSONResponse
from app.db.session import get_db
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.slo import Slo
from app.models.slo_translations import SloTranslation
import sqlalchemy as sa
from app.api.v1.schemas.slo import SloCreate


async def get_all_slos(db: AsyncSession):
    try:
        result = await db.execute(select(Slo, SloTranslation).join(SloTranslation, Slo.slo_code == SloTranslation.slo_code))
        rows = result.all()

        slos = []
        for slo, translation in rows:
            slos.append({
                "id": slo.id,
                "university_code": slo.university_code,
                "specialty_code": slo.specialty_code,
                "slo_code": slo.slo_code,
                "language_code": translation.language_code,
                "slo_content": translation.slo_content
            })

        return JSONResponse(
            content={
                "statusCode": 200,
                "message": "All SLOs fetched successfully",
                "slos": slos
            },
            status_code=200
        )

    except Exception as e:
        return JSONResponse(
            content={"statusCode": 500, "error": str(e)},
            status_code=500
        )


# GET by specialty_code
async def get_slos_by_specialty(
        specialty_code: str,
        lang: str = "en",
        db: AsyncSession = Depends(get_db)
):
    try:
        query = (
            select(Slo,SloTranslation)
            .join(SloTranslation, Slo.slo_code == specialty_code)
            .where(SloTranslation.language_code == lang)
        )
        result = await db.execute(query)
        rows = result.all()

        if not rows:
            return JSONResponse(
                content={
                    "statusCode": 200,
                    "message": "No SLO found for this specialty!",
                    "slos":[]
                },
                status_code=200
            )
        slos = []
        for slo, translation in rows:
            slos.append({
                "id": slo.id,
                "university_code": slo.university_code,
                "slo_code": slo.slo_code,
                "language_code": translation.language_code,
                "slo_content": translation.slo_content
            })
        return JSONResponse(
            content={
                "statusCode": 200,
                "message": "SLOs fetched succesfully!",
                "slos": slos
            },
            status_code=200
        )
    except Exception as e:
        return JSONResponse(
            content={
                "statusCode": 404,
                "error": str(e)
            },
            status_code=404
        )

# Create SLO with translations
async def create_slo(
        db: AsyncSession,
        slo_data
):
    try:
        db_slo = Slo(
            university_code = slo_data.university_code,
            specialty_code = slo_data.specialty_code,
            slo_code = slo_data.slo_code
        )
        db.add(db_slo)
        await db.flush()

        for t in slo_data.translations:
            db_translations = SloTranslation(
                slo_code = db_slo.slo_code,
                language_code = t.language_code,
                slo_content = t.slo_content
            )
            db.add(db_translations)

        await db.commit()
        await db.refresh(db_slo)

        return JSONResponse(
            content={
                "statusCode": 201,
                "message": "SLO created succesfully!",
                "slo_code": db_slo.slo_code
            },
            status_code=201
        )
    except Exception as e:
        await db.rollback()
        return JSONResponse(
            content={
                "statusCode": 404,
                "error": str(e)
            },
            status_code=404
        )


# DELETE SLO by slo_code
async def delete_slo(db: AsyncSession, slo_code: str):
    try:
        result = await db.execute(
            select(Slo).where(Slo.slo_code == slo_code)
        )
        slo = result.scalars().first()
        if not slo:
            return JSONResponse({"statusCode": 404, "error": "SLO not found"}, status_code=404)
        
        await db.delete(slo)
        await db.commit()
        return JSONResponse({"statusCode": 200, "message": "SLO deleted successfully"}, status_code=200)
    
    except Exception as e:
        await db.rollback()
        return JSONResponse({"statusCode": 500, "error": str(e)}, status_code=500)


# UPDATE SLO by slo_code
async def update_slo(db: AsyncSession, slo_code: str, slo_data: SloCreate):
    try:
        result = await db.execute(select(Slo).where(Slo.slo_code == slo_code))
        slo = result.scalars().first()
        if not slo:
            return JSONResponse({"statusCode": 404, "error": "SLO not found"}, status_code=404)

        slo.university_code = slo_data.university_code
        slo.specialty_code = slo_data.specialty_code
        slo.slo_code = slo_data.slo_code

        # update translations
        await db.execute(
            sa.delete(SloTranslation).where(SloTranslation.slo_code == slo_code)
        )
        for t in slo_data.translations:
            db.add(SloTranslation(
                slo_code = slo_data.slo_code,
                language_code = t.language_code,
                slo_content = t.slo_content
            ))

        await db.commit()
        await db.refresh(slo)
        return JSONResponse({"statusCode": 200, "message": "SLO updated successfully"}, status_code=200)

    except Exception as e:
        await db.rollback()
        return JSONResponse({"statusCode": 500, "error": str(e)}, status_code=500)


