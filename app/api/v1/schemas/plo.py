from pydantic import BaseModel
from typing import List, Optional


class PloTranslationCreate(BaseModel):
    language_code: str
    plo_content: str

class PloCreate(BaseModel):
    university_code: str
    specialty_code: str
    plo_code: str
    # translations: List[PloTranslationCreate]
    plo_content: str

class PloUpdate(BaseModel):
    university_code: str
    specialty_code: str
    # translations: List[PloTranslationCreate]
    plo_content: str

class PloTranslationOut(BaseModel):
    language_code: str
    plo_content: str

class PloOut(BaseModel):
    id: int
    university_code: str
    specialty_code: str
    plo_code: str
    translations: List[PloTranslationOut]







