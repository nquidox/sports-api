from fastapi import FastAPI
from db_worker import init_db
import activities
import authentication
import users


app = FastAPI()
app.include_router(authentication.router)
app.include_router(users.router)
app.include_router(activities.router)


@app.on_event('startup')
async def run_on_startup():
    init_db()
