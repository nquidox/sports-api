from typing import Annotated
from fastapi import Depends, APIRouter
from authentication import get_current_active_user
from db_worker import db_worker
from http_codes import c403
from models import UserModel, ActivityModel


router = APIRouter(tags=['Activities'])


@router.post('/{user_id}/add_activity')
async def add_activity_run(user_id: int,
                           current_user: Annotated[UserModel, Depends(get_current_active_user)],
                           act: ActivityModel):
    try:
        if user_id == current_user['id'] or current_user['is_superuser'] == 1:
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


@router.get('/{user_id}/activities/{act_id}')
async def get_activity(user_id: int, act_id: int,
                       current_user: Annotated[UserModel, Depends(get_current_active_user)]):
    try:
        if user_id == current_user['id'] or current_user['is_superuser'] == 1:
            sql = "SELECT * FROM activities WHERE user_id = ? AND id = ?"
            values = (user_id, act_id)
            r = db_worker('fo', sql, values)
            # refactor this with 'out' model, also add return of all activities
            d = {'id': r[0], 'user_id': r[1], 'title': r[2], 'description': r[3], 'activity_type': r[4],
                 'laps': r[5], 'distance': r[6], 'date': r[7], 'time_start': r[8], 'time_end': r[9],
                 'published': r[10], 'visibility': r[11]}
            return d

        else:
            return c403

    except Exception as e:
        return {'error': e}


@router.put('/{user_id}/activities/{act_id}')
async def edit_activity(user_id: int, act_id: int,
                        act: ActivityModel,
                        current_user: Annotated[UserModel, Depends(get_current_active_user)]):
    try:
        if user_id == current_user['id'] or current_user['is_superuser'] == 1:
            sql = ("UPDATE activities SET title = ?, description = ?, activity_type = ?, laps = ?,"
                   "distance = ?, date = ?, time_start = ?, time_end = ?, published = ?, visibility = ?"
                   "WHERE user_id = ? AND id = ?")
            values = (act.title, act.description, act.activity_type, act.laps, act.distance, act.date,
                      act.time_start, act.time_end, act.published, act.visibility)
            values += (user_id, act_id)
            db_worker('upd', sql, values)
            return act
        else:
            return c403

    except Exception as e:
        return {'error': e}


@router.delete('/{user_id}/activities/{act_id}')
async def delete_activity(user_id: int, act_id: int,
                          current_user: Annotated[UserModel, Depends(get_current_active_user)]):
    try:
        if user_id == current_user['id'] or current_user['is_superuser'] == 1:
            sql = "DELETE FROM activities WHERE user_id = ? AND id = ?"
            values = (user_id, act_id)
            db_worker('del', sql, values)
        else:
            return c403

    except Exception as e:
        return {'error': e}
