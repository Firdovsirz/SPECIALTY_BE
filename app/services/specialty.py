from datetime import datetime
from app.db.session import get_db
from fastapi import Depends, status
from sqlalchemy.future import select
from fastapi.responses import JSONResponse
from app.utils.language import get_language
from app.models.speciality import Specialty
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.translator import translate_to_english
from app.api.v1.schemas.specialty import CreateSpecialty
from app.models.specialty_translations import SpecialtyTranslations

async def get_specialties(
    lang_code: str = Depends(get_language),
    db: AsyncSession = Depends(get_db)
):
    try:
        fetch_data = await db.execute(
            select(SpecialtyTranslations)
            .where(SpecialtyTranslations.language_code == lang_code)
        )

        specialties = fetch_data.scalars().all()

        if not fetch_data:
            return JSONResponse(
                content={
                    "statusCode": 204,
                    "message": "No specialty found."
                }, status_code=status.HTTP_204_NO_CONTENT
            )
        
        return JSONResponse(
            content={
                "statusCode": 200,
                "message": "Specialties fetched successfully.",
                "specialties": [
                    {
                        "university_code": specialty.university_code,
                        "cafedra_code": specialty.cafedra_code,
                        "specialty_code": specialty.specialty_code,
                        "specialty_name": specialty.specialty_name,
                        "created_at": specialty.created_at
                    } for specialty in specialties
                ]
            }
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "statusCode": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

async def add_specialty(
    specialty_details: CreateSpecialty,
    db: AsyncSession = Depends(get_db)
):
    try:
        exists_specialty_code = await db.execute(
            select(Specialty)
            .where(Specialty.specialty_code == specialty_details.specialty_code)
        )

        exists_specialty_name = await db.execute(
            select(SpecialtyTranslations)
            .where(SpecialtyTranslations.specialty_name == specialty_details.specialty_name)
        )

        if exists_specialty_code.scalar_one_or_none() or exists_specialty_name.scalar_one_or_none():
            return JSONResponse(
                content={
                    "statusCode": 409,
                    "message": "Specialty already exists."
                }, status_code=status.HTTP_409_CONFLICT
            )
        
        new_specialty = Specialty(
            cafedra_code=specialty_details.cafedra_code,
            specialty_code=specialty_details.specialty_code,
            created_at=datetime.utcnow(),
            updated_at=None
        )

        new_specialty_translations_az = SpecialtyTranslations(
            specialty_code = specialty_details.specialty_code,
            language_code = 'az',
            specialty_name = specialty_details.specialty_name,
            created_at = datetime.utcnow()
        )

        new_specialty_translations_en = SpecialtyTranslations(
            specialty_code = specialty_details.specialty_code,
            language_code = 'en',
            specialty_name = translate_to_english(specialty_details.specialty_name),
            created_at = datetime.utcnow()
        )

        db.add(new_specialty)
        db.add(new_specialty_translations_az)
        db.add(new_specialty_translations_en)
        await db.commit()
        await db.refresh(new_specialty)
        await db.refresh(new_specialty_translations_az)
        await db.refresh(new_specialty_translations_en)

        return JSONResponse(
            content={
                "statusCode": 201,
                "message": "Specialty created successfully."
            }, status_code=status.HTTP_201_CREATED
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "statusCode": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )