from enum import Enum
from pydantic import BaseModel


class ErrorKind(str, Enum):
    user_not_found: str = "USER_NOT_FOUND"
    user_exist: str = "USER_EXIST"
    bad_password: str = "BAD_PASSWORD"
    access_denied: str = "ACCESS_DENIED"
    internal_error: str = "INTERNAL_ERROR"
    not_found: str = "NOT_FOUND"
    conflict: str = "CONFLICT"


class ErrorResponse(BaseModel):
    error_kind: ErrorKind
    error: str
