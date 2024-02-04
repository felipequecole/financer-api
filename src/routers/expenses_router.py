import asyncio
from multiprocessing import Queue
from queue import Empty

from fastapi import APIRouter, Depends, WebSocket
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session
from starlette.websockets import WebSocketDisconnect

from src.database.db import get_db
from src.database.subscription import SubscriptionService
from src.jsonapi.json_api import JSONAPIPage, JSONAPIParams, JSONAPIResponse
from src.schemas.expense_vo import ExpenseRequestVo, ExpenseUpdateVo, ExpenseVo
from src.services.expenses_service import ExpenseService
from src.settings.logging import logger

router = APIRouter(prefix="/expenses")
active_connections_set = set()


@router.get(path="/", response_model=JSONAPIPage[ExpenseVo], response_model_exclude_none=True)
def list_all(db: Session = Depends(get_db), params: JSONAPIParams = Depends()):
    return ExpenseService.get_all(db, paginate, params)


@router.post("/", response_model=JSONAPIResponse[ExpenseVo], response_model_exclude_none=True)
def add_expense(expense: ExpenseRequestVo, db: Session = Depends(get_db)):
    expense = ExpenseService.create(db, expense)
    return JSONAPIResponse(data=expense)


@router.patch("/{expense_id}", response_model=JSONAPIResponse[ExpenseVo], response_model_exclude_none=True)
def update_expense(expense_id: str, expense: ExpenseUpdateVo, db: Session = Depends(get_db)):
    logger.info(f"Updating expense {expense_id}")
    updated_expense = ExpenseService.update(db, expense_id, expense)
    return JSONAPIResponse(data=updated_expense)


@router.delete("/{expense_id}")
def delete_expense(expense_id: str, db: Session = Depends(get_db)):
    logger.info(f"Deleting expense {expense_id}")
    return ExpenseService.delete(db, expense_id)


@router.get("/{expense_id}", response_model=JSONAPIResponse[ExpenseVo], response_model_exclude_none=True)
def get_by_id(expense_id: str, db: Session = Depends(get_db)):
    logger.info(f"Getting expense {expense_id}")
    expense = ExpenseService.get_by_id(db, expense_id)
    return JSONAPIResponse(data=expense)


@router.websocket("/ws")
async def expenses_subscription(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()
    active_connections_set.add(websocket)
    logger.info('Websocket connection established')
    queue = Queue()
    active = True
    subscription = SubscriptionService.subscribe('expenses', queue, lambda: active)
    logger.info('Subscribed to expenses')

    while True:
        try:
            data = queue.get_nowait()
            if ('del' in data):
                await websocket.send_json(
                    {
                        'action': 'delete',
                        'data':
                            {
                                'id': data.split(' ')[1].upper().strip()
                            }
                    }
                )
                logger.info(f"Deleted expense {data.split(' ')[1]}")
            else:
                expense_id = data.split(' ')[1].upper().strip()
                response = ExpenseService.get_by_id(db, expense_id)
                await websocket.send_json(
                    {
                        'action': 'update',
                        'data': response.model_dump(mode='json')
                    }
                )
                logger.info(f"Updated expense {expense_id}")
        except Empty:
            still_active = await _is_connection_alive(websocket)
            if (still_active):
                continue
            else:
                break

    logger.info('Websocket connection closed')
    active = False
    subscription.unsubscribe()
    active_connections_set.remove(websocket)


@router.on_event("shutdown")
async def shutdown():
    logger.info('Shutting down')
    for websocket in active_connections_set:
        await websocket.close(code=1001)


async def _is_connection_alive(websocket: WebSocket):
    try:
        await asyncio.wait_for(websocket.receive_bytes(), timeout=0.01)
    except asyncio.TimeoutError:
        # Connection is still alive
        return True
    except WebSocketDisconnect:
        # Connection closed by client
        logger.info('Connection has been closed')
        return False
    else:
        # Received some data from the client, ignore it
        return True
