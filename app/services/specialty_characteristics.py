# services/specialty_characteristics.py
from fastapi import Depends
from fastapi.responses import JSONResponse
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.specialty_characteristics import SpecialtyCharacteristics
from app.models.specialty_characteristics_translation import SpecialtyCharacteristicsTranslation
from app.models.speciality import Specialty
from app.api.v1.schemas.specialty_characteristics import (
    SpecialtyCharacteristicsCreate,
    SpecialtyCharacteristicsUpdate,
    SpecialtyCharacteristicsTranslationOut
)

allowed_languages = ["en", "az"]

# GET SpecialtyCharacteristics by specialty_code
async def get_specialty_characteristics_by_specialty(db: AsyncSession, specialty_code: str, lang: str):
    if lang not in allowed_languages:
        return JSONResponse({"statusCode": 404, "message": "Invalid language code!"}, status_code=404)

    try:
        spec_q = await db.execute(select(Specialty).where(Specialty.specialty_code == specialty_code))
        specialty = spec_q.scalars().first()
        if not specialty:
            return JSONResponse({"statusCode": 404, "message": f"Specialty '{specialty_code}' not found!"}, status_code=404)
        
        result = await db.execute(
            select(SpecialtyCharacteristics, SpecialtyCharacteristicsTranslation)
            .join(SpecialtyCharacteristicsTranslation, SpecialtyCharacteristics.id == SpecialtyCharacteristicsTranslation.specialty_characteristic_id)
            .where(SpecialtyCharacteristics.id == SpecialtyCharacteristicsTranslation.specialty_characteristic_id)
            .where(SpecialtyCharacteristics.specialty_code == specialty_code)
            .where(SpecialtyCharacteristicsTranslation.language_code == lang)
        )
        rows = result.all()

        if not rows:
            return JSONResponse({"statusCode": 204, "message": f"No specialty characteristics found for specialty '{specialty_code}' and language '{lang}'!"}, status_code=204)

        characteristics = []
        for char, translation in rows:
            characteristics.append({
                "id": char.id,
                "specialty_code": char.specialty_code,
                "language_code": translation.language_code,
                "program_desc": translation.program_desc,
                "degree_requirements": translation.degree_requirements
            })

        return JSONResponse({
            "statusCode": 200,
            "message": f"Specialty characteristics fetched successfully for specialty '{specialty_code}' and language '{lang}'!",
            "characteristics": characteristics
        }, status_code=200)

    except Exception as e:
        return JSONResponse({"statusCode": 500, "error": str(e)}, status_code=500)

# GET all SpecialtyCharacteristics by language
async def get_all_specialty_characteristics(db: AsyncSession, lang: str):
    if lang not in allowed_languages:
        return JSONResponse({"statusCode": 404, "message": "Invalid language code!"}, status_code=404)

    try:
        result = await db.execute(
            select(SpecialtyCharacteristics, SpecialtyCharacteristicsTranslation)
            .join(SpecialtyCharacteristicsTranslation)
            .where(SpecialtyCharacteristicsTranslation.language_code == lang)
        )
        rows = result.all()

        if not rows:
            return JSONResponse({"statusCode": 204, "message": f"No specialty characteristics found for language '{lang}'!"}, status_code=204)

        characteristics = []
        for char, translation in rows:
            characteristics.append({
                "id": char.id,
                "specialty_code": char.specialty_code,
                "language_code": translation.language_code,
                "program_desc": translation.program_desc,
                "degree_requirements": translation.degree_requirements
            })

        return JSONResponse({
            "statusCode": 200,
            "message": f"All specialty characteristics fetched successfully for language '{lang}'!",
            "characteristics": characteristics
        }, status_code=200)

    except Exception as e:
        return JSONResponse({"statusCode": 500, "error": str(e)}, status_code=500)


# CREATE SpecialtyCharacteristics
async def create_specialty_characteristics(db: AsyncSession, char_data: SpecialtyCharacteristicsCreate, lang: str):
    if lang not in allowed_languages:
        return JSONResponse({"statusCode": 404, "message": "Invalid language code!"}, status_code=404)

    try:
        spec_q = await db.execute(select(Specialty).where(Specialty.specialty_code == char_data.specialty_code))
        if not spec_q.scalars().first():
            return JSONResponse({"statusCode": 404, "message": "Specialty code does not exist!"}, status_code=404)

        result = await db.execute(select(SpecialtyCharacteristics).where(SpecialtyCharacteristics.specialty_code == char_data.specialty_code))
        base_char = result.scalars().first()

        if base_char is None:
            new_char = SpecialtyCharacteristics(specialty_code=char_data.specialty_code)
            db.add(new_char)
            await db.flush() 

            new_translation = SpecialtyCharacteristicsTranslation(
                specialty_characteristic_id=new_char.id,
                language_code=lang,
                program_desc=char_data.program_desc,
                degree_requirements=char_data.degree_requirements
            )
            db.add(new_translation)
            await db.commit()
            return JSONResponse({"statusCode": 201, "message": f"Specialty characteristics created with translation ({lang})!"}, status_code=201)

        tr_q = await db.execute(
            select(SpecialtyCharacteristicsTranslation)
            .where(SpecialtyCharacteristicsTranslation.specialty_characteristic_id == base_char.id)
            .where(SpecialtyCharacteristicsTranslation.language_code == lang)
        )
        existing_tr = tr_q.scalars().first()
        if existing_tr:
            return JSONResponse({"statusCode": 409, "message": f"Translation already exists for language '{lang}'!"}, status_code=409)

        new_translation = SpecialtyCharacteristicsTranslation(
            specialty_characteristic_id=base_char.id,
            language_code=lang,
            program_desc=char_data.program_desc,
            degree_requirements=char_data.degree_requirements
        )
        db.add(new_translation)
        await db.commit()
        return JSONResponse({"statusCode": 201, "message": f"Translation added for language '{lang}'!"}, status_code=201)

    except Exception as e:
        await db.rollback()
        return JSONResponse({"statusCode": 500, "error": str(e)}, status_code=500)


# UPDATE SpecialtyCharacteristics
async def update_specialty_characteristics(db: AsyncSession, specialty_code: str, char_data: SpecialtyCharacteristicsUpdate, lang: str):
    if lang not in allowed_languages:
        return JSONResponse({"statusCode": 404, "message": "Invalid language code!"}, status_code=404)

    try:
        res = await db.execute(select(SpecialtyCharacteristics).where(SpecialtyCharacteristics.specialty_code == specialty_code))
        char = res.scalars().first()
        if not char:
            return JSONResponse({"statusCode": 404, "message": "Specialty characteristics not found!"}, status_code=404)

        tr_res = await db.execute(
            select(SpecialtyCharacteristicsTranslation)
            .where(SpecialtyCharacteristicsTranslation.specialty_characteristic_id == char.id)
            .where(SpecialtyCharacteristicsTranslation.language_code == lang)
        )
        tr = tr_res.scalars().first()
        if not tr:
            return JSONResponse({"statusCode": 404, "message": f"Translation for language '{lang}' not found!"}, status_code=404)

        tr.program_desc = char_data.program_desc
        tr.degree_requirements = char_data.degree_requirements
        await db.commit()
        return JSONResponse({"statusCode": 200, "message": f"Specialty characteristics updated for language '{lang}'!"}, status_code=200)

    except Exception as e:
        await db.rollback()
        return JSONResponse({"statusCode": 500, "error": str(e)}, status_code=500)


# DELETE SpecialtyCharacteristics
async def delete_specialty_characteristics(db: AsyncSession, specialty_code: str):
    try:
        res = await db.execute(select(SpecialtyCharacteristics).where(SpecialtyCharacteristics.specialty_code == specialty_code))
        char = res.scalars().first()
        if not char:
            return JSONResponse({"statusCode": 404, "message": "Specialty characteristics not found!"}, status_code=404)

        await db.execute(SpecialtyCharacteristicsTranslation.__table__.delete().where(
            SpecialtyCharacteristicsTranslation.specialty_characteristic_id == char.id
        ))

        await db.delete(char)
        await db.commit()
        return JSONResponse({"statusCode": 200, "message": "Specialty characteristics and translations deleted successfully!"}, status_code=200)

    except Exception as e:
        await db.rollback()
        return JSONResponse({"statusCode": 500, "error": str(e)}, status_code=500)
