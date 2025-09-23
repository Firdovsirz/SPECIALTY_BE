from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class LiteratureTransBase(BaseModel):
    language_code: str
    literature_name: str

class LiteratureTransCreate(LiteratureTransBase):
    pass

class LiteratureTransUpdate(BaseModel):
    language_code: Optional[str] = None
    literature_name: Optional[str] = None

class LiteratureTrans(LiteratureTransBase):
    id: int
    literature_code: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class LiteratureBase(BaseModel):
    literature_code: int
    specialty_code: int
    url: str

class LiteratureCreate(LiteratureBase):
    translations: List[LiteratureTransCreate] = []

class LiteratureUpdate(BaseModel):
    literature_code: Optional[int] = None
    specialty_code: Optional[int] = None
    url: Optional[str] = None
    translations: Optional[List[LiteratureTransCreate]] = None

class Literature(LiteratureBase):
    id: int
    created_at: datetime
    updated_at: datetime
    translations: List[LiteratureTrans] = []

    class Config:
        from_attributes = True