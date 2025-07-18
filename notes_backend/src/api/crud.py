from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
from typing import Optional
from . import models, schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# PUBLIC_INTERFACE
def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """Get user by username."""
    return db.query(models.User).filter(models.User.username == username).first()


# PUBLIC_INTERFACE
def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Create a new user."""
    hashed_pw = pwd_context.hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_pw)
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
    except IntegrityError:
        db.rollback()
        return None
    return db_user


# PUBLIC_INTERFACE
def verify_password(plain_password, hashed_password):
    """Verify plaintext password against hashed value."""
    return pwd_context.verify(plain_password, hashed_password)


# PUBLIC_INTERFACE
def authenticate_user(db: Session, username: str, password: str):
    """Authenticate a user by username and password."""
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


# PUBLIC_INTERFACE
def get_notes(db: Session, user_id: int):
    """Get all notes for a user."""
    return db.query(models.Note).filter(models.Note.owner_id == user_id).order_by(models.Note.updated_at.desc()).all()


# PUBLIC_INTERFACE
def get_note(db: Session, note_id: int, user_id: int):
    """Get a single note by ID (owned by user)."""
    return db.query(models.Note).filter(models.Note.id == note_id, models.Note.owner_id == user_id).first()


# PUBLIC_INTERFACE
def create_note(db: Session, note: schemas.NoteCreate, user_id: int):
    """Create a new note for a user."""
    db_note = models.Note(title=note.title, content=note.content, owner_id=user_id)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


# PUBLIC_INTERFACE
def update_note(db: Session, note_id: int, note: schemas.NoteUpdate, user_id: int):
    """Update an existing note."""
    db_note = get_note(db, note_id, user_id)
    if not db_note:
        return None
    db_note.title = note.title
    db_note.content = note.content
    db_note.updated_at = models.datetime.datetime.utcnow()
    db.commit()
    db.refresh(db_note)
    return db_note


# PUBLIC_INTERFACE
def delete_note(db: Session, note_id: int, user_id: int):
    """Delete a note."""
    db_note = get_note(db, note_id, user_id)
    if not db_note:
        return False
    db.delete(db_note)
    db.commit()
    return True
