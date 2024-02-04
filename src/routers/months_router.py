import asyncio
from queue import Empty, Queue

from fastapi import APIRouter, Depends, Response, WebSocket
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session
from starlette.websockets import WebSocketDisconnect

from src.database.db import get_db
from src.database.subscription import SubscriptionService
from src.jsonapi.json_api import JSONAPIPage, JSONAPIParams, JSONAPIResponse
from src.schemas.month_vo import MonthCreateRequest, MonthDetailsVo
from src.services.month_service import MonthService
from src.settings.logging import logger

router = APIRouter(prefix="/month")
active_connections_set = set()


@router.get("/", response_model=JSONAPIPage[MonthDetailsVo], response_model_exclude_none=True)
def get_all_months(db: Session = Depends(get_db), params: JSONAPIParams = Depends()):
    return MonthService.get_all(db, paginate, params)


@router.delete("/{month_id}")
def delete_month(month_id: str, response: Response, db: Session = Depends(get_db)):
    logger.info(f"Deleting month {month_id}")
    MonthService.delete(month_id, db)
    response.status_code = 204


@router.post("/create", response_model=JSONAPIResponse[MonthDetailsVo], response_model_exclude_none=True)
def create_month(month_spec: MonthCreateRequest, db: Session = Depends(get_db)):
    month = MonthService.create(month_spec, db)
    return JSONAPIResponse(data=month)


@router.websocket("/ws")
async def expenses_subscription(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()
    active_connections_set.add(websocket)
    logger.info('Websocket connection established')
    queue = Queue()
    active = True
    subscription = SubscriptionService.subscribe('month', queue, lambda: active)
    logger.info('Subscribed to month')

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
                month_id = data.split(' ')[1].upper().strip()
                response = MonthService.get_details(month_id, db)
                await websocket.send_json(
                    {
                        'action': 'update',
                        'data': response.model_dump(mode='json')
                    }
                )
                logger.info(f"Updated month {month_id}")
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
