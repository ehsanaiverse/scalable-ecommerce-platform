from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
import bcrypt

from app.src.db.database import get_db, SessionLocal
from app.src.core.config import SECRET_KEY, ALGORITHM, ADMIN_NAME, ADMIN_EMAIL, ADMIN_PASSWORD
from app.src.utils.exceptions import InvalidCredentialsException
from app.src.models.user import User


if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not set in .env")


# it used to get the token from the request header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login") 
http_bearer = HTTPBearer()

def create_token(data: dict):
    to_encode = data.copy()
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


# it used to get the current user from the token
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer), db: Session = Depends(get_db)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        id = payload.get("id")
        fullname = payload.get("fullname")
        email = payload.get("email")
        role = payload.get("role")
        
        if not all([id, fullname, email, role]):
            raise InvalidCredentialsException
        
        return {
            "id": id,
            "fullname": fullname,
            "email": email,
            "role": role
        }
    
    except JWTError:
        raise InvalidCredentialsException
    


def hashed_password(plain: str) -> str:
    return bcrypt.hashpw(
        plain.encode("utf-8"),
        bcrypt.gensalt()).decode("utf-8")



def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain.encode("utf-8"),
            hashed.encode("utf-8"))
    except Exception as exp:
        return exp


def required_role(required_role: str):
    def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user['role'] != required_role:
            raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Permission denied"
                )
        return current_user
    return role_checker



def create_default_admin():
    db: Session = SessionLocal()

    try:
        admin = db.query(User).filter(User.role == "admin").first()
        if admin:
            return  # Admin already exists

        if not all([ADMIN_NAME, ADMIN_EMAIL, ADMIN_PASSWORD]):
            raise RuntimeError("Admin credentials are not set in .env")

        admin_user = User(
            fullname=ADMIN_NAME,
            email=ADMIN_EMAIL,
            password=hashed_password(ADMIN_PASSWORD),
            role="admin"
        )

        db.add(admin_user)
        db.commit()
        print("Admin created from .env")

    finally:
        db.close()