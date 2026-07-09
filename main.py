from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / '.env')

import mimetypes
mimetypes.add_type('application/javascript', '.js')
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from agent.setup import Agent
from agent.support.logic import create_db_and_tables
import asyncio


import traceback

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*']
)

app.mount('/static', StaticFiles(directory="frontend/static"), name='static')

@app.get('/', include_in_schema=False)
async def serve_home():
    return FileResponse('frontend/index.html')

@app.websocket('/agent/{mode}/{lang}')
async def call_agent(websocket: WebSocket, mode: str, lang: str):
    await websocket.accept()

    try:
        voice_agent = Agent(websocket=websocket)

        await voice_agent.run(mode, lang)

    except asyncio.CancelledError:
        return 204
    
    except Exception as exc:
        traceback.print_exc()

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, port=9000)