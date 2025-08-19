from pydantic import BaseModel
from typing import List, Optional

class PloTranslationBase(BaseModel):
    language_code: str
    plo_content: str

class PloBase(BaseModel):
    university_code: str
    specialty_code: str
    plo_code: str

class CreatePlo(PloBase):
    translations: List[PloTranslationBase]

class PloResponse(PloBase):
    translations: List[PloTranslationBase]

    class Config:
        orm_mode = True











