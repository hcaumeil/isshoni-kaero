from pydantic import BaseModel
from fastapi import HTTPException, APIRouter, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import List
from error import ErrorResponse, ErrorKind
from datetime import datetime

router = APIRouter()


class Message(BaseModel):
    id: str
    content: str
    send_at: datetime
    sender: str

class MessageInput(BaseModel):
    content: str
    channel: str


def fetch_messages(db, channel):
    cur = db.cursor()
    cur.execute(
        "SELECT message_id, content, send_at, email FROM messages WHERE channel_id = %s ORDER BY send_at DESC",
        (channel,),
    )
    msgs = cur.fetchall()
    db.commit()
    cur.close()
    return [Message(id=msg[0], content=msg[1], send_at=msg[2], sender=msg[3]) for msg in msgs]


@router.get("/{channel_id}")
def get_messages(request: Request, channel_id: str):
    db = request.app.state.db
    user = request.state.user

    try:
        channels = fetch_messages(db, channel_id)
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

def create_message(db, message_input: MessageInput, sender: str):
    now = datetime.now()
    cur = db.cursor()
    cur.execute(
        "INSERT INTO messages (content, send_at, email, channel_id) VALUES (%s,%s,%s,%s) RETURNING message_id;", (message_input.content, now, sender, message_input.channel)
    )
    new_id = cur.fetchone()[0]

    db.commit()
    cur.close()
    return new_id


@router.post("/")
def message_channel(request: Request, message_input: MessageInput):
    db = request.app.state.db
    user = request.state.user

    try:
        msg_id = create_message(db, message_input, user)
        return JSONResponse(
            status_code=200, content=jsonable_encoder({"id": msg_id})
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
