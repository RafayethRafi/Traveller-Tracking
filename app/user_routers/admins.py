from .. import models, schemas , oauth2,send_email
from fastapi import Response,status,HTTPException,Depends,APIRouter
from sqlalchemy.orm import Session
from ..database import get_db
from typing import List


router = APIRouter(
    prefix= "/admins",
    tags=['Admins']
)


    



#an endpoint to find the users that are registered under an admin
@router.get("/registered_users/", status_code=status.HTTP_200_OK,response_model=List[schemas.UserOut])
def get_registered_users(db: Session = Depends(get_db),current_user:int=Depends(oauth2.get_current_user)) -> Response:

    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only Admins can view registered users")
    
    registered_users = db.query(models.User).filter(models.User.role != "admin").all()

    if not registered_users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No users registered.")
    
    return registered_users



@router.post("/invite_users/", status_code=status.HTTP_200_OK)
async def invite_users(invitations : List[schemas.InvitationBase],db: Session = Depends(get_db),current_user:int=Depends(oauth2.get_current_user)) -> Response:

    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only Admins can invite users")
    
    admin_id = current_user.id
    
    invited_users =[]
    
    for invitation in invitations:
        #check if the user is already invited
        is_invited = db.query(models.Invitations).filter(models.Invitations.email == invitation.email).first()
        is_registered = db.query(models.Invitations).filter(models.Invitations.email == invitation.email,models.Invitations.is_registered==True).first()

        if is_registered:
            invited_users.append({"email":invitation.email,"role":invitation.role,"status":"Already registered"})
            continue
        if is_invited:
            invited_users.append({"email":invitation.email,"role":invitation.role,"status":"Already invited"})
            continue

        new_invitation = models.Invitations(admin_id=admin_id,**invitation.model_dump())
        db.add(new_invitation)
        db.commit()
        db.refresh(new_invitation)

        invited_users.append({"email":invitation.email,"role":invitation.role,"status":"Invited"})

        send_email.send_invitation_email(invitation.email,invitation.role)

    #convert invited_users list to json
    invited_users = {"Invited users":invited_users}
        
    
    return invited_users


# Find the emails that the admin invited but not registered yet
@router.get("/pending_invitations/", status_code=status.HTTP_200_OK,response_model=List[schemas.InvitationBase])
def get_pending_invitations(db: Session = Depends(get_db),current_user:int=Depends(oauth2.get_current_user)) -> Response:

    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only Admins can view pending invitations")
    
    pending_invitations = db.query(models.Invitations).filter(models.Invitations.is_registered == False).all()

    if not pending_invitations:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No pending invitations for {current_user.email}")
    
    return pending_invitations


# create an endpoint to get all the users
@router.get("/get_data_operators/", status_code=status.HTTP_200_OK,response_model=List[schemas.UserOut])
def get_data_operators(db: Session = Depends(get_db),current_user:int=Depends(oauth2.get_current_user)) -> Response:

    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only Admins can view users")
    
    users = db.query(models.User).all()

    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No users found.")
    
    # if a user role is admin, remove it from the list
    users = [user for user in users if user.role == "data_operator"]
    
    return users


#create an endpoint to change the language of the user
@router.put("/change_language/", status_code=status.HTTP_200_OK)
def change_language(language:str,id:int,db: Session = Depends(get_db),current_user:int=Depends(oauth2.get_current_user)) -> Response:

    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only Admins can change language")
    
    #find the user with the given id
    user = db.query(models.User).filter(models.User.id == id).first()

    #if the user not found or not data operator raise an error
    if not user or (user.role != "data_operator" and user.role != "data_manager"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"User not found or the user is not data_operator or data_manager.")
    
    #change the language
    user.language = language
    db.commit()
    db.refresh(user)

    return {"message":f"Language changed successfully to {language} for user id: "+str(id)}