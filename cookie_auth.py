from typing import Annotated
from fastapi.routing import APIRouter
from fastapi import Response, Depends
from datetime import datetime, timedelta, timezone
from hashlib import sha256

from authentication import get_current_user
from db_worker import db_worker
from models import UserModel

router = APIRouter(tags=['Cookie authentication'])


@router.get('/cookie')
async def get_cookie(response: Response, current_user: Annotated[UserModel, Depends(get_current_user)]):
    sql = "SELECT * FROM users WHERE username = ?"
    values = (current_user['username'], )
    result = db_worker('fo', sql, values)

    if not result['cookie_secret']:
        generate_secret = sha256((str(result['id']) + result['username']).encode('utf-8')).hexdigest()

        sql = "UPDATE users SET cookie_secret=? WHERE username=?"
        values = (generate_secret, current_user['username'])
        db_worker('upd', sql, values)

        exp_date = (datetime.utcnow() + timedelta(days=365*3)).astimezone(timezone.utc)
        response.set_cookie(key='token', value=generate_secret, httponly=True, secure=False, expires=exp_date)
        return {'cookie_test': exp_date}
