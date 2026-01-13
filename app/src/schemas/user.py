from pydantic import BaseModel, EmailStr

class UserRegister(BaseModel):
    fullname: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserProfile(BaseModel):
    id: int
    fullname: str
    email: EmailStr
    role: str
    
    
class ChangePassword(BaseModel):
    email: EmailStr
    old_password: str
    new_password: str


class ForgetPassword(BaseModel):
    email: EmailStr


class VerifyOTP(BaseModel):
    email: EmailStr
    otp: int
    new_password: str
