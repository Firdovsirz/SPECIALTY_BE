from pydantic import BaseModel

class CompetencyTranslationCreate(BaseModel):
    language_code: str
    competency_content: str

class CompetencyCreate(BaseModel):
    university_code: str
    specialty_code: str
    competency_code: str
    competency_content: str

class CompetencyUpdate(BaseModel):
    university_code: str
    specialty_code: str
    competency_content: str

class CompetencyTranslationOut(BaseModel):
    language_code: str
    competency_content: str
