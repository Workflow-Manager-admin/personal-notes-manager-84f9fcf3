from pydantic import BaseModel, Field
from typing import Optional
import datetime

# PUBLIC_INTERFACE
class UserCreate(BaseModel):
    """Request schema for user registration."""
    username: str = Field(..., description="Username for the new user")
    password: str = Field(..., description="Password for the new user")


# PUBLIC_INTERFACE
class UserLogin(BaseModel):
    """Request schema for user login."""
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")


# PUBLIC_INTERFACE
class UserResponse(BaseModel):
    """Response schema for user information."""
    id: int
    username: str

    class Config:
        orm_mode = True


# PUBLIC_INTERFACE
class NoteBase(BaseModel):
    """Base schema for a note."""
    title: str = Field(..., description="Note title")
    content: Optional[str] = Field(None, description="Note content")


# PUBLIC_INTERFACE
class NoteCreate(NoteBase):
    """Request schema for note creation."""
    pass


# PUBLIC_INTERFACE
class NoteUpdate(NoteBase):
    """Request schema for note updating."""
    pass


# PUBLIC_INTERFACE
class NoteResponse(NoteBase):
    """Response schema for a note."""
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    owner_id: int

    class Config:
        orm_mode = True


# PUBLIC_INTERFACE
class Token(BaseModel):
    """JWT token response schema."""
    access_token: str
    token_type: str = "bearer"


# PUBLIC_INTERFACE
class TokenData(BaseModel):
    """JWT token data schema."""
    username: Optional[str] = None
