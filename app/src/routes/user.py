from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.src.schemas.user import UserRegister, UserLogin, UserProfile, ChangePassword, ForgetPassword, VerifyOTP
from app.src.db.database import get_db
from app.src.models.user import User
from app.src.utils.exceptions import EmailAlreadyRegisteredException, InvalidCredentialsException, UserNotFoundException, OTPNotFoundException, InvalidOTPException
from app.src.core.security import get_current_user, hashed_password, verify_password, create_token, required_role
from app.src.utils.otp import generate_otp
from app.src.models.notification import Notification
from app.src.security.manager import Manager

router = APIRouter(prefix="/user", tags=["User"])

@router.post('/register')
async def register(user:UserRegister, db:Session=Depends(get_db)):
    
    existing_user = db.query(User).filter(User.email == user.email).first()
    
    if existing_user:
        raise EmailAlreadyRegisteredException
    
    new_user = User(
        fullname = user.fullname,
        email = user.email,
        password = user.password
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    
    # create notification unread
    notification_meassage = Notification(
        id = new_user.id,
        message = "New user registored"
    )
    
    db.add(notification_meassage)
    db.commit()
    
    # send realtime notification
    await Manager.send_to_user(
        user_id=new_user.id,
        message="New user registored"
    )
    
    return {"message": "You are registered"}



@router.post('/login')
async def user_login(user:UserLogin, db:Session=Depends(get_db)):
    
    existing_user=db.query(User).filter(User.email == user.email).first()
    
    if not existing_user or not verify_password(existing_user.password, user.password):
        raise InvalidCredentialsException
    
    # create token
    payload = {
        "id": existing_user.id,
        "fullname": existing_user.fullname,
        "email": existing_user.email,
        "role": existing_user.role,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }

    access_token = create_token(data=payload)
    
    # save notification (unread)
    if existing_user.role == 'admin':
        notification_message = Notification(
            id=existing_user.id,
            message="Admin logged in",
            is_read=True
        )
    else:
        notification_message = Notification(
            id=existing_user.id,
            message="User logged in"
        )

    db.add(notification_message)
    db.commit()
    db.refresh(notification_message)

    # send realtime notification (only if user is connected)
    await Manager.send_to_user(
        user_id=existing_user.id,
        message="Login successful"
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get('/profile')
def user_profile(user:dict = Depends(get_current_user)):
    
    data = {
        'id': user['id'],
        'fullname': user['fullname'],
        'email': user['email'],
        'role': user['role']
    }
    
    return data



# user change password
@router.post('/change-password')
async def change_password(user: ChangePassword, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        if not verify_password(user.old_password, existing_user.password):
            raise InvalidCredentialsException
        
        # make new password hashed
        existing_user.password = hashed_password(user.new_password)

        db.commit()
        db.refresh(existing_user)
        
        # save notification (unread)
        notification_message = Notification(
            id=existing_user.id,
            message="Password updated",
            is_read=False
        )

        db.add(notification_message)
        db.commit()
        db.refresh(notification_message)

        # send realtime notification (only if user is connected)
        await Manager.send_to_user(
            user_id=existing_user.id,
            message="Password update"
        )
        
        
        return {"message": "Password changed successfully"}
    raise InvalidCredentialsException



            
# user forget password
@router.post('/forget-password')
async def forget_password(user: ForgetPassword, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    
    if not existing_user:
        raise UserNotFoundException
    
    otp = generate_otp()
    existing_user.otp = otp   # assign otp to existing user
    
    db.commit()
    db.refresh(existing_user)
        
    # save notification (unread)
    notification_message = Notification(
        id=existing_user.id,
        message="Password forgeted",
        is_read=False
    )

    db.add(notification_message)
    db.commit()
    db.refresh(notification_message)

    # send realtime notification (only if user is connected)
    await Manager.send_to_user(
        user_id=existing_user.id,
        message="Password foget successful"
    )
    
    return {
        "message": "OTP sent on email",
        "OTP": existing_user.otp
    }
    

@router.post('/verify-otp')
async def verify_otp(otp: VerifyOTP, db: Session = Depends(get_db)):
    
    existing_user = db.query(User).filter(User.email == otp.email).first()
    
    if not existing_user:
        raise UserNotFoundException
    
    if not existing_user.otp:
        raise OTPNotFoundException
    
    if otp.otp != existing_user.otp:
        raise InvalidOTPException
    
    existing_user.password = hashed_password(otp.new_password)
    
    existing_user.otp = None
    
    db.commit()
    
    
    # save notification (unread)
    notification_message = Notification(
        id=existing_user.id,
        message="OTP verified",
        is_read=False
    )

    db.add(notification_message)
    db.commit()
    db.refresh(notification_message)

    # send realtime notification (only if user is connected)
    await Manager.send_to_user(
        user_id=existing_user.id,
        message="OTP verified successful"
    )
    
    return {
        "message": "OTP verified and password reset successfully"
    }
