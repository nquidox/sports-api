from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException, status, APIRouter
from typing import Annotated
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

from pydantic import BaseModel
from models import UserModel
from db_worker import db_worker

MINUTES = 60
SECRET_KEY = '229f99f5f9187b139cfba8bc80cc1bf107d51684eb8bd17571b939b4b465007a'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = MINUTES

router = APIRouter()


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(username):
    users_list = db_worker('fa', 'SELECT username FROM users')

    if any(x['username'] == username for x in users_list):
        user = db_worker('fo', 'SELECT * FROM users WHERE username = ?', (username, ))
        return user


def authenticate_user(username: str, password: str):
    user = get_user(username)

    if not user:
        return False

    if not verify_password(password, user['hashed_password']):
        return False

    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta

    else:
        expire = datetime.utcnow() + timedelta(minutes=MINUTES)

    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'}
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')

        if username is None:
            raise credentials_exception

        token_data = TokenData(username=username)

    except JWTError:
        raise credentials_exception

    user = get_user(token_data.username)

    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(current_user: Annotated[UserModel, Depends(get_current_user)]):
    if current_user['disabled'] != 0:
        raise HTTPException(status_code=400, detail='Inactive User')
    return current_user


@router.post('/token', tags=['Token'], response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': user['username']}, expires_delta=access_token_expires
    )
    return {'access_token': access_token, 'token_type': 'bearer'}
