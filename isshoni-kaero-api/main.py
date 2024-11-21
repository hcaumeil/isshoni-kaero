from fastapi import FastAPI, Request
from fastapi.responses import Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder

from login import check_permission, router as login_router
from channels import router as channels_router
from users import router as users_router
from error import ErrorResponse, ErrorKind

# from building import router as building_router
# from floor import router as floor_router
# from place import router as place_router
# from booking import router as booking_router

import psycopg2
import biscuit_auth
import os


# get an env var, if the env var is not provided the program crash
def expect_env_var(var):
    res = os.environ.get(var)
    if res == None:
        print("error: please provide env ", var)
        exit(1)
    return res


private_key = expect_env_var("BISCUIT_KEY")
pg_db = expect_env_var("POSTGRESQL_ADDON_DB")
pg_host = expect_env_var("POSTGRESQL_ADDON_HOST")
pg_password = expect_env_var("POSTGRESQL_ADDON_PASSWORD")
pg_port = expect_env_var("POSTGRESQL_ADDON_PORT")
pg_user = expect_env_var("POSTGRESQL_ADDON_USER")

key = biscuit_auth.PrivateKey.from_hex(private_key)
db = psycopg2.connect(
    dbname=pg_db, host=pg_host, password=pg_password, port=pg_port, user=pg_user
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.keypair = biscuit_auth.KeyPair.from_private_key(key)
app.state.db = db

app.include_router(login_router)
app.include_router(users_router, prefix="/users")
app.include_router(channels_router, prefix="/channels")
# app.include_router(floor_router, prefix="/floors")
# app.include_router(place_router, prefix="/places")
# app.include_router(booking_router, prefix="/bookings")


@app.get("/")
def root() -> Response:
    return Response()


@app.get("/ping")
def ping():
    return "PONG !"


@app.middleware("http")
async def check_authentication(request: Request, call_next):
    auth = request.headers.get("Authorization")
    if request.method != "OPTIONS":
        if not check_permission(request, auth, request.app.state.keypair):
            return JSONResponse(
                jsonable_encoder(
                    ErrorResponse(
                        error_kind=ErrorKind.access_denied, error="access denied"
                    )
                ),
                401,
                {"WWW-Authenticate": "Bearer"},
            )

    return await call_next(request)
