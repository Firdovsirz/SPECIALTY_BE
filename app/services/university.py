from datetime import datetime
from app.db.session import get_db
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from app.models.university import University
from fastapi import Depends, HTTPException, status
from app.api.v1.schemas.university import CreateUniversity

def get_university(
    university_code: str,
    db: Session = Depends(get_db)
):
    try:
        university = db.query(University).filter(
            University.university_code == university_code
        ).first()

        if not university:
            # raise HTTPException(
            #     status_code=status.HTTP_404_NOT_FOUND,
            #     detail="University not found."
            # )

            return JSONResponse(content={
                "statusCode": 404,
                "message": "Not found"
            })
        
        return JSONResponse(
            content={
                "statusCode": 200,
                "message": "University fetched successfully.",
                "university": {
                    "id": university.id,
                    "university_code": university.university_code,
                    "university_name": university.university_name,
                    "university_short_name": university.university_short_name,
                    "is_frozen": university.is_frozen,
                    "created_at": university.created_at,
                    "updated_at": university.updated_at,
                    "deleted_at": university.deleted_at  
                }
            }
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "error": str(e)
            }, status_code=500
        )

def add_university(
    university_details: CreateUniversity,
    db: Session = Depends(get_db) 
):
    try:
        exist_university = db.query(University).filter(
            University.university_name == university_details.university_name
        ).first()

        if not exist_university:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="University not found."
            )

        new_university = University(
            university_name = university_details.university_name,
            university_short_name = university_details.university_short_name,
            is_frozen = False,
            create_at = datetime.utcnow()
        )

        db.add(new_university)
        db.commit()
        db.refresh(new_university)

        return JSONResponse(
            content={
                "statusCode": 201,
                "message": "University createed successfully."
            }, status_code=201
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "statusCode": 500,
                "error": str(e)
            }, status_code=500
        )
    
def delete_university(
    university_code: str,
    db: Session = Depends(get_db)
):
    university = db.query(University).filter(
        University.university_code == university_code
    ).first()

    if not university:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="University not found."
        )

    try:
        db.delete(university)
        db.commit()

        return JSONResponse(
            content={
                "statusCode": 200,
                "message": "University deleted successfully."
            }, status_code=status.HTTP_200_OK
        )
    
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the university."
        )