from fastapi import Depends
from fastapi.responses import JSONResponse
from app.db.session import get_db
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.competency import Competency
from app.models.competency_tranlation import CompetencyTranslation
import sqlalchemy as sa
from app.api.v1.schemas.competency import CompetencyCreate
from app.utils.language import get_language
from app.models.university import University
from app.models.speciality import Specialty

allowed_languages = ["en", "az"]

# GET All Competencies
async def get_all_competency(db: AsyncSession, lang: str = Depends(get_language)):
    if lang not in allowed_languages:
        return JSONResponse(content={
            "statusCode": 404,
            "message": "Invalid language code!"
        }, 
        status_code=404
    )

    try:
        result = await db.execute(
            select(Competency, CompetencyTranslation)
            .join(CompetencyTranslation, Competency.competency_code == CompetencyTranslation.competency_code)
            .where(CompetencyTranslation.language_code == lang)
        )
        rows = result.all()

        if not rows:
            return JSONResponse(
                content={
                    "statusCode": 204,
                    "message": f"No competency found for language '{lang}!'"
                },
                status_code=204
            )

        competencies = []
        for competency, translation in rows:
            competencies.append(
                {
                    "id": competency.id,
                    "university_code": competency.university_code,
                    "specialty_code": competency.specialty_code,
                    "competency_code": competency.competency_code,
                    "language_code": translation.language_code,
                    "competency_content": translation.competency_content
                }
            )

        return JSONResponse(
            content={
                "statusCode": 200,
                "message": f"All competencies fetched successfully for language '{lang}'!",
                "competencies": competencies
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


# GET Competencies by specialty_code
async def get_competencies_by_specialty(specialty_code: str, lang: str, db: AsyncSession):
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
            select(Competency, CompetencyTranslation)
            .join(CompetencyTranslation, Competency.competency_code == CompetencyTranslation.competency_code)
            .where(Competency.specialty_code == specialty_code)
            .where(CompetencyTranslation.language_code == lang)
        )
        result = await db.execute(query)
        rows = result.all()

        if not rows:
            return JSONResponse(
                content={
                    "statusCode": 204,
                    "message": "No competency found for this specialty in the requested language!",
                },
                status_code=204
            )

        competencies = []
        for competency, translation in rows:
            competencies.append(
                {
                    "id": competency.id,
                    "university_code": competency.university_code,
                    "specialty_code": competency.specialty_code,
                    "competency_code": competency.competency_code,
                    "language_code": translation.language_code,
                    "competency_content": translation.competency_content
                }
            )

        return JSONResponse(
            content={
                "statusCode": 200,
                "message": "Competencies fetched successfully!",
                "competencies": competencies
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


# CREATE Competency
async def create_competency(db: AsyncSession, competency_data: CompetencyCreate, lang: str):
    try:
        if lang not in allowed_languages:
            return JSONResponse(
                content={"statusCode": 404, "message": "Invalid language code!"},
                status_code=404
            )
        result = await db.execute(
            select(Competency).where(Competency.competency_code == competency_data.competency_code)
        )
        base_competency = result.scalars().first()

        if base_competency is None:
            uni_q = await db.execute(
                select(University).where(University.university_code == competency_data.university_code)
            )
            specialty_q = await db.execute(
                select(Specialty).where(Specialty.specialty_code == competency_data.specialty_code)
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

            new_competency = Competency(
                university_code=competency_data.university_code,
                specialty_code=competency_data.specialty_code,
                competency_code=competency_data.competency_code
            )
            db.add(new_competency)

            new_translation = CompetencyTranslation(
                competency_code=competency_data.competency_code,
                language_code=lang,
                competency_content=competency_data.competency_content
            )
            db.add(new_translation)

            await db.commit()
            return JSONResponse(
                content={
                    "statusCode": 201,
                    "message": f"Competency created successfully with translation ({lang})!",
                    "competency_code": competency_data.competency_code
                },
                status_code=201
            )

        if (base_competency.university_code != competency_data.university_code or 
            base_competency.specialty_code != competency_data.specialty_code):
            return JSONResponse(
                content={
                    "statusCode": 409,
                    "message": "Competency exists but university_code/specialty_code mismatch!"
                },
                status_code=409
            )

        translation_q = await db.execute(
            select(CompetencyTranslation)
            .where(CompetencyTranslation.competency_code == competency_data.competency_code)
            .where(CompetencyTranslation.language_code == lang)
        )
        existing_translation = translation_q.scalars().first()

        if existing_translation:
            return JSONResponse(
                content={
                    "statusCode": 409,
                    "message": f"Competency translation already exists for '{lang}'!"
                },
                status_code=409
            )
        
        new_translation = CompetencyTranslation(
            competency_code=competency_data.competency_code,
            language_code=lang,
            competency_content=competency_data.competency_content
        )
        db.add(new_translation)
        await db.commit()

        return JSONResponse(
            content={
                "statusCode": 201,
                "message": f"Competency translation added for '{lang}'",
                "competency_code": competency_data.competency_code
            },
            status_code=201
        )

    except Exception as e:
        await db.rollback()
        return JSONResponse(
            content={"statusCode": 500, "error": str(e)},
            status_code=500
        )


# DELETE Competency
async def delete_competency(db: AsyncSession, competency_code: str):
    try:
        result = await db.execute(
            select(Competency).where(Competency.competency_code == competency_code)
        )
        competency = result.scalars().first()
        if not competency:
            return JSONResponse(
                {"statusCode": 404, "error": "Competency not found!"},
                status_code=404,
            )

        await db.execute(
            CompetencyTranslation.__table__.delete().where(
                CompetencyTranslation.competency_code == competency_code
            )
        )

        await db.delete(competency)
        await db.commit()

        return JSONResponse(
            {
                "statusCode": 200,
                "message": "Competency and its translations deleted successfully!",
            },
            status_code=200,
        )

    except Exception as e:
        await db.rollback()
        return JSONResponse(
            {"statusCode": 500, "error": str(e)},
            status_code=500,
        )


# UPDATE Competency
async def update_competency(db: AsyncSession, competency_code: str, competency_data, lang: str):
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
            select(Competency).where(Competency.competency_code == competency_code)
        )
        competency = res.scalars().first()
        if not competency:
            return JSONResponse(
                {"statusCode": 404, "error": "Competency not found!"},
                status_code=404,
            )

        if competency.university_code != competency_data.university_code:
            uni_q = await db.execute(
                select(University).where(
                    University.university_code == competency_data.university_code
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

        if competency.specialty_code != competency_data.specialty_code:
            spec_q = await db.execute(
                select(Specialty).where(
                    Specialty.specialty_code == competency_data.specialty_code
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
            select(CompetencyTranslation).where(
                CompetencyTranslation.competency_code == competency_code,
                CompetencyTranslation.language_code == lang,
            )
        )
        tr = tr_res.scalars().first()

        if not tr:
            return JSONResponse(
                {
                    "statusCode": 404,
                    "error": f"Competency translation for language '{lang}' does not exist!"
                },
                status_code=404,
            )
        
        competency.university_code = competency_data.university_code
        competency.specialty_code = competency_data.specialty_code
        tr.competency_content = competency_data.competency_content

        await db.commit()
        await db.refresh(competency)

        return JSONResponse(
            {
                "statusCode": 200,
                "message": f"Competency updated successfully for language '{lang}'!",
            },
            status_code=200,
        )

    except Exception as e:
        await db.rollback()
        return JSONResponse(
            {"statusCode": 500, "error": str(e)},
            status_code=500
        )













