from fastapi import Depends
from fastapi.responses import JSONResponse
from app.db.session import get_db
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.gco import GCO
from app.models.gco_translations import GCOTranslation
import sqlalchemy as sa
from app.api.v1.schemas.gco import GCOCreate
from app.utils.language import get_language
from app.models.university import University
from app.models.speciality import Specialty

allowed_languages = ["en", "az"]

# GET All GCOs
async def get_all_gcos(db: AsyncSession, lang: str = Depends(get_language)):
    if lang not in allowed_languages:
        return JSONResponse(content={
            "statusCode": 404,
            "message": "Invalid language code!"
        }, 
        status_code=404
    )

    try:
        result = await db.execute(
            select(GCO, GCOTranslation)
            .join(GCOTranslation, GCO.career_code == GCOTranslation.career_code)
            .where(GCOTranslation.language_code == lang)
        )
        rows = result.all()

        if not rows:
            return JSONResponse(
                content={
                    "statusCode": 204,
                    "message": f"No GCO found for language '{lang}!'"
                },
                status_code=204
            )

        gcos = []
        for gco, translation in rows:
            gcos.append(
                {
                    "id": gco.id,
                    "university_code": gco.university_code,
                    "specialty_code": gco.specialty_code,
                    "career_code": gco.career_code,
                    "language_code": translation.language_code,
                    "career_content": translation.career_content
                }
            )

        return JSONResponse(
            content={
                "statusCode": 200,
                "message": f"All GCOs fetched successfully for language '{lang}'!",
                "gcos": gcos
            },
            status_code=200
        )

    except Exception as e:
        return JSONResponse(
            content={
                "statusCode": 500,
                "error": str(e)
            },
            status_code=500
        )


# GET GCOs by specialty_code
async def get_gcos_by_specialty(specialty_code: str, lang: str, db: AsyncSession):
    if lang not in allowed_languages:
        return JSONResponse(
            content={
                "statusCode": 404,
                "message": "Invalid language code!"
            },
            status_code=404
        )

    try:
        spec_q = await db.execute(
            select(Specialty).where(Specialty.specialty_code == specialty_code)
        )
        if not spec_q.scalars().first():
            return JSONResponse(
                content={
                    "statusCode": 404,
                    "message": "Specialty not found!"
                },
                status_code=404
            )

        query = (
            select(GCO, GCOTranslation)
            .join(GCOTranslation, GCO.career_code == GCOTranslation.career_code)
            .where(GCO.specialty_code == specialty_code)
            .where(GCOTranslation.language_code == lang)
        )
        result = await db.execute(query)
        rows = result.all()

        if not rows:
            return JSONResponse(
                content={
                    "statusCode": 204,
                    "message": "No GCO found for this specialty in the requested language!",
                },
                status_code=204
            )

        gcos = []
        for gco, translation in rows:
            gcos.append(
                {
                    "id": gco.id,
                    "university_code": gco.university_code,
                    "specialty_code": gco.specialty_code,
                    "career_code": gco.career_code,
                    "language_code": translation.language_code,
                    "career_content": translation.career_content
                }
            )

        return JSONResponse(
            content={
                "statusCode": 200,
                "message": "GCOs fetched successfully!",
                "gcos": gcos
            },
            status_code=200
        )

    except Exception as e:
        return JSONResponse(
            content={
                "statusCode": 500,
                "error": str(e)
            },
            status_code=500
        )


# CREATE GCO
async def create_gco(db: AsyncSession, gco_data: GCOCreate, lang: str):
    try:
        if lang not in allowed_languages:
            return JSONResponse(
                content={"statusCode": 404, "message": "Invalid language code!"},
                status_code=404
            )
        result = await db.execute(
            select(GCO).where(GCO.career_code == gco_data.career_code)
        )
        base_gco = result.scalars().first()

        if base_gco is None:
            uni_q = await db.execute(
                select(University).where(University.university_code == gco_data.university_code)
            )
            specialty_q = await db.execute(
                select(Specialty).where(Specialty.specialty_code == gco_data.specialty_code)
            )

            if not uni_q.scalars().first():
                return JSONResponse(
                    content={"statusCode": 404, "message": "University code does not exist!"},
                    status_code=404
                )

            if not specialty_q.scalars().first():
                return JSONResponse(
                    content={"statusCode": 404, "message": "Specialty code does not exist!"},
                    status_code=404
                )

            new_gco = GCO(
                university_code=gco_data.university_code,
                specialty_code=gco_data.specialty_code,
                career_code=gco_data.career_code
            )
            db.add(new_gco)

            new_translation = GCOTranslation(
                career_code=gco_data.career_code,
                language_code=lang,
                career_content=gco_data.career_content
            )
            db.add(new_translation)

            await db.commit()
            return JSONResponse(
                content={
                    "statusCode": 201,
                    "message": f"GCO created successfully with translation ({lang})!",
                    "career_code": gco_data.career_code
                },
                status_code=201
            )

        if (base_gco.university_code != gco_data.university_code or 
            base_gco.specialty_code != gco_data.specialty_code):
            return JSONResponse(
                content={
                    "statusCode": 409,
                    "message": "GCO exists but university_code/specialty_code mismatch!"
                },
                status_code=409
            )

        translation_q = await db.execute(
            select(GCOTranslation)
            .where(GCOTranslation.career_code == gco_data.career_code)
            .where(GCOTranslation.language_code == lang)
        )
        existing_translation = translation_q.scalars().first()

        if existing_translation:
            return JSONResponse(
                content={
                    "statusCode": 409,
                    "message": f"GCO translation already exists for '{lang}'!"
                },
                status_code=409
            )
        
        new_translation = GCOTranslation(
            career_code=gco_data.career_code,
            language_code=lang,
            career_content=gco_data.career_content
        )
        db.add(new_translation)
        await db.commit()

        return JSONResponse(
            content={
                "statusCode": 201,
                "message": f"GCO translation added for '{lang}'",
                "career_code": gco_data.career_code
            },
            status_code=201
        )

    except Exception as e:
        await db.rollback()
        return JSONResponse(
            content={"statusCode": 500, "error": str(e)},
            status_code=500
        )


# DELETE GCO
async def delete_gco(db: AsyncSession, career_code: str):
    try:
        result = await db.execute(
            select(GCO).where(GCO.career_code == career_code)
        )
        gco = result.scalars().first()
        if not gco:
            return JSONResponse(
                {"statusCode": 404, "error": "GCO not found!"},
                status_code=404,
            )

        await db.execute(
            GCOTranslation.__table__.delete().where(
                GCOTranslation.career_code == career_code
            )
        )

        await db.delete(gco)
        await db.commit()

        return JSONResponse(
            {
                "statusCode": 200,
                "message": "GCO and its translations deleted successfully!",
            },
            status_code=200,
        )

    except Exception as e:
        await db.rollback()
        return JSONResponse(
            {"statusCode": 500, "error": str(e)},
            status_code=500,
        )


# UPDATE GCO
async def update_gco(db: AsyncSession, career_code: str, gco_data, lang: str):
    if lang not in allowed_languages:
        return JSONResponse(
            content={
                "statusCode": 404,
                "message": "Invalid language code!"
            },
            status_code=404
        )

    try:
        res = await db.execute(
            select(GCO).where(GCO.career_code == career_code)
        )
        gco = res.scalars().first()
        if not gco:
            return JSONResponse(
                {"statusCode": 404, "error": "GCO not found!"},
                status_code=404,
            )

        if gco.university_code != gco_data.university_code:
            uni_q = await db.execute(
                select(University).where(
                    University.university_code == gco_data.university_code
                )
            )
            if not uni_q.scalars().first():
                return JSONResponse(
                    {
                        "statusCode": 404,
                        "error": "University code does not exist!",
                    },
                    status_code=404,
                )

        if gco.specialty_code != gco_data.specialty_code:
            spec_q = await db.execute(
                select(Specialty).where(
                    Specialty.specialty_code == gco_data.specialty_code
                )
            )
            if not spec_q.scalars().first():
                return JSONResponse(
                    {
                        "statusCode": 404,
                        "error": "Specialty code does not exist!",
                    },
                    status_code=404,
                )

        tr_res = await db.execute(
            select(GCOTranslation).where(
                GCOTranslation.career_code == career_code,
                GCOTranslation.language_code == lang,
            )
        )
        tr = tr_res.scalars().first()

        if not tr:
            return JSONResponse(
                {
                    "statusCode": 404,
                    "error": f"GCO translation for language '{lang}' does not exist!"
                },
                status_code=404,
            )
        
        gco.university_code = gco_data.university_code
        gco.specialty_code = gco_data.specialty_code
        tr.career_content = gco_data.career_content

        await db.commit()
        await db.refresh(gco)

        return JSONResponse(
            {
                "statusCode": 200,
                "message": f"GCO updated successfully for language '{lang}'!",
            },
            status_code=200,
        )

    except Exception as e:
        await db.rollback()
        return JSONResponse(
            {"statusCode": 500, "error": str(e)},
            status_code=500
        )













