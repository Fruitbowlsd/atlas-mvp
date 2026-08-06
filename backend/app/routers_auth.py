from fastapi import APIRouter, Cookie, HTTPException, Response
from pydantic import BaseModel

from . import auth

router = APIRouter(prefix="/api", tags=["auth"])


class LoginRequest(BaseModel):
    password: str


@router.post("/login")
def login(payload: LoginRequest, response: Response):
    if not auth.check_password(payload.password):
        raise HTTPException(status_code=401, detail="Falsches Passwort")
    auth.set_auth_cookie(response)
    return {"status": "ok"}


@router.get("/login/check")
def login_check(atlas_auth: str | None = Cookie(default=None)):
    return {"authenticated": auth.is_authenticated(atlas_auth)}
