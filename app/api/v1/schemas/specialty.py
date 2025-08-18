from pydantic import BaseModel

class SpecialtyBase(BaseModel):
    university_code: str
    cafedra_code: str
    specialty_code: str
    specialty_name: str

class CreateSpecialty(SpecialtyBase):
    pass