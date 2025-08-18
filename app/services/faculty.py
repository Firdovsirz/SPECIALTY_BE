from app.db.session import get_db
from fastapi import Depends, status
from sqlalchemy.future import select
from app.models.faculty import Faculty
from fastapi.responses import JSONResponse
from app.models.university import University
from sqlalchemy.ext.asyncio import AsyncSession

# get all faculties

async def get_faculties(
    db: AsyncSession = Depends(get_db) 
):
    try:
        fetched_data = await db.execute(select(Faculty))
        faculties = fetched_data.scalars().all()

        if not faculties:
            return JSONResponse(
                content={
                    "statusCode": 200,
                    "message": "No faculty found.",
                    "faculties": []
                }, status_code=status.HTTP_204_NO_CONTENT
            )
        
        return JSONResponse(
            content={
                "statusCode": 200,
                "message": "Faculties fetched successfully.",
                "faculties" : [
                    {
                        "university_code": faculty.university_code,
                        "faculty_code": faculty.faculty_code,
                        "faculty_name": faculty.faculty_name,
                        "created_at": str(faculty.created_at) if faculty.created_at else None,
                        "updated_at": str(faculty.updated_at) if faculty.updated_at else None
                    } for faculty in faculties
                ]
            }, status_code=status.HTTP_200_OK
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "statusCode": 500,
                "error": str(e)
            }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
# get all faculties by university code
    
async def get_uni_faculties(
    uni_code: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        fetched_data = await db.execute(
            select(Faculty)
            .where(Faculty.university_code==uni_code)
        )

        faculties = fetched_data.scalars().all()

        universities = await db.execute(
            select(University)
            .where(University.university_code==uni_code)
        )

        university = universities.scalars().all()

        if not university:
            return JSONResponse(
                content={
                    "status": 404,
                    "message": "University not found",
                }, status_code=status.HTTP_404_NOT_FOUND
            )

        if not faculties:
            return JSONResponse(
                content={
                    "status": 204,
                    "message": "No faculties found",
                    "faculties": []
                }, status_code=status.HTTP_204_NO_CONTENT
            )
        
        return JSONResponse(
            content={
                "status": 200,
                "message": "Faculties fethed successfully.",
                "faculties": [
                    {
                        "faculty_code": faculty.faculty_code,
                        "faculty_name": faculty.faculty_name
                    } for faculty in faculties
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