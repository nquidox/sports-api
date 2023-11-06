from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from db_worker import db_worker, init_db
from authentication import *
from models import ActivityModel

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
            return HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Resource is available but not accessible because of permissions',
                headers={})

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
            return HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Resource is available but not accessible because of permissions',
                headers={})

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
            return HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Resource is available but not accessible because of permissions',
                headers={})

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


@app.post('/add_activity/')
async def add_activity_run(current_user: Annotated[UserModel, Depends(get_current_active_user)],
                           act: ActivityModel):
    try:
        sql = ("INSERT INTO activities ("
               "user_id, title, description, activity_type, laps, distance, date, time_start,"
               "time_end, published, visibility) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")
        values = (current_user['id'], act.title, act.description, act.activity_type, act.laps,
                  act.distance, act.date, act.time_start, act.time_end, act.published, act.visibility)
        db_worker('ins', sql, values)
        return act

    except Exception as e:
        return {'error': e}
