from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from db_worker import init_db
import activities
import authentication
import cookie_auth
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
app.include_router(cookie_auth.router)


@app.on_event('startup')
async def run_on_startup():
    init_db()
