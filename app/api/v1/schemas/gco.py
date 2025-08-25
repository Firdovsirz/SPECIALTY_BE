from pydantic import BaseModel
from typing import List, Optional

class GCOTranslationCreate(BaseModel):
    language_code: str
    career_content: str

class GCOCreate(BaseModel):
    university_code: str
    specialty_code: str
    career_code: str
    career_content: str

class GCOUpdate(BaseModel):
    university_code: str
    specialty_code: str
    career_content: str

class GCOTranslationOut(BaseModel):
    language_code: str
    career_content: str

class GCOOut(BaseModel):
    id: int
    university_code: str
    specialty_code: str
    career_code: str
    translations: List[GCOTranslationOut]