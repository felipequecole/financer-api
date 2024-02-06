import uvicorn
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi_pagination import add_pagination
from starlette.middleware.cors import CORSMiddleware
from uvicorn.config import LOGGING_CONFIG

from src.errors.UserError import UserError
from src.jsonapi.json_api import JSONAPIError, JSONAPIErrorResponse
from src.routers.bill_router import router as bill_router
from src.routers.expenses_router import router as expenses_router
from src.routers.income_router import router as income_router
from src.routers.months_router import router as months_router

origins = [
    "*"
]
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(expenses_router)
app.include_router(months_router)
app.include_router(bill_router)
app.include_router(income_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.exception_handler(UserError)
async def user_error_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=JSONAPIErrorResponse(errors=[
            JSONAPIError(
                status=str(status.HTTP_400_BAD_REQUEST),
                title="User Error",
                detail=exc.message,
                code=exc.code
            )
        ])
        .model_dump(mode='json', exclude_none=True),
    )


add_pagination(app)

if (__name__ == '__main__'):
    LOGGING_CONFIG["formatters"]["default"]["fmt"] = "%(asctime)s [%(name)s] %(levelprefix)s %(message)s"
    uvicorn.run(app, host='0.0.0.0')
