from fastapi import APIRouter,Depends,status,HTTPException,Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import database , schemas,models,utils,oauth2
from ..database import get_db
import asyncio

router = APIRouter(tags=['Authentication'])

@router.post('/login',response_model=schemas.Token,status_code=status.HTTP_200_OK)
async def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    #user_credentials will return only usename and password
    
    # user = db.query(models.User).filter(models.User.email == user_credentials.email).first()

    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
    
    if not utils.verify(user_credentials.password,user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials") 

    access_token = oauth2.create_access_token(data = {"user_id" : user.id})
    return {"access_token": access_token, "token_type": "bearer"}




@router.put('/password_reset/{id}_{email}',status_code=status.HTTP_200_OK)
def password_reset(id:int,email:str,user_provided_info:schemas.PassReset,db: Session = Depends(database.get_db)):
    
    user = db.query(models.User).filter(models.User.email == email).first()
    user2 = db.query(models.User).filter(models.User.email == user_provided_info.u_p_email).first()
    if not user or not user2:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if user.id != id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    
    hashed_password = utils.hash(user_provided_info.password)
    hashed_password2 = utils.hash(user_provided_info.re_password)

    if hashed_password != hashed_password2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")
    
    user.password = hashed_password
    db.commit()
    db.refresh(user)


    return {"detail":"Password updated successfully"}
