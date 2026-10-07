from pydantic import BaseModel


class Token(BaseModel):
    """JWT token response returned after successful login."""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Payload decoded from a JWT token."""

    sub: str | None = None
