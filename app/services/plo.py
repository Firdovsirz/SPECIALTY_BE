from fastapi import Depends
from fastapi.responses import JSONResponse
from app.db.session import get_db
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.plo import Plo
from app.models.plo_translations import PloTranslation
import sqlalchemy as sa
from app.api.v1.schemas.plo import PloCreate
from app.utils.language import get_language
from app.models.university import University
from app.models.speciality import Specialty

allowed_languages = ["en","az"]

async def get_all_plos(db: AsyncSession, lang: str = Depends(get_language)):
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
            select(Plo, PloTranslation)
            .join(PloTranslation, Plo.plo_code == PloTranslation.plo_code)
            .where(PloTranslation.language_code == lang)
        )
        rows = result.all()

        if not rows:
            return JSONResponse(
                content={
                    "statusCode": 204,
                    "message": f"No PLO found for language '{lang}'!"
                },
                status_code=204
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
                "message":  f"All PLOs fetched successfully for language '{lang}'",
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
            select(Plo, PloTranslation)
            .join(PloTranslation, Plo.plo_code == PloTranslation.plo_code)
            .where(Plo.specialty_code == specialty_code)
            .where(PloTranslation.language_code == lang)
        )

        result = await db.execute(query)
        rows = result.all()

        if not rows:
            return JSONResponse(
                content={
                    "statusCode": 204,
                    "message": "No PLO found for this specialty!",
                },
                status_code=204
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
                "message": "PLOs fetched successfully!",
                "plos": plos
            },
            status_code=200
        )

    except Exception as e:
        return JSONResponse(
            content={"statusCode": 500, "error": str(e)},
            status_code=500
        )

# Create PLO with translations
async def create_plo(db: AsyncSession, plo_data, lang: str):
    try:
        if lang not in allowed_languages:
            return JSONResponse(
                content={"statusCode": 400, "message": "Invalid language code! Allowed: az, en"},
                status_code=400
            )

        result = await db.execute(select(Plo).where(Plo.plo_code == plo_data.plo_code))
        base_plo = result.scalars().first()

        if base_plo is None:
            new_plo = Plo(
                university_code=plo_data.university_code,
                specialty_code=plo_data.specialty_code,
                plo_code=plo_data.plo_code,
            )
            db.add(new_plo)

            new_translation = PloTranslation(
                plo_code=plo_data.plo_code,
                language_code=lang,
                plo_content=plo_data.plo_content,
            )
            db.add(new_translation)

            await db.commit()
            return JSONResponse(
                content={
                    "statusCode": 201,
                    "message": f"PLO created successfully with translation ({lang})",
                    "plo_code": plo_data.plo_code
                },
                status_code=201
            )

        if (
            base_plo.university_code != plo_data.university_code
            or base_plo.specialty_code != plo_data.specialty_code
        ):
            return JSONResponse(
                content={
                    "statusCode": 409,
                    "message": (
                        "PLO exists but university_code/specialty_code mismatch."
                    ),
                },
                status_code=409
            )

        translation_q = await db.execute(
            select(PloTranslation).where(
                PloTranslation.plo_code == plo_data.plo_code,
                PloTranslation.language_code == lang
            )
        )
        existing_translation = translation_q.scalars().first()

        if existing_translation:
            return JSONResponse(
                content={
                    "statusCode": 409,
                    "message": f"PLO translation already exists for '{lang}'."
                },
                status_code=409
            )

        new_translation = PloTranslation(
            plo_code=plo_data.plo_code,
            language_code=lang,
            plo_content=plo_data.plo_content,
        )
        db.add(new_translation)
        await db.commit()

        return JSONResponse(
            content={
                "statusCode": 201,
                "message": f"PLO translation added for '{lang}'",
                "plo_code": plo_data.plo_code
            },
            status_code=201
        )

    except Exception as e:
        await db.rollback()
        return JSONResponse(
            content={"statusCode": 500, "error": str(e)},
            status_code=500
        )


# DELETE PLO by plo_code
async def delete_plo(db: AsyncSession, plo_code: str):
    try:
        result = await db.execute(select(Plo).where(Plo.plo_code == plo_code))
        plo = result.scalars().first()
        if not plo:
            return JSONResponse(
                {"statusCode": 404, "error": "PLO not found!"},
                status_code=404
            )

        await db.execute(
            PloTranslation.__table__.delete().where(PloTranslation.plo_code == plo_code)
        )

        await db.delete(plo)
        await db.commit()

        return JSONResponse(
            {"statusCode": 200, "message": "PLO and its translations deleted successfully"},
            status_code=200
        )

    except Exception as e:
        await db.rollback()
        return JSONResponse(
            {"statusCode": 500, "error": str(e)},
            status_code=500
        )

# UPDATE PLO by plo_code
async def update_plo(db: AsyncSession, plo_code: str, plo_data, lang: str):
    if lang not in allowed_languages:
        return JSONResponse({"statusCode": 400, "message": "Invalid language code! (az|en)"}, status_code=400)

    try:
        res = await db.execute(select(Plo).where(Plo.plo_code == plo_code))
        plo = res.scalars().first()
        if not plo:
            return JSONResponse({"statusCode": 404, "error": "PLO not found"}, status_code=404)

        if plo.university_code != plo_data.university_code:
            uni_q = await db.execute(select(University).where(University.university_code == plo_data.university_code))
            if not uni_q.scalars().first():
                return JSONResponse({"statusCode": 400, "error": "University code does not exist!"}, status_code=400)

        if plo.specialty_code != plo_data.specialty_code:
            spec_q = await db.execute(select(Specialty).where(Specialty.specialty_code == plo_data.specialty_code))
            if not spec_q.scalars().first():
                return JSONResponse({"statusCode": 400, "error": "Specialty code does not exist!"}, status_code=400)

        plo.university_code = plo_data.university_code
        plo.specialty_code = plo_data.specialty_code

        tr_res = await db.execute(
            select(PloTranslation).where(
                PloTranslation.plo_code == plo_code,
                PloTranslation.language_code == lang
            )
        )
        tr = tr_res.scalars().first()
        if tr:
            tr.plo_content = plo_data.plo_content
        else:
            db.add(PloTranslation(
                plo_code=plo_code,
                language_code=lang,
                plo_content=plo_data.plo_content
            ))

        await db.commit()
        await db.refresh(plo)
        return JSONResponse({"statusCode": 200, "message": f"PLO updated successfully for language '{lang}'"}, status_code=200)

    except Exception as e:
        await db.rollback()
        return JSONResponse({"statusCode": 500, "error": str(e)}, status_code=500)
   










