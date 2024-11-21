from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from biscuit_auth import Authorizer, KeyPair, BiscuitBuilder, Biscuit, Rule
from pydantic import BaseModel
import hashlib

from error import ErrorResponse, ErrorKind
from users import create_user, users_emails, fetch_user_password, User

router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    token: str


class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str


def check_permission(r: Request, auth, k: KeyPair):
    if (
        r.url.path[1:] == "login"
        or r.url.path[1:] == "register"
        or r.url.path[1:] == ""
        or r.url.path[1:] == "ping"
    ):
        return True

    try:
        scheme, data = (auth or " ").split(" ", 1)
        if scheme != "Bearer":
            return False
    except:
        return False

    token = Biscuit.from_base64(data, k.public_key)
    authorizer = Authorizer("allow if user($u);")

    authorizer.add_token(token)

    if authorizer.authorize() >= 0:
        r.state.user = authorizer.query(Rule("user($u) <- user($u)"))[0].terms[0]
        return True
    else:
        return False


def make_token(k: KeyPair, user: str):
    return (
        BiscuitBuilder(
            """
    user({user_id});
    """,
            {
                "user_id": user,
            },
        )
        .build(k.private_key)
        .to_base64()
    )


@router.post("/register")
def register(r: Request, body: RegisterRequest):
    emails = users_emails(r.app.state.db)

    if body.email in emails:
        return JSONResponse(
            status_code=400,
            content=jsonable_encoder(
                ErrorResponse(
                    error="User already exist", error_kind=ErrorKind.user_exist
                )
            ),
        )

    create_user(
        r.app.state.db,
        User(
            email=body.email,
            password=hashlib.sha256(body.password.encode()).hexdigest().encode(),
            name=body.name,
        ),
    )

    return Response(status_code=200)


@router.post("/login")
def login(r: Request, body: LoginRequest):
    password_hash = fetch_user_password(r.app.state.db, body.email)
    if password_hash is None:
        return JSONResponse(
            status_code=404,
            content=jsonable_encoder(
                ErrorResponse(
                    error="No user registered for this email",
                    error_kind=ErrorKind.user_not_found,
                )
            ),
        )

    input_hash = str(hashlib.sha256(body.password.encode()).hexdigest())
    if password_hash == input_hash:
        k = r.app.state.keypair
        token = make_token(k, body.email)
        return JSONResponse(
            status_code=200,
            content=jsonable_encoder(LoginResponse(token=token)),
        )

    return JSONResponse(
        status_code=401,
        content=jsonable_encoder(
            ErrorResponse(error="Wrong password !", error_kind=ErrorKind.bad_password)
        ),
    )
