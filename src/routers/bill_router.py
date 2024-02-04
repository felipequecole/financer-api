import asyncio
from queue import Empty, Queue

from fastapi import APIRouter, Depends, Response, WebSocket
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session
from starlette.websockets import WebSocketDisconnect

from src.database.db import get_db
from src.database.subscription import SubscriptionService
from src.jsonapi.json_api import JSONAPIPage, JSONAPIParams, JSONAPIResponse
from src.schemas.bill_vo import BillUpdateVo, BillVo
from src.services.bill_service import BillService
from src.settings.logging import logger

router = APIRouter(prefix="/bill")
active_connections_set = set()


@router.get("/", response_model=JSONAPIPage[BillVo], response_model_exclude_none=True)
def get_all_bills(db: Session = Depends(get_db), params: JSONAPIParams = Depends()):
    return BillService.get_all_paginated(db, paginate, params)


@router.get("/{month_id}", response_model=JSONAPIPage[BillVo], response_model_exclude_none=True)
def get_all_bills_by_month(month_id: str, db: Session = Depends(get_db), params: JSONAPIParams = Depends()):
    return BillService.get_paginated_by_month(db, month_id, paginate, params)


@router.post("/{month_id}", response_model=JSONAPIResponse[BillVo], response_model_exclude_none=True)
def create_bill(month_id: str, bill: BillUpdateVo, db: Session = Depends(get_db)):
    logger.info(f"Creating bill in month {month_id}")
    updated_bill = BillService.create(db, month_id, bill)
    return JSONAPIResponse(data=updated_bill)


@router.delete("/{bill_id}")
def delete_bill(bill_id: str, response: Response, db: Session = Depends(get_db)):
    logger.info(f"Deleting bill {bill_id}")
    BillService.delete(db, bill_id)
    response.status_code = 204


@router.patch("/{bill_id}", response_model=JSONAPIResponse[BillVo], response_model_exclude_none=True)
def update_expense(bill_id: str, bill: BillUpdateVo, db: Session = Depends(get_db)):
    logger.info(f"Updating bill {bill_id}")
    updated_bill = BillService.update(db, bill_id, bill)
    return JSONAPIResponse(data=updated_bill)


@router.websocket("/ws/{month_id}")
async def expenses_subscription(month_id: str, websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()
    active_connections_set.add(websocket)
    logger.info('Websocket connection established')
    queue = Queue()
    active = True
    subscription = SubscriptionService.subscribe(f'bill_{month_id}', queue, lambda: active)
    logger.info(f'Subscribed to bills on month {month_id}')

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
                bill_id = data.split(' ')[1].upper().strip()
                response = BillService.get_by_id(db, bill_id)
                await websocket.send_json(
                    {
                        'action': 'update',
                        'data': response.model_dump(mode='json')
                    }
                )
                logger.info(f"Updated bill {bill_id}")
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
