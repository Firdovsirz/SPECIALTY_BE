from pydantic import BaseModel

class AuthBase(BaseModel):
    name: str
    surname: str
    father_name: str
    role: str
    university_code: str
    fin_kod: str
    user_type: str
    project_role: str

class SignUp(AuthBase):
    password: str
    pass

class SignIn(BaseModel):
    fin_kod: str
    password: str

class ValidateOTP(BaseModel):
    fin_kod: str
    otp: int