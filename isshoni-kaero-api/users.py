from pydantic import BaseModel
from fastapi import HTTPException, Request, APIRouter
from fastapi.responses import Response, JSONResponse
from fastapi.encoders import jsonable_encoder
from error import ErrorResponse, ErrorKind
import hashlib

router = APIRouter()


class User(BaseModel):
    email: str
    password: str
    name: str


class PasswordUpdate(BaseModel):
    new_password: str


def create_user(db, user: User):
    cur = db.cursor()
    cur.execute(
        "INSERT INTO users (email, password, name) VALUES (%s, %s, %s)",
        (
            user.email,
            user.password,
            user.name,
        ),
    )

    db.commit()
    cur.close()


def users_emails(db):
    cur = db.cursor()
    cur.execute("SELECT email FROM users;")

    emails = cur.fetchall()
    res = [e[0] for e in emails]

    db.commit()
    cur.close()

    return res


def fetch_user_password(db, email: str):
    cur = db.cursor()
    cur.execute("SELECT password FROM users WHERE email=%s;", (email,))

    res = cur.fetchone()

    if res != None:
        res = res[0]

    db.commit()
    cur.close()

    return res


def fetch_user_role(db, email: str):
    cur = db.cursor()
    cur.execute("SELECT role FROM users WHERE email=%s;", (email,))

    res = cur.fetchone()

    if res != None:
        res = res[0]

    db.commit()
    cur.close()

    return res


# Check if a user with the given email exists in the database.
# Args:
# db: The database connection.
# email: The email of the user to check.
# Returns: True if the user exists, False otherwise.
def check_user_exists(db, email: str) -> bool:
    cur = db.cursor()
    try:
        cur.execute("SELECT 1 FROM users WHERE email = %s;", (email,))
        return cur.fetchone() is not None
    finally:
        cur.close()


@router.get("/")
def get_users(r: Request):
    # Only admin can view all users
    if r.state.user != "admin@example.com":
        return JSONResponse(
            status_code=403,
            content=jsonable_encoder(
                ErrorResponse(
                    error_kind=ErrorKind.user_not_found,
                    error="Only admin can view all users.",
                )
            ),
        )

    db = r.app.state.db
    cur = db.cursor()
    try:
        # Getting all the infos about a user
        cur.execute("SELECT email, name FROM users;")
        users = cur.fetchall()
        # Putting all the infos into a list
        users_list = [
            {
                "email": user[0],
                "name": user[1],
            }
            for user in users
        ]
        #  Return list to a json format
        return JSONResponse(status_code=200, content=jsonable_encoder(users_list))
    except Exception as e:
        db.rollback()
        return JSONResponse(
            status_code=500,
            content=jsonable_encoder(
                ErrorResponse(error_kind=ErrorKind.bad_password, error=str(e))
            ),
        )
    finally:
        cur.close()


@router.patch("/{email}/password")
async def patch_password(r: Request, email: str, password_data: PasswordUpdate):
    # User can only modify his own password
    if r.state.user != email:
        return JSONResponse(
            status_code=403,
            content=jsonable_encoder(
                ErrorResponse(
                    error_kind=ErrorKind.user_not_found,
                    error="You can only update your own password.",
                )
            ),
        )

    db = r.app.state.db
    cur = db.cursor()

    try:
        # Update the password
        new_password_hash = hashlib.sha256(
            password_data.new_password.encode()
        ).hexdigest()
        cur.execute(
            "UPDATE users SET password = %s WHERE email = %s;",
            (new_password_hash, email),
        )
        db.commit()

        return JSONResponse(
            status_code=200,
            content=jsonable_encoder({"message": "Password updated successfully"}),
        )
    except Exception as e:
        db.rollback()
        return JSONResponse(
            status_code=500,
            content=jsonable_encoder(
                ErrorResponse(error_kind=ErrorKind.bad_password, error=str(e))
            ),
        )
    finally:
        cur.close()


@router.delete("/{email}")
def delete_user(r: Request, email: str):
    user_email = r.state.user
    user_role = r.state.role

    # Request by the user itself or admin only
    if r.state.user != email and r.state.role != "admin":
        return JSONResponse(
            status_code=403,
            content=jsonable_encoder(
                ErrorResponse(
                    error_kind=ErrorKind.user_not_found,
                    error="You can only delete your own account or perform this action as an admin.",
                )
            ),
        )
    db = r.app.state.db
    cur = db.cursor()

    try:
        if not check_user_exists(db, email):
            return JSONResponse(
                status_code=404,
                content=jsonable_encoder(
                    ErrorResponse(
                        error_kind=ErrorKind.user_not_found,
                        error=f"No user found with email {email}.",
                    )
                ),
            )
        # We delete the user
        cur.execute("DELETE FROM users WHERE email = %s;", (email,))
        db.commit()

        return JSONResponse(
            status_code=200,
            content=jsonable_encoder({"message": "User deleted successfully"}),
        )
    except Exception as e:
        db.rollback()
        return JSONResponse(
            status_code=500,
            content=jsonable_encoder(
                ErrorResponse(error_kind=ErrorKind.bad_password, error=str(e))
            ),
        )
    finally:
        cur.close()
