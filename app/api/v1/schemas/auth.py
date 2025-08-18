from pydantic import BaseModel

class AuthBase(BaseModel):
    fin_kod: str
    user_type: str
    project_role: str

class SignUp(AuthBase):
    password: str
    pass

class SignIn(BaseModel):
    fin_kod: str
    password: str