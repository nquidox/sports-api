from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from db_worker import db_worker, init_db
from authentication import *
from models import ActivityModel
from http_codes import c403

app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory='templates')


@app.on_event('startup')
async def run_on_startup():
    init_db()


@app.get('/', response_class=HTMLResponse)
async def get_root(request: Request):
    return templates.TemplateResponse('index.html',
                                      {'request': request, 'first': 'Hello', 'second': 'world!'})


@app.post('/users/')
async def create_user(user: UserModel):
    try:
        hashed_password = get_password_hash(user.hashed_password)
        sql = ("INSERT INTO users (username, first_name, last_name, birthday, gender, disabled, hashed_password, "
               "is_superuser) VALUES (?, ?, ?, ?, ?, ?, ?, ?)")
        values = (user.username, user.first_name, user.last_name, user.birthday, user.gender, user.disabled,
                  hashed_password, 0)
        db_worker('ins', sql, values)
        return user

    except Exception as e:
        return {'error': e}


@app.get('/users/{user_id}')
async def get_user(user_id: int, current_user: Annotated[UserModel, Depends(get_current_active_user)]):
    try:
        if user_id == current_user['id'] or current_user['is_superuser'] == 1:
            sql = "SELECT username, first_name, last_name, birthday, gender FROM users WHERE id = ?"
            values = (user_id, )
            r = db_worker('fo', sql, values)
            return {'username': r[0], 'first_name': r[1], 'last_name': r[2], 'birthday': r[3], 'gender': r[4]}
        else:
            return c403

    except Exception as e:
        return {'error': e}


@app.delete('/users/{user_id}')
async def delete_user(user_id: int, current_user: Annotated[UserModel, Depends(get_current_active_user)]):
    try:
        if user_id == current_user['id'] or current_user['is_superuser'] == 1:
            sql = "DELETE FROM users WHERE id = ?"
            values = (user_id, )
            db_worker('del', sql, values)
        else:
            return c403

    except Exception as e:
        return {'error': e}


@app.put('/users/{user_id}')
async def update_user(user_id: int, user: UserModel,
                      current_user: Annotated[UserModel, Depends(get_current_active_user)]):
    try:
        if user_id == current_user['id'] or current_user['is_superuser'] == 1:
            values = (user.username, user.first_name, user.last_name, user.birthday, user.gender, user.is_superuser,
                      user_id)
            sql = ("UPDATE users SET username = ?, first_name=?, last_name=?, birthday=?, gender=?, is_superuser=?"
                   "WHERE id=?")
            db_worker('upd', sql, values)
            return user

        else:
            return c403

    except Exception as e:
        return {'error': e}


@app.post('/token', response_model=Token)
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


@app.post('/{user_id}/add_activity')
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


@app.get('/{user_id}/activities/{act_id}')
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


@app.put('/{user_id}/activities/{act_id}')
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


@app.delete('/{user_id}/activities/{act_id}')
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
