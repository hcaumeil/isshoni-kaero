from pydantic import BaseModel
from fastapi import HTTPException, APIRouter, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import List
from error import ErrorResponse, ErrorKind

router = APIRouter()


class Channel(BaseModel):
    id: str
    name: str


class ChannelInput(BaseModel):
    name: str
    members: List[str]


def fetch_channels(db, user):
    cur = db.cursor()
    cur.execute(
        "SELECT ch.channel_id, ch.name FROM channels AS ch JOIN channels_members AS cm ON cm.channel_id=ch.channel_id WHERE cm.email = %s;",
        (user,),
    )
    channels = cur.fetchall()
    db.commit()
    cur.close()
    return [Channel(id=ch[0], name=ch[1]) for ch in channels]


@router.get("/")
def get_channels(request: Request):
    db = request.app.state.db
    user = request.state.user

    try:
        channels = fetch_channels(db, user)
        return JSONResponse(jsonable_encoder(channels))
    except Exception as e:
        raise HTTPException(
            500,
            jsonable_encoder(
                ErrorResponse(
                    error="Internal error: " + str(e),
                    error_kind=ErrorKind.internal_error,
                )
            ),
        )


def create_channel(db, channel: ChannelInput):
    cur = db.cursor()
    cur.execute(
        "INSERT INTO channels (name) VALUES (%s) RETURNING channel_id;", (channel.name,)
    )
    new_id = cur.fetchone()[0]

    for m in channel.members:
        cur.execute(
            "INSERT INTO channels_members (channel_id, email) VALUES (%s,%s) RETURNING channel_id;",
            (new_id, m),
        )

    db.commit()
    cur.close()
    return new_id


@router.post("/")
def add_channel(request: Request, channel_input: ChannelInput):
    db = request.app.state.db
    user = request.state.user

    if not user in channel_input.members:
        channel_input.members.append(user)

    try:
        channel_id = create_channel(db, channel_input)
        return JSONResponse(
            status_code=200, content=jsonable_encoder({"id": channel_id})
        )
    except Exception as e:
        raise HTTPException(
            500,
            jsonable_encoder(
                ErrorResponse(
                    error="Internal error: " + str(e),
                    error_kind=ErrorKind.internal_error,
                )
            ),
        )
