import asyncio
import uvicorn
import itsdangerous
import string
import secrets
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from starlette.templating import Jinja2Templates
from sse_starlette.sse import EventSourceResponse


session_secret = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(15))

middleware = [
    Middleware(CORSMiddleware,
      allow_origins=["https://127.0.0.1:4200"],
      allow_credentials=True,
      allow_headers=["*"],
      allow_methods=["*"]),
    Middleware(
        SessionMiddleware,
        secret_key=session_secret)
]

templates = Jinja2Templates(directory='templates')

async def homepage(request):
    request.session['enable'] = True
    return templates.TemplateResponse('index.html', {'request': request})

async def numbers(minimum, maximum):
    for i in range(minimum, maximum + 1):
        await asyncio.sleep(0.9)
        yield dict(data=i)

async def sse(request):
    generator = numbers(1, 5)
    return EventSourceResponse(generator)


routes = [
    Route('/', endpoint=homepage),
    Route("/stream", endpoint=sse)
]

app = Starlette(
    debug=True,
    routes=routes,
    middleware=middleware)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level='info')
