from .. import models, schemas , utils,oauth2,send_email
from fastapi import Response,status,HTTPException,Depends,APIRouter,Body
from sqlalchemy.orm import Session
from ..database import get_db
from typing import Annotated,Optional
from .. import country_coordinates
from datetime import date



router = APIRouter(
    prefix= "/users",
    tags=['Users']
)

# @router.post("/register_user/{role}",status_code=status.HTTP_201_CREATED,response_model=schemas.UserOut)
# def register_user(user:schemas.UserCreate,role:str, db: Session = Depends(get_db)):

#     #if organization already exists by email
#     if db.query(models.User).filter(models.User.email == user.email).first():
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="User already exists")
    


#     hashed_password = utils.hash(user.password)
#     user.password = hashed_password

#     new_user = models.User(role=role,**user.model_dump())
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)


#     return new_user



@router.post("/register_user/{info}", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def register_user(info:str, user: schemas.UserCreate, db: Session = Depends(get_db)):

    email,role = info.split("__emailrole__")


    # if db.query(models.User).filter(models.User.email == email).first():
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="User already exists")
    
    # #if email not in invitations table
    # if not db.query(models.Invitations).filter(models.Invitations.email == email).first():
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="User not invited or wrong email")
    
    
    hashed_password = utils.hash(user.password)
    user.password = hashed_password

    if email == user.email:
        new_user = models.User(role=role,**user.model_dump())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # # set the is_registered to True
        # invitation = db.query(models.Invitations).filter(models.Invitations.email == email).first()
        # invitation.is_registered = True
        # db.commit()
        # db.refresh(invitation)
        
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Email does not match")


    return new_user



#forgot password and recovery
@router.post("/forgot_password/", status_code=status.HTTP_200_OK)
def forgot_password(data:schemas.ForgotPassword,db: Session = Depends(get_db)) -> Response:

    user = db.query(models.User).filter(models.User.email == data.email).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"{data.email} not registered")

    send_email.send_pass_recovery_email(user.id,data.email)

    return f"Recovery email sent to {data.email} of id : {user.id}"



#create an endpoint to get the coordinates of the countries in the travellers table and number of travellers in each country
@router.post("/get_countries/", status_code=status.HTTP_200_OK)
def get_countries(
    lower_date:  Optional[date] = None,
    upper_date: Optional[date] = None,
    db: Session = Depends(get_db),
    staying_status: Optional[str] = "all",
    current_user: int = Depends(oauth2.get_current_user)
) -> Response:

    if current_user.role != "data_manager" and current_user.role != "security1" and current_user.role != "security2" and current_user.role!="data_operator":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Data managers,operators and security officers can view the list of countries")
    
    if staying_status == "all":
        if lower_date and upper_date:
            countries = db.query(models.Traveller.alpha3_country_code).filter(models.Traveller.arrival_date>=lower_date,models.Traveller.arrival_date<=upper_date).all()
        elif lower_date:
            countries = db.query(models.Traveller.alpha3_country_code).filter(models.Traveller.arrival_date>=lower_date).all()
        elif upper_date:
            countries = db.query(models.Traveller.alpha3_country_code).filter(models.Traveller.arrival_date<=upper_date).all()
        else:
            countries = db.query(models.Traveller.alpha3_country_code).all()
    else:
        if lower_date and upper_date:
            countries = db.query(models.Traveller.alpha3_country_code).filter(models.Traveller.arrival_date>=lower_date,models.Traveller.arrival_date<=upper_date,models.Traveller.staying_status==staying_status).all()
        elif lower_date:
            countries = db.query(models.Traveller.alpha3_country_code).filter(models.Traveller.arrival_date>=lower_date,models.Traveller.staying_status==staying_status).all()
        elif upper_date:
            countries = db.query(models.Traveller.alpha3_country_code).filter(models.Traveller.arrival_date<=upper_date,models.Traveller.staying_status==staying_status).all()
        else:
            countries = db.query(models.Traveller.alpha3_country_code).filter(models.Traveller.staying_status==staying_status).all()

    

    #get the unique countries and count the frequency of each country
    countries = [country[0] for country in countries]

    #get the unique countries and count the frequency of each country
    countries = {country:countries.count(country) for country in countries}


    # create a list of dictionaries with country as key and values from country_coordinates.py
    countries = [{"country_code":country,"country_name":country_coordinates.cc[country]["Country"],"latitude":country_coordinates.cc[country]["Latitude"],"longitude":country_coordinates.cc[country]["Longitude"],"count":countries[country]} for country in countries]
    return countries



# create an endpoint to get the loged in userinfo.
@router.get("/get_userinfo/",status_code=status.HTTP_200_OK)
def get_userinfo(db: Session = Depends(get_db),current_user:int=Depends(oauth2.get_current_user)) -> Response:
        
    return current_user

#create an endpoint to get the coordinates of the countries in the travellers table and number of travellers in each country which traveller's staying status is stay.
# @router.get("/get_countries_stay/",status_code=status.HTTP_200_OK)
# def get_countries_stay(db: Session = Depends(get_db),current_user:int=Depends(oauth2.get_current_user)) -> Response:
    
#         # if current_user.role != "data_operator":
#         #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only Data Operators can view the list of countries")
    
#         countries = db.query(models.Traveller.country).filter(models.Traveller.staying_status == "stay").all()
    
#         #get the unique countries and count the frequency of each country
#         countries = [country[0] for country in countries]
    
#         #get the unique countries and count the frequency of each country
#         countries = {country:countries.count(country) for country in countries}
    
#         countries = db.query(models.Traveller.country).filter(models.Traveller.staying_status == "stay").all()
    
#         #get the unique countries and count the frequency of each country
#         countries = [country[0] for country in countries]
    
#         #get the unique countries and count the frequency of each country
#         countries = {country:countries.count(country) for country in countries}
    
#         # create a list of dictionaries with country as key and values from country_coordinates.py
#         countries = [{"country_code":country,"country_name":country_coordinates.cc[country]["Country"],"latitude":country_coordinates.cc[country]["Latitude"],"longitude":country_coordinates.cc[country]["Longitude"],"count":countries[country]} for country in countries]
#         return countries



#create an endpoint to get the coordinates of the countries in the travellers table and number of travellers in each country which traveller's staying status is return.
# @router.get("/get_countries_return/",status_code=status.HTTP_200_OK)
# def get_countries_return(db: Session = Depends(get_db),current_user:int=Depends(oauth2.get_current_user)) -> Response:
        
#     # if current_user.role != "data_operator":
#     #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only Data Operators can view the list of countries")
        
#     countries = db.query(models.Traveller.country).filter(models.Traveller.staying_status == "return").all()
        
#     #get the unique countries and count the frequency of each country
#     countries = [country[0] for country in countries]
        
#     #get the unique countries and count the frequency of each country
#     countries = {country:countries.count(country) for country in countries}
        
#     countries = db.query(models.Traveller.country).filter(models.Traveller.staying_status == "return").all()
        
#     #get the unique countries and count the frequency of each country
#     countries = [country[0] for country in countries]
        
#     #get the unique countries and count the frequency of each country
#     countries = {country:countries.count(country) for country in countries}
        
#     # create a list of dictionaries with country as key and values from country_coordinates.py
#     countries = [{"country_code":country,"country_name":country_coordinates.cc[country]["Country"],"latitude":country_coordinates.cc[country]["Latitude"],"longitude":country_coordinates.cc[country]["Longitude"],"count":countries[country]} for country in countries]
#     return countries 