from .database import Base
from sqlalchemy import Column,Integer,String,Boolean,TIMESTAMP,text,ForeignKey,Date,ARRAY
from sqlalchemy .sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP


class User(Base):
    __tablename__ = "users"

    id = Column(Integer,primary_key=True,index=True,nullable=False)
    name = Column(String,nullable=True)
    email = Column(String,nullable=False,unique=True)
    password = Column(String,nullable=False)
    phone = Column(String,nullable=True)
    address = Column(String,nullable=True)
    role = Column(String,nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False,server_default=text('now()'))
    language = Column(String,nullable=True)
    
    

class Invitations(Base):
    __tablename__ = "invitations"

    id = Column(Integer,primary_key=True,nullable=False)
    email = Column(String,nullable=False)
    role = Column(String,nullable=False)
    admin_id = Column(Integer,ForeignKey("users.id",ondelete="CASCADE"),nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False,server_default=text('now()'))
    is_registered = Column(Boolean,nullable=False,default=False)


class Traveller(Base):
    __tablename__ = "travellers"

    id = Column(Integer,primary_key=True,nullable=False)
    type = Column(String,nullable=True)
    mrz_type = Column(String,nullable=True)
    country = Column(String,nullable=True)
    passport_number = Column(String,nullable=False)
    first_name = Column(String,nullable=True)
    surname = Column(String,nullable=True)
    nationality = Column(String,nullable=False)
    date_of_birth = Column(String,nullable=False)
    sex = Column(String,nullable=False)
    passport_expiration_date = Column(String,nullable=False)
    personal_number = Column(String,nullable=True)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False,server_default=text('now()'))
    user_id = Column(Integer,ForeignKey("users.id",ondelete="CASCADE"),nullable=False)
    arrival_date = Column(Date, nullable=False, server_default=text('now()'))
    expiry_date = Column(Date, nullable=False)
    ticket_time = Column(Date, nullable=True)
    muballig_id = Column(String,nullable=False)
    status = Column(String,nullable=True,default="")
    staying_status = Column(String,nullable=True,default="stay")
    visa_application_status = Column(String,nullable=True,default="")
    alpha3_country_code = Column(String,nullable=True,default="")



class VisaApplication(Base):
    __tablename__ = "visa_applications"

    file_id = Column(Integer,primary_key=True,nullable=False)
    applied_muballigs = Column(ARRAY(String),nullable=False)
    status = Column(String,nullable=False,default="applied")
    submission_date = Column(Date, nullable=False,default=text('now()'))
    extented_date = Column(Date, nullable=True)
    user_id = Column(Integer,ForeignKey("users.id",ondelete="CASCADE"),nullable=False)




