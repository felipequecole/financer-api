import asyncio
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Queue
from queue import Empty
from typing import List

from fastapi import APIRouter, Depends, WebSocket
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.database.subscription import subscribe
from src.schemas.expense_vo import ExpenseRequestVo, ExpenseUpdateVo, ExpenseVo
from src.services import expenses as expenses_service
from src.services.expenses import get_expense_by_id
from src.settings.logging import logger
from starlette.websockets import WebSocketDisconnect

router = APIRouter(prefix="/expenses")
active_connections_set = set()


@router.get(path="/", response_model=List[ExpenseVo], response_model_exclude_none=True)
def list_all(db: Session = Depends(get_db)):
    return expenses_service.get_all_expenses(db)


@router.post("/", response_model=ExpenseVo, response_model_exclude_none=True)
def add_expense(expense: ExpenseRequestVo, db: Session = Depends(get_db)):
    return expenses_service.create_expense(db, expense)


@router.patch("/{expense_id}", response_model=ExpenseVo, response_model_exclude_none=True)
def update_expense(expense_id: int, expense: ExpenseUpdateVo, db: Session = Depends(get_db)):
    logger.info(f"Updating expense {expense_id}")
    return expenses_service.update_expense(db, expense_id, expense)


@router.delete("/{expense_id}")
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    logger.info(f"Deleting expense {expense_id}")
    return expenses_service.delete_expense(db, expense_id)


@router.websocket("/liveupdates")
async def expenses_subscription(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()
    active_connections_set.add(websocket)
    logger.info('Websocket connection established')
    queue = Queue()
    executor = ThreadPoolExecutor(max_workers=1)
    active = True
    subscribe('expenses', queue, executor, lambda: active)
    logger.info('Subscribed to expenses')

    while True:
        try:
            data = queue.get(timeout=0.06)
            if ('del' in data):
                await websocket.send_json(
                    {
                        'action': 'delete',
                        'data':
                            {
                                'id': int(data.split(' ')[1])
                            }
                    }
                )
                logger.info(f"Deleted expense {data.split(' ')[1]}")
            else:
                expense_id = int(data.split(' ')[1])
                response = get_expense_by_id(db, int(expense_id))
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
    active_connections_set.remove(websocket)
    executor.shutdown(wait=True, cancel_futures=True)


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
        return False
    else:
        # Received some data from the client, ignore it
        return True
