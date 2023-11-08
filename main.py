from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from db_worker import init_db
import activities
import authentication
import users


app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory='templates')

app.include_router(authentication.router)
app.include_router(users.router)
app.include_router(activities.router)


@app.on_event('startup')
async def run_on_startup():
    init_db()


@app.get('/', response_class=HTMLResponse)
async def get_root(request: Request):
    return templates.TemplateResponse('index.html',
                                      {'request': request, 'first': 'Hello', 'second': 'world!'})
