import random
import string
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.routing import APIRouter
from fastapi import Request, Response, Depends, HTTPException, status, Cookie
from datetime import datetime, timedelta, timezone
from hashlib import sha256

from db_worker import db_worker
from models import UserModel

router = APIRouter(tags=['Cookie authentication'])


def create_session(user_data: dict, request: Request, response: Response):
    exp_date = (datetime.utcnow() + timedelta(days=365 * 3)).astimezone(timezone.utc)

    token = sha256((str(user_data['id']) + user_data['username'] + str(exp_date)).encode('utf-8')).hexdigest()

    sql = "INSERT INTO sessions (user_id, token, client_info, expires) VALUES (?, ?, ?, ?)"
    values = (user_data['id'], token, request.headers['User-Agent'], str(exp_date))
    db_worker('ins', sql, values)

    response.set_cookie(key='token', value=token, httponly=True, secure=False, expires=exp_date)


def get_password_hash(plain_password, salt):
    return sha256((str(plain_password + salt)).encode('utf-8')).hexdigest()


def get_password_salt():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))


def get_user(username: str):
    return db_worker('fo', "SELECT * FROM users WHERE username = ?", (username, ))


def verify_password(plain_password: str, hashed_password: str, salt: str):
    return get_password_hash(plain_password, salt) == hashed_password


def authenticate_user(username: str, password: str):
    user = get_user(username)

    if not user:
        return False

    if not verify_password(password, user['cookie_secret'], user['salt']):
        return False

    return user


async def get_current_user(token: Annotated[str | None, Cookie()] = None):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials'
    )

    sql = "SELECT username FROM users JOIN sessions ON users.id = sessions.user_id WHERE token = ?"
    values = (token, )
    user_data = db_worker('fo', sql, values)

    if not user_data:
        raise credentials_exception

    user = get_user(user_data['username'])

    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(current_user: Annotated[UserModel, Depends(get_current_user)]):
    if current_user['disabled'] != 0:
        raise HTTPException(status_code=400, detail='Inactive User')
    return current_user


@router.post('/login')
async def cookie_login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                       request: Request, response: Response):
    user = authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
        )

    create_session(get_user(form_data.username), request, response)
