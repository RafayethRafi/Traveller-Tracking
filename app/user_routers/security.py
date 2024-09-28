#make an endpoint to get the list of travellers who are staying
from fastapi import  File, UploadFile, HTTPException,Body,Response,Depends,APIRouter,status
from passporteye import read_mrz
from .. import models, schemas , oauth2,send_email
from fastapi import Response,Depends,APIRouter
from sqlalchemy.orm import Session
from ..database import get_db
from typing import List
from typing import Annotated,Optional
from datetime import date
from .. import country_coordinates


router = APIRouter(
    prefix= "/security",
    tags=['Security']
)



@router.get("/get_all_travellers/",response_model=List[schemas.Traveller]|dict)
def get_all_travellers( lower_date: Optional[date] = None,
                        upper_date: Optional[date] = None,
                        db: Session = Depends(get_db),current_user:int=Depends(oauth2.get_current_user)) -> Response:

    if current_user.role != "data_manager" and current_user.role != "security2" and current_user.role != "data_operator":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only Data Operators can view the list of all travellers")

    if upper_date and lower_date:
        travellers = db.query(models.Traveller).filter(models.Traveller.arrival_date>=lower_date,models.Traveller.arrival_date<=upper_date).all()
    elif upper_date:
        travellers = db.query(models.Traveller).filter(models.Traveller.arrival_date<=upper_date).all()
    elif lower_date:
        travellers = db.query(models.Traveller).filter(models.Traveller.arrival_date>=lower_date).all()
    else:
        travellers = db.query(models.Traveller).all()

    if travellers == []:
        return {"detail":"No travellers have arrived"}

    # Convert models.Traveller objects into schemas.Traveller objects
    travellers = [schemas.Traveller.model_validate(traveller) for traveller in travellers]

    return {"travellers_info":travellers}


@router.get("/get_staying_travellers/",response_model=List[schemas.Traveller]|dict)
def get_staying_travellers( lower_date: Optional[date] = None,
                            upper_date: Optional[date] = None,
                               db: Session = Depends(get_db),current_user:int=Depends(oauth2.get_current_user)) -> Response:

    if current_user.role != "data_manager" and current_user.role != "security2":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only Data Operators can view the list of travellers who are staying")
    

    if upper_date and lower_date:
        travellers = db.query(models.Traveller).filter(models.Traveller.staying_status == "stay",models.Traveller.arrival_date>=lower_date,models.Traveller.arrival_date<=upper_date).all()
    elif upper_date:
        travellers = db.query(models.Traveller).filter(models.Traveller.staying_status == "stay",models.Traveller.arrival_date<=upper_date).all()
    elif lower_date:
        travellers = db.query(models.Traveller).filter(models.Traveller.staying_status == "stay",models.Traveller.arrival_date>=lower_date).all()
    else:
        travellers = db.query(models.Traveller).filter(models.Traveller.staying_status == "stay").all()

    if travellers == []:
        return {"detail":"No travellers are staying"}
    
    # travellers = {"travellers_info_with_status_stay":travellers}
    # Convert models.Traveller objects into schemas.Traveller objects
    travellers = [schemas.Traveller.model_validate(traveller) for traveller in travellers]

    return {"travellers_info_with_status_stay":travellers}

#make an endpoint to get the list of travellers who are return
@router.get("/get_returned_travellers/",response_model=List[schemas.Traveller]|dict)
def get_returned_travellers( lower_date: Optional[date] = None,
                            upper_date: Optional[date] = None,
                            db: Session = Depends(get_db),current_user:int=Depends(oauth2.get_current_user)) -> Response:

    if current_user.role != "data_manager" and current_user.role != "security2":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only Data Operators can view the list of travellers who are staying")

    if upper_date and lower_date:
        travellers = db.query(models.Traveller).filter(models.Traveller.staying_status == "return",models.Traveller.arrival_date>=lower_date,models.Traveller.arrival_date<=upper_date).all()
    elif upper_date:
        travellers = db.query(models.Traveller).filter(models.Traveller.staying_status == "return",models.Traveller.arrival_date<=upper_date).all()
    elif lower_date:
        travellers = db.query(models.Traveller).filter(models.Traveller.staying_status == "return",models.Traveller.arrival_date>=lower_date).all()
    else:
        travellers = db.query(models.Traveller).filter(models.Traveller.staying_status == "return").all()

    if travellers == []:
        return {"detail":"No travellers are returning"}

    # Convert models.Traveller objects into schemas.Traveller objects
    travellers = [schemas.Traveller.model_validate(traveller) for traveller in travellers]

    return {"travellers_info_with_status_return":travellers}



#make an endpoint to get the list of travellers who's visa application status is applied
@router.get("/get_visa_application_status_applied/",status_code=status.HTTP_200_OK)
def get_visa_application_status_applied( lower_date: Optional[date] = None,
                                         upper_date: Optional[date] = None,
                            db: Session = Depends(get_db),current_user:int=Depends(oauth2.get_current_user)) -> Response:

    if current_user.role != "data_manager" and current_user.role != "security2":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only Data Operators can view the list of travellers who's visa application status is applied")
    
    if upper_date and lower_date:
        files = db.query(models.VisaApplication).filter(models.VisaApplication.submission_date>=lower_date,models.VisaApplication.submission_date<=upper_date,models.VisaApplication.extented_date==None).all()
    elif upper_date:
        files = db.query(models.VisaApplication).filter(models.VisaApplication.submission_date<=upper_date,models.VisaApplication.extented_date==None).all()
    elif lower_date:
        files = db.query(models.VisaApplication).filter(models.VisaApplication.submission_date>=lower_date,models.VisaApplication.extented_date==None).all()
    else:
        files = db.query(models.VisaApplication).filter(models.VisaApplication.extented_date==None).all()

    if files == []:
        return {"detail":"No travellers have applied for visa"}
    
    return {"files":files}

#make an endpoint to get the list of travellers who's visa application status is extended
@router.get("/get_visa_application_status_extended/",status_code=status.HTTP_200_OK)
def get_visa_application_status_extended(lower_date: Optional[date] = None,
                                         upper_date: Optional[date] = None,
                                         db: Session = Depends(get_db),current_user:int=Depends(oauth2.get_current_user)) -> Response:

    if current_user.role != "data_manager" and current_user.role != "security2":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only Data Operators can view the list of travellers who's visa application status is extended")

    if upper_date and lower_date:
        files = db.query(models.VisaApplication).filter(models.VisaApplication.extented_date>=lower_date,models.VisaApplication.extented_date<=upper_date).all()
    elif upper_date:
        files = db.query(models.VisaApplication).filter(models.VisaApplication.extented_date<=upper_date).all()
    elif lower_date:
        files = db.query(models.VisaApplication).filter(models.VisaApplication.extented_date>=lower_date).all()
    else:
        files = db.query(models.VisaApplication).all()

    if files == []:
        return {"detail":"No travellers have extended their visa"}
    
    return {"files":files}