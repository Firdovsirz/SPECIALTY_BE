from fastapi import Depends
from fastapi.responses import JSONResponse
from app.db.session import get_db
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.slo import Slo
from app.models.slo_translations import SloTranslation
import sqlalchemy as sa
from app.api.v1.schemas.slo import SloCreate
from app.utils.language import get_language
from app.models.university import University
from app.models.speciality import Specialty


allowed_languages = ["en","az"]

async def get_all_slos(db: AsyncSession, lang: str = Depends(get_language)):
    if lang not in allowed_languages:
        return JSONResponse(
            content={
                "statusCode": 400,
                "message":"Invalid language code!"
            },
            status_code=400
        )
    try:
        result = await db.execute(
            select(Slo, SloTranslation)
            .join(SloTranslation, Slo.slo_code == SloTranslation.slo_code)
            .where(SloTranslation.language_code == lang)
        )
        rows = result.all()

        if not rows:
            return JSONResponse(
                content={
                    "statusCode": 204,
                    "message": f"No SLO found for language '{lang}'!"
                },
                status_code=204
            )

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
                "message":  f"All SLOs fetched successfully for language '{lang}'",
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
    lang: str,
    db: AsyncSession
):
    if lang not in allowed_languages:
        return JSONResponse(
            content={"statusCode": 400, "message": "Invalid language code!"},
            status_code=400
        )

    try:
        query = (
            select(Slo, SloTranslation)
            .join(SloTranslation, Slo.slo_code == SloTranslation.slo_code)
            .where(Slo.specialty_code == specialty_code)
            .where(SloTranslation.language_code == lang)
        )

        result = await db.execute(query)
        rows = result.all()

        if not rows:
            return JSONResponse(
                content={
                    "statusCode": 204,
                    "message": "No SLO found for this specialty!",
                },
                status_code=204
            )

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
                "message": "SLOs fetched successfully!",
                "slos": slos
            },
            status_code=200
        )

    except Exception as e:
        return JSONResponse(
            content={"statusCode": 500, "error": str(e)},
            status_code=500
        )


# Create SLO with translations
async def create_slo(db: AsyncSession, slo_data, lang: str):
    try:
        if lang not in allowed_languages:
            return JSONResponse(
                content={"statusCode": 400, "message": "Invalid language code! Allowed: az, en"},
                status_code=400
            )

        result = await db.execute(select(Slo).where(Slo.slo_code == slo_data.slo_code))
        base_slo = result.scalars().first()

        if base_slo is None:
            new_slo = Slo(
                university_code=slo_data.university_code,
                specialty_code=slo_data.specialty_code,
                slo_code=slo_data.slo_code,
            )
            db.add(new_slo)

            new_translation = SloTranslation(
                slo_code=slo_data.slo_code,
                language_code=lang,
                slo_content=slo_data.slo_content,
            )
            db.add(new_translation)

            await db.commit()
            return JSONResponse(
                content={
                    "statusCode": 201,
                    "message": f"SLO created successfully with translation ({lang})",
                    "slo_code": slo_data.slo_code
                },
                status_code=201
            )

        if (
            base_slo.university_code != slo_data.university_code
            or base_slo.specialty_code != slo_data.specialty_code
        ):
            return JSONResponse(
                content={
                    "statusCode": 409,
                    "message": (
                        "SLO exists but university_code/specialty_code mismatch."
                    ),
                },
                status_code=409
            )

        translation_q = await db.execute(
            select(SloTranslation).where(
                SloTranslation.slo_code == slo_data.slo_code,
                SloTranslation.language_code == lang
            )
        )
        existing_translation = translation_q.scalars().first()

        if existing_translation:
            return JSONResponse(
                content={
                    "statusCode": 409,
                    "message": f"SLO translation already exists for '{lang}'."
                },
                status_code=409
            )

        new_translation = SloTranslation(
            slo_code=slo_data.slo_code,
            language_code=lang,
            slo_content=slo_data.slo_content,
        )
        db.add(new_translation)
        await db.commit()

        return JSONResponse(
            content={
                "statusCode": 201,
                "message": f"SLO translation added for '{lang}'",
                "slo_code": slo_data.slo_code
            },
            status_code=201
        )

    except Exception as e:
        await db.rollback()
        return JSONResponse(
            content={"statusCode": 500, "error": str(e)},
            status_code=500
        )


# DELETE SLO by slo_code
async def delete_slo(db: AsyncSession, slo_code: str):
    try:
        result = await db.execute(select(Slo).where(Slo.slo_code == slo_code))
        slo = result.scalars().first()
        if not slo:
            return JSONResponse(
                {"statusCode": 404, "error": "SLO not found!"},
                status_code=404
            )

        await db.execute(
            SloTranslation.__table__.delete().where(SloTranslation.slo_code == slo_code)
        )

        await db.delete(slo)
        await db.commit()

        return JSONResponse(
            {"statusCode": 200, "message": "SLO and its translations deleted successfully"},
            status_code=200
        )

    except Exception as e:
        await db.rollback()
        return JSONResponse(
            {"statusCode": 500, "error": str(e)},
            status_code=500
        )

# UPDATE SLO by slo_code
async def update_slo(db: AsyncSession, slo_code: str, slo_data, lang: str):
    if lang not in allowed_languages:
        return JSONResponse({"statusCode": 400, "message": "Invalid language code! (az|en)"}, status_code=400)

    try:
        res = await db.execute(select(Slo).where(Slo.slo_code == slo_code))
        slo = res.scalars().first()
        if not slo:
            return JSONResponse({"statusCode": 404, "error": "SLO not found"}, status_code=404)

        if slo.university_code != slo_data.university_code:
            uni_q = await db.execute(select(University).where(University.university_code == slo_data.university_code))
            if not uni_q.scalars().first():
                return JSONResponse({"statusCode": 400, "error": "University code does not exist!"}, status_code=400)

        if slo.specialty_code != slo_data.specialty_code:
            spec_q = await db.execute(select(Specialty).where(Specialty.specialty_code == slo_data.specialty_code))
            if not spec_q.scalars().first():
                return JSONResponse({"statusCode": 400, "error": "Specialty code does not exist!"}, status_code=400)

        slo.university_code = slo_data.university_code
        slo.specialty_code = slo_data.specialty_code

        tr_res = await db.execute(
            select(SloTranslation).where(
                SloTranslation.slo_code == slo_code,
                SloTranslation.language_code == lang
            )
        )
        tr = tr_res.scalars().first()
        if tr:
            tr.slo_content = slo_data.slo_content
        else:
            db.add(SloTranslation(
                slo_code=slo_code,
                language_code=lang,
                slo_content=slo_data.slo_content
            ))

        await db.commit()
        await db.refresh(slo)
        return JSONResponse({"statusCode": 200, "message": f"SLO updated successfully for language '{lang}'"}, status_code=200)

    except Exception as e:
        await db.rollback()
        return JSONResponse({"statusCode": 500, "error": str(e)}, status_code=500)
    
