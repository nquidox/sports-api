from typing import Annotated
from fastapi import Depends, APIRouter
from authentication import get_password_hash, get_current_active_user
from cookie_auth import get_password_hash as gph
from db_worker import db_worker
from http_codes import c403
from models import UserModel


router = APIRouter(prefix='/user', tags=['Users'])


@router.post('/')
async def create_user(user: UserModel):
    try:
        hashed_password = get_password_hash(user.hashed_password)
        sql = ("INSERT INTO users (username, first_name, last_name, birthday, gender, disabled, hashed_password,"
               "is_superuser, cookie_secret) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)")
        values = (user.username, user.first_name, user.last_name, user.birthday, user.gender, user.disabled,
                  hashed_password, 0, gph(user.hashed_password))
        db_worker('ins', sql, values)
        return user

    except Exception as e:
        return {'error': e}


@router.get('/{user_id}')
async def get_user_by_id(user_id: int, current_user: Annotated[UserModel, Depends(get_current_active_user)]):
    try:
        if user_id == current_user['id'] or current_user['is_superuser'] == 1:
            sql = "SELECT username, first_name, last_name, birthday, gender FROM users WHERE id = ?"
            values = (user_id, )
            return db_worker('fo', sql, values)
        else:
            return c403

    except Exception as e:
        return {'error': e}


@router.get('/{username}/')
async def get_user_by_username(username: str, current_user: Annotated[UserModel, Depends(get_current_active_user)]):
    try:
        if username == current_user['username'] or current_user['is_superuser'] == 1:
            sql = "SELECT username, first_name, last_name, birthday, gender FROM users WHERE username = ?"
            values = (username, )
            return db_worker('fo', sql, values)
        else:
            return c403

    except Exception as e:
        return {'error': e}


@router.put('/{username}/')
async def update_user(username: str, user: UserModel,
                      current_user: Annotated[UserModel, Depends(get_current_active_user)]):
    try:
        if username == current_user['username'] or current_user['is_superuser'] == 1:
            values = (user.username, user.first_name, user.last_name, user.birthday, user.gender, user.is_superuser,
                      current_user['id'])
            sql = ("UPDATE users SET username = ?, first_name=?, last_name=?, birthday=?, gender=?, is_superuser=?"
                   "WHERE id=?")
            db_worker('upd', sql, values)
            return user

        else:
            return c403

    except Exception as e:
        return {'error': e}


@router.delete('/{username}/')
async def delete_user(username: str, current_user: Annotated[UserModel, Depends(get_current_active_user)]):
    try:
        if username == current_user['username'] or current_user['is_superuser'] == 1:
            sql = "DELETE FROM users WHERE id = ?"
            values = (current_user['id'], )
            db_worker('del', sql, values)
        else:
            return c403

    except Exception as e:
        return {'error': e}
