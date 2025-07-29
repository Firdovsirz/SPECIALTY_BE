from app.db.session import get_db
from sqlalchemy.orm import Session
from app.services.university import *
from fastapi import APIRouter, Depends, Query
from app.api.v1.schemas.university import CreateUniversity

router = APIRouter()

@router.get("/university")
def get_university_endpoint(
    university_code: str = Query(...),
    db: Session = Depends(get_db)
):
    return get_university(university_code, db)

@router.post("/university")
def create_university_endpoint(
    university_details: CreateUniversity,
    db: Session = Depends(get_db)
):
    return add_university(university_details, db)

@router.delete("/university")
def delete_university_endpoint(
    university_code: str = Query(...),
    db: Session = Depends(get_db)
):
    return delete_university(university_code, db)
