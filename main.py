from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / '.env')

import mimetypes
mimetypes.add_type('application/javascript', '.js')
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response, JSONResponse
from agent.setup import Agent
from agent.support.load_seed_data import load_seed_data
from agent.support.logic import (
    engine, 
    create_db_and_tables, 
    get_products as handle_get_products, 
    search_account, 
    search_order,
    get_account_payments as handle_get_account_payments,
    get_requests,
    update_payment
)
import asyncio

from typing_extensions import TypedDict
import traceback

import json

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_seed_data()
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

# Customer Support Endpoints
@app.get('/products')
async def get_products():
    
    products = await handle_get_products(engine)

    if products:
        return products

    raise HTTPException(500)

@app.get('/orders/{account_id}')
async def get_account_orders(account_id: str):
    account = await search_account(engine, account_id)
    if account is not None:
        orders = await search_order(engine, account=account['id'])

        if orders:
            return orders

    raise HTTPException(500)

@app.get('/payments/{account_id}')
async def get_account_payments(account_id: str):
    account = await search_account(engine, account_id)
    if account is not None:
        payments = await handle_get_account_payments(engine, account['id'])
        if payments:
            return payments


    raise HTTPException(500)

@app.get('/requests/{account_id}')
async def get_account_requests(account_id: str):
    account = await search_account(engine, account_id)
    if account is not None:
        requests = await get_requests(engine, 'request', account['id'])

        return requests
    
    raise HTTPException(500)

@app.get('/complaints/{account_id}')
async def get_account_complaints(account_id: str):
    account = await search_account(engine, account_id)
    if account is not None:
        requests = await get_requests(engine, 'complaint', account['id'])

        return requests
    
    raise HTTPException(500)

@app.post('/reset-password/{account_id}')
async def reset_account_password(request, account_id: str):
    new_password = request.new_password
    
    return Response()

class PaymentRequest(TypedDict):
    complete: bool

@app.post('/pay/{payment_id}/{account_id}')
async def complete_payment(request:PaymentRequest, payment_id: str, account_id: str):
    account = await search_account(engine, account_id)
    if account is not None:
        complete = request['complete']

        result = await update_payment(engine, payment_id, complete)
        
        return JSONResponse({'complete': result}, 200)



if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, port=9000)