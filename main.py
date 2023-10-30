from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from models import UserModel
from db_worker import db_worker, init_db
from authentication import *

app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory='templates')


@app.on_event('startup')
async def run_on_startup():
    init_db()
    pass


@app.get('/', response_class=HTMLResponse)
async def get_root(request: Request):
    return templates.TemplateResponse('index.html', {'request': request, 'first': 'Hello', 'second': 'world!'})


@app.post('/users/')
async def create_user(user: UserModel):
    try:
        sql = "INSERT INTO users (username, first_name, last_name, birthday, gender, disabled) VALUES (?, ?, ?, ?, ?, ?)"
        values = (user.username, user.first_name, user.last_name, user.birthday, user.gender, user.disabled)
        db_worker('ins', sql, values)
        return user

    except Exception as e:
        return {'error': e}


@app.get('/users/{user_id}')
async def get_user(user_id: int):
    try:
        sql = "SELECT username, first_name, last_name, birthday, gender FROM users WHERE id = ?"
        values = (user_id, )
        r = db_worker('fo', sql, values)
        return {'username': r[0], 'first_name': r[1], 'last_name': r[2], 'birthday': r[3], 'gender': r[4]}

    except Exception as e:
        return {'error': 'Not found'}


@app.delete('/users/{user_id}')
async def delete_user(user_id: int):
    try:
        sql = "DELETE FROM users WHERE id = ?"
        values = (user_id, )
        db_worker('del', sql, values)

    except Exception as e:
        return {'error': e}


@app.put('/users/{user_id}')
async def update_user(user_id: int, user: UserModel):
    try:
        values = (user.username, user.first_name, user.last_name, user.birthday, user.gender, user_id)
        sql = "UPDATE users SET username = ?, first_name=?, last_name=?, birthday=?, gender=? WHERE id=?"
        db_worker('upd', sql, values)
        return user
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


@app.get('/users/me/', response_model=UserModel)
async def read_users_me(current_user: Annotated[UserModel, Depends(get_current_active_user)]):
    return current_user


@app.get("/users/me/details")
async def read_own_items(current_user: Annotated[UserModel, Depends(get_current_active_user)]):
    return [{'username': current_user['username'], 'first name': current_user['first_name'], 'last name': current_user['last_name'],}]
