from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from db_worker import init_db
import activities
import authentication
import users


app = FastAPI()

# CORS
origins = [
    'http://localhost:8080',
    'http://127.0.0.1:8080',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

# routers
app.include_router(authentication.router)
app.include_router(users.router)
app.include_router(activities.router)


@app.on_event('startup')
async def run_on_startup():
    init_db()


@app.get('/cookie', tags=['Cookie test'])
async def get_cookie(response: Response):
    exp_date = (datetime.utcnow() + timedelta(days=365*3)).astimezone(timezone.utc)
    response.set_cookie(key='cookie_test', value='some info', httponly=True, secure=False, expires=exp_date)
    return {'cookie_test': exp_date}
