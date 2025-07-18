from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from . import models, schemas, crud, database, auth

load_dotenv()
database.init_db()

app = FastAPI(
    title="Notes Manager API",
    description="API backend for personal notes manager app.",
    version="1.0.0",
    openapi_tags=[
        {"name": "auth", "description": "User registration and authentication"},
        {"name": "notes", "description": "Note operations"},
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["health"])
def health_check():
    """Health check endpoint for API status."""
    return {"message": "Healthy"}

# === AUTH ENDPOINTS ===

# PUBLIC_INTERFACE
@app.post("/api/register", response_model=schemas.UserResponse, summary="Register user", tags=["auth"])
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    """
    Register a new user.
    """
    db_user = crud.create_user(db, user)
    if not db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return db_user

# PUBLIC_INTERFACE
@app.post("/api/login", response_model=schemas.Token, summary="Login user and issue JWT", tags=["auth"])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    """
    Login a user and return JWT token.
    """
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# === NOTES CRUD ENDPOINTS ===

# PUBLIC_INTERFACE
@app.get("/api/notes", response_model=list[schemas.NoteResponse], summary="Get all notes", tags=["notes"])
def list_notes(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    """
    Retrieve all notes for the authenticated user.
    """
    notes = crud.get_notes(db, current_user.id)
    return notes

# PUBLIC_INTERFACE
@app.post("/api/notes", response_model=schemas.NoteResponse, status_code=201, summary="Create note", tags=["notes"])
def create_note(note: schemas.NoteCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    """
    Create a new note.
    """
    db_note = crud.create_note(db, note, current_user.id)
    return db_note

# PUBLIC_INTERFACE
@app.put("/api/notes/{note_id}", response_model=schemas.NoteResponse, summary="Update note", tags=["notes"])
def update_note(note_id: int, note: schemas.NoteUpdate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    """
    Update an existing note.
    """
    updated_note = crud.update_note(db, note_id, note, current_user.id)
    if not updated_note:
        raise HTTPException(status_code=404, detail="Note not found")
    return updated_note

# PUBLIC_INTERFACE
@app.delete("/api/notes/{note_id}", status_code=204, summary="Delete note", tags=["notes"])
def delete_note(note_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    """
    Delete a note.
    """
    deleted = crud.delete_note(db, note_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Note not found")
    return
