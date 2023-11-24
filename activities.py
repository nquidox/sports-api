from typing import Annotated
from fastapi import Depends, APIRouter
from authentication import get_current_active_user
from db_worker import db_worker
from http_codes import c403
from models import UserModel, ActivityModel

router = APIRouter(tags=['Activities'])


@router.post('/{username}/add_activity')
async def add_activity(username: str,
                       current_user: Annotated[UserModel, Depends(get_current_active_user)],
                       act: ActivityModel):
    try:
        if username == current_user['username'] or current_user['is_superuser'] == 1:
            sql = ("INSERT INTO activities ("
                   "user_id, title, description, activity_type, laps, distance, date, time_start,"
                   "time_end, published, visibility) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")
            values = (current_user['id'], act.title, act.description, act.activity_type, act.laps,
                      act.distance, act.date, act.time_start, act.time_end, act.published, act.visibility)
            db_worker('ins', sql, values)
            return act

        else:
            return c403

    except Exception as e:
        return {'error': e}


@router.get('/{username}/activities/{act_id}')
async def get_activity_by_id(username: str, act_id: int,
                             current_user: Annotated[UserModel, Depends(get_current_active_user)]):
    try:
        if username == current_user['username'] or current_user['is_superuser'] == 1:
            sql = "SELECT * FROM activities WHERE user_id = ? AND id = ?"
            values = (current_user['id'], act_id)
            return db_worker('fo', sql, values)

        else:
            return c403

    except Exception as e:
        return {'error': e}


@router.get('/{username}/activities/{act_type}/')
async def get_activities_by_type(username: str, act_type: str,
                                 current_user: Annotated[UserModel, Depends(get_current_active_user)]):
    try:
        if username == current_user['username'] or current_user['is_superuser'] == 1:
            sql = '''SELECT user_id, username, title, description, activity_type,laps, distance, date,
            time_start, time_end, published, visibility FROM users JOIN activities ON user_id
            WHERE users.id = ? AND activity_type = ?'''
            values = (current_user['id'], act_type)
            return db_worker('fa', sql, values)

        else:
            return c403

    except Exception as e:
        return {'error': e}


@router.put('/{username}/activities/{act_id}/')
async def edit_activity(username: str, act_id: int,
                        act: ActivityModel,
                        current_user: Annotated[UserModel, Depends(get_current_active_user)]):
    try:
        if username == current_user['username'] or current_user['is_superuser'] == 1:
            sql = ("UPDATE activities SET title = ?, description = ?, activity_type = ?, laps = ?,"
                   "distance = ?, date = ?, time_start = ?, time_end = ?, published = ?, visibility = ?"
                   "WHERE user_id = ? AND id = ?")
            values = (act.title, act.description, act.activity_type, act.laps, act.distance, act.date,
                      act.time_start, act.time_end, act.published, act.visibility)
            values += (current_user['id'], act_id)
            db_worker('upd', sql, values)
            return act
        else:
            return c403

    except Exception as e:
        return {'error': e}


@router.delete('/{username}/activities/{act_id}/')
async def delete_activity(username: str, act_id: int,
                          current_user: Annotated[UserModel, Depends(get_current_active_user)]):
    try:
        if username == current_user['username'] or current_user['is_superuser'] == 1:
            sql = "DELETE FROM activities WHERE user_id = ? AND id = ?"
            values = (current_user['id'], act_id)
            db_worker('del', sql, values)
        else:
            return c403

    except Exception as e:
        return {'error': e}
