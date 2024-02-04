from fastapi import APIRouter, Depends, Response
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.jsonapi.json_api import JSONAPIPage, JSONAPIParams, JSONAPIResponse
from src.schemas.income_vo import IncomeUpdateVo, IncomeVo
from src.services.income_service import IncomeService
from src.settings.logging import logger

router = APIRouter(prefix="/income")
active_connections_set = set()


@router.get("/", response_model=JSONAPIPage[IncomeVo], response_model_exclude_none=True)
def get_all_income(db: Session = Depends(get_db), params: JSONAPIParams = Depends()):
    return IncomeService.get_all_paginated(db, paginate, params)


@router.get("/{month_id}", response_model=JSONAPIPage[IncomeVo], response_model_exclude_none=True)
def get_all_income_by_month(month_id: str, db: Session = Depends(get_db), params: JSONAPIParams = Depends()):
    return IncomeService.get_paginated_by_month(db, month_id, paginate, params)


@router.delete("/{income_id}")
def delete_income(income_id: str, response: Response, db: Session = Depends(get_db)):
    logger.info(f"Deleting income {income_id}")
    IncomeService.delete(db, income_id)
    response.status_code = 204


@router.patch("/{income_id}", response_model=JSONAPIResponse[IncomeVo], response_model_exclude_none=True)
def update_income(income_id: str, income: IncomeUpdateVo, db: Session = Depends(get_db)):
    logger.info(f"Updating bill {income_id}")
    updated_bill = IncomeService.update(db, income_id, income)
    return JSONAPIResponse(data=updated_bill)

# @router.websocket("/ws")
# async def expenses_subscription(websocket: WebSocket, db: Session = Depends(get_db)):
#     await websocket.accept()
#     active_connections_set.add(websocket)
#     logger.info('Websocket connection established')
#     queue = Queue()
#     active = True
#     subscription = SubscriptionService.subscribe('month', queue, lambda: active)
#     logger.info('Subscribed to month')
#
#     while True:
#         try:
#             data = queue.get(timeout=0.06)
#             if ('del' in data):
#                 await websocket.send_json(
#                     {
#                         'action': 'delete',
#                         'data':
#                             {
#                                 'id': data.split(' ')[1].upper().strip()
#                             }
#                     }
#                 )
#                 logger.info(f"Deleted expense {data.split(' ')[1]}")
#             else:
#                 month_id = data.split(' ')[1].upper().strip()
#                 response = MonthService.get_details(month_id, db)
#                 await websocket.send_json(
#                     {
#                         'action': 'update',
#                         'data': response.model_dump(mode='json')
#                     }
#                 )
#                 logger.info(f"Updated month {month_id}")
#         except Empty:
#             still_active = await _is_connection_alive(websocket)
#             if (still_active):
#                 continue
#             else:
#                 break
#
#     logger.info('Websocket connection closed')
#     active = False
#     subscription.unsubscribe()
#     active_connections_set.remove(websocket)
#
#
# @router.on_event("shutdown")
# async def shutdown():
#     logger.info('Shutting down')
#     for websocket in active_connections_set:
#         await websocket.close(code=1001)
#
#
# async def _is_connection_alive(websocket: WebSocket):
#     try:
#         await asyncio.wait_for(websocket.receive_bytes(), timeout=0.01)
#     except asyncio.TimeoutError:
#         # Connection is still alive
#         return True
#     except WebSocketDisconnect:
#         # Connection closed by client
#         logger.info('Connection has been closed')
#         return False
#     else:
#         # Received some data from the client, ignore it
#         return True
