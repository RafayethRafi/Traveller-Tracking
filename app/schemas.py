from pydantic import BaseModel,EmailStr,Field
from datetime import datetime,date
from typing import Optional,List

class User(BaseModel):
    name : str
    email : str
    phone : str
    address : str
    

    # class Config:
    #     from_attributes = True

class UserCreate(User):
    password : str


class UserOut(User):
    id : int
    role : str
    created_at : datetime
    

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[int] = None


class InvitationBase(BaseModel):
    email : EmailStr
    role : str

# class InvitationCreate(InvitationBase):
#     admin_id : int
    

class ForgotPassword(BaseModel):
    email : EmailStr


class PassReset(BaseModel):
    u_p_email: EmailStr
    password : str
    re_password : str


class TravellerBase(BaseModel):
    arrival_date : None|date = Field(format="iso8601")
    expiry_date : None|date = Field(format="iso8601")
    ticket_time : None|date = Field(format="iso8601")


class Traveller(TravellerBase):
    type : str
    mrz_type : str
    country : str|None
    passport_number : str
    first_name : str
    surname : str
    nationality : str
    date_of_birth : str
    sex : str
    passport_expiration_date : str
    personal_number : str|None
    user_id : int
    created_at : datetime
    muballig_id : str
    status : str|None
    staying_status : str|None
    visa_application_status : str|None
    alpha3_country_code : str|None

    class Config:
        from_attributes = True


class VisaApplicationStatus(BaseModel):
    muballig_id : str
    visa_application_status : str

    


class VisaApplication(BaseModel):
    file_id : int
    user_id : int
    applied_muballigs : List[str]
    status : str
    submission_date : date

    class Config:
        from_attributes = True

class VisaApplicationOut(VisaApplication):
    extented_date : date

    class Config:
        from_attributes = True