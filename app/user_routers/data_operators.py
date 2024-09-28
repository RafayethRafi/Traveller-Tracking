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
from fastapi import Form


router = APIRouter(
    prefix= "/data_operators",
    tags=['Data_Operators']
)


@router.post("/get_traveller_data/")
async def get_traveller_data(arrival_date: Optional[date] = Form(None),
                             expiry_date: Optional[date] = Form(None),
                             ticket_time: Optional[date] = Form(None),
                             file: UploadFile = File(...),
                             db: Session = Depends(get_db),
                             current_user: int = Depends(oauth2.get_current_user)) -> Response:
    
    # Check if ticket_time is None, and determine the status
    if not ticket_time:
        status = "uncertain"
    elif expiry_date and expiry_date > ticket_time:
        status = "safe"
    else:
        status = "danger"

    try:
        # Read the uploaded image file
        image_bytes = await file.read()

        # Read MRZ from the image
        mrz = read_mrz(image_bytes)

        # Check if MRZ was successfully extracted
        if mrz is None:
            raise HTTPException(status_code=400, detail="Could not extract MRZ from the provided image.")

        # Convert the MRZ data to a dictionary
        mrz_data = mrz.to_dict()

        passport_info = {
            "type": mrz.type,
            "mrz_type": mrz.mrz_type,
            "alpha3_country_code": mrz.country,
            "passport_number": mrz.number,
            "first_name": mrz.names,
            "surname": mrz.surname,
            "nationality": mrz.nationality,
            "date_of_birth": mrz.date_of_birth,
            "sex": mrz.sex,
            "passport_expiration_date": mrz.expiration_date,
            "personal_number": mrz.personal_number if hasattr(mrz, 'personal_number') else "na"
        }

        # Remove all characters after the first occurrence of a space in first_name
        passport_info["first_name"] = passport_info["first_name"].split(" ")[0]

        # Remove all "<" characters from the fields
        for key in passport_info.keys():
            passport_info[key] = passport_info[key].replace("<", "")

        # Check if the traveller data is already in the database
        if db.query(models.Traveller).filter(models.Traveller.passport_number == passport_info["passport_number"]).first():
            return {"detail": "Data already collected"}

    except HTTPException as e:
        # Re-raise HTTPException with status code and details
        raise e
    except Exception as e:
        # Return an error if any other exception occurs
        raise HTTPException(detail=str(e), status_code=500)

    # Validate that current_user.language is not None
    language = current_user.language
    if not language:
        raise HTTPException(status_code=400, detail="User does not have a valid language set.")

    # Generate a muballig_id based on language and previous traveller IDs
    scanned_travellers = db.query(models.Traveller).filter(models.Traveller.muballig_id.like(f"{language[0]}%")).all()
    scanned_travellers = [int(traveller.muballig_id[1:]) for traveller in scanned_travellers]
    max_number = max(scanned_travellers) if scanned_travellers else 0
    muballig_id = language[0] + str(max_number + 1)

    # Add the traveller details to the database
    new_traveller = models.Traveller(user_id=current_user.id,
                                     arrival_date=arrival_date,
                                     expiry_date=expiry_date,
                                     ticket_time=ticket_time,
                                     muballig_id=muballig_id,
                                     staying_status="stay",
                                     country=country_coordinates.cc[passport_info["alpha3_country_code"]]["Country"],
                                     status=status,
                                     **passport_info)

    db.add(new_traveller)
    db.commit()
    db.refresh(new_traveller)

    return new_traveller





#make an endpoint to change the status of a list of travellers
@router.post("/change_status_to_return/",status_code=status.HTTP_200_OK)
def change_status_to_return(travellers:List[str],db: Session = Depends(get_db),current_user:int=Depends(oauth2.get_current_user)) -> Response:

    if current_user.role != "data_operator" and current_user.role != "data_manager":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only Data Operators can change the status of travellers")
    
    non_existent_travellers = []
    existent_travellers = []
    for traveller in travellers:
        found_traveller = db.query(models.Traveller).filter(models.Traveller.muballig_id == traveller).first()

        if not found_traveller:
            non_existent_travellers.append(traveller)
            continue
        existent_travellers.append(traveller)
        found_traveller.staying_status = "return"
        db.commit()
        db.refresh(found_traveller)

    return {"Status_Changed": existent_travellers,"non_existent_travellers":non_existent_travellers}

#make an endpoint to change the status of a list of travellers to stay
@router.post("/change_status_to_stay/",status_code=status.HTTP_200_OK)
def change_status_to_stay(travellers:List[str],db: Session = Depends(get_db),current_user:int=Depends(oauth2.get_current_user)) -> Response:

    if current_user.role != "data_operator" and current_user.role != "data_manager":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only Data Operators can change the status of travellers")
    
    non_existent_travellers = []
    existent_travellers = []
    for traveller in travellers:
        found_traveller = db.query(models.Traveller).filter(models.Traveller.muballig_id == traveller).first()

        if not found_traveller:
            non_existent_travellers.append(traveller)
            continue
        existent_travellers.append(traveller)
        found_traveller.staying_status = "stay"
        db.commit()
        db.refresh(found_traveller)

    return {"Status_Changed": existent_travellers,"non_existent_travellers":non_existent_travellers}

#make an endpoint to change the visa_application_status of a list of travellers
@router.post("/visa_application/",response_model=schemas.VisaApplication)
def change_visa_application_status_to_applied(applied_muballigs:List[str],db: Session = Depends(get_db),current_user:int=Depends(oauth2.get_current_user)) -> Response:

    if current_user.role != "data_operator" and current_user.role != "data_manager":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only Data Operators can change the visa_application_status of travellers")

    for traveller in applied_muballigs:
        found_traveller = db.query(models.Traveller).filter(models.Traveller.muballig_id == traveller).first()

        if not found_traveller:
            continue
        found_traveller.visa_application_status = "applied"
        db.commit()
        db.refresh(found_traveller)

    
    travellers = models.VisaApplication(user_id=current_user.id,applied_muballigs=applied_muballigs)
    db.add(travellers)
    db.commit()
    db.refresh(travellers)

    travellers = schemas.VisaApplication.model_validate(travellers)

    return travellers

#make an endpoint to extend the visa
@router.post("/extend_visa/",status_code=status.HTTP_200_OK)
def extend_visa(file_ids:List[int],db: Session = Depends(get_db),current_user:int=Depends(oauth2.get_current_user)) -> Response:

    if current_user.role != "data_operator" and current_user.role != "data_manager":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only Data Operators can extend the visa")

    visa_extended = {
        "already_extended": [],
        "extended_now": []
    }
    for id in file_ids:
        found_file = db.query(models.VisaApplication).filter(models.VisaApplication.file_id == id).first()
        applied_muballigs = found_file.applied_muballigs

        for traveller in applied_muballigs:
            found_traveller = db.query(models.Traveller).filter(models.Traveller.muballig_id == traveller).first()

            if not found_traveller:
                continue
            if found_traveller.visa_application_status == "extended":
                visa_extended["already_extended"].append(traveller)
                continue
            visa_extended["extended_now"].append(traveller)
            found_traveller.visa_application_status = "extended"
            db.commit()
            db.refresh(found_traveller)
        
        found_file.extented_date = date.today()
        db.commit()
        db.refresh(found_file)

    return visa_extended

        

        


            
        






#make an endpoint to search the travellers by their muballig_id or passport_number or their name
@router.post("/search_travellers/",response_model=List[schemas.Traveller]|dict)
def search_travellers(search:Optional[str] = Form(None),
                      country:Optional[str] = Form(None),
                      status:Optional[str] = Form(None),
                      lower_date: Optional[date] = Form(None),
                        upper_date: Optional[date] = Form(None),
                        db: Session = Depends(get_db),current_user:int=Depends(oauth2.get_current_user)) -> Response:

    if current_user.role != "data_operator" and current_user.role != "data_manager":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only Data Operators can search the travellers")
    
    
    if search == None:
        travellers = db.query(models.Traveller).all()
    else:
        travellers = db.query(models.Traveller).filter(models.Traveller.muballig_id.ilike(f"%{search}%") | models.Traveller.passport_number.ilike(f"%{search}%") | models.Traveller.first_name.ilike(f"%{search}%") | models.Traveller.surname.ilike(f"%{search}%")).all()

    if country != None:
        travellers = [traveller for traveller in travellers if traveller.country == country]

    if status != None:
        travellers = [traveller for traveller in travellers if traveller.staying_status == status]

    # if country != None:
    #     travellers = db.query(models.Traveller).filter(models.Traveller.muballig_id.ilike(f"%{search}%") | models.Traveller.passport_number.ilike(f"%{search}%") | models.Traveller.first_name.ilike(f"%{search}%") | models.Traveller.surname.ilike(f"%{search}%")| models.Traveller.first_name.ilike(f"%{search}%")).filter(models.Traveller.country == country).all()
    # else:
    #     travellers = db.query(models.Traveller).filter(models.Traveller.muballig_id.ilike(f"%{search}%") | models.Traveller.passport_number.ilike(f"%{search}%") | models.Traveller.first_name.ilike(f"%{search}%") | models.Traveller.surname.ilike(f"%{search}%")| models.Traveller.first_name.ilike(f"%{search}%")).all()

    if upper_date and lower_date:
        #filter the travellers by their arrival date
        travellers = [traveller for traveller in travellers if traveller.arrival_date>=lower_date and traveller.arrival_date<=upper_date]
    elif upper_date:
        travellers = [traveller for traveller in travellers if traveller.arrival_date<=upper_date]
    elif lower_date:
        travellers = [traveller for traveller in travellers if traveller.arrival_date>=lower_date]


    if travellers == []:
        return {"detail":"No travellers found"}
    
    # Convert models.Traveller objects into schemas.Traveller objects
    travellers = [schemas.Traveller.model_validate(traveller) for traveller in travellers]

    return {"travellers_info":travellers}


#make an endpoint to get the travellers by their muballig_id
@router.post("/get_travellers_by_muballig_id/",response_model=List[schemas.Traveller])
def get_travellers_by_muballig_id(muballig_ids:List[str],db: Session = Depends(get_db),current_user:int=Depends(oauth2.get_current_user)) -> Response:

    if current_user.role != "data_operator" and current_user.role != "data_manager":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only Data Operators can get the travellers by their muballig_id")
    
    travellers = []
    for muballig_id in muballig_ids:
        found_traveller = db.query(models.Traveller).filter(models.Traveller.muballig_id == muballig_id).first()

        if not found_traveller:
            continue
        travellers.append(found_traveller)

    if travellers == []:
        return {"detail":"No travellers found"}
    
    return travellers