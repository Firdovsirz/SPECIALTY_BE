from pydantic import BaseModel
from typing import List

class SloTranslationCreate(BaseModel):
    language_code: str
    slo_content: str

class SloCreate(BaseModel):
    university_code: str
    specialty_code: str
    slo_code: str
    # translations: List[SloTranslationCreate]
    slo_content: str

class SloUpdate(BaseModel):
    university_code: str
    specialty_code: str
    # translations: List[SloTranslationCreate]
    slo_content: str

class SloTranslationOut(BaseModel):
    language_code: str
    slo_content: str

class SloOut(BaseModel):
    id: int
    university_code: str
    specialty_code: str
    slo_code: str
    translations: List[SloTranslationOut]