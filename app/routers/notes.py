from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from app.db.database import get_session
from app.models.note import Note
from app.schemas.note import NoteCreate, NoteRead
from app.utils import encrypt_note, decrypt_note, sign_note, verify_note_signature

# NEW: bring in the auth dependency
from app.auth.deps import get_current_user
from app.models.user import User  # or wherever your User model lives

router = APIRouter(prefix="/notes", tags=["notes"])


# @router.post("/", response_model=NoteRead, status_code=status.HTTP_201_CREATED)
# def create_note(
#     note: NoteCreate,
#     session: Session = Depends(get_session),
#     current_user: User = Depends(get_current_user),
# ):
#     # Assign ownership server-side; never trust client-provided user_id
#     encrypted_title = encrypt_note(note.title)
#     encrypted = encrypt_note(note.content)
#     encrypted_keywords = encrypt_note(note.keywords)
#     signature = sign_note(encrypted)

#     new_note = Note(
#         user_id=current_user.id,
#         encrypted_title=encrypted_title,
#         encrypted_content=encrypted,
#         encrypted_keywords=encrypted_keywords,
#         signature=signature,
#     )
#     session.add(new_note)
#     session.commit()
#     session.refresh(new_note)
#     return new_note

@router.post("/", response_model=NoteRead, status_code=status.HTTP_201_CREATED)
def create_note(
    note: NoteCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    encrypted_title = encrypt_note(note.title)
    encrypted = encrypt_note(note.content)
    encrypted_keywords = encrypt_note(note.keywords)
    
    encrypted_drawing = None
    if note.drawing:
        encrypted_drawing = encrypt_note(note.drawing)
    
    signature = sign_note(encrypted)

    new_note = Note(
        user_id=current_user.id,
        encrypted_title=encrypted_title,
        encrypted_content=encrypted,
        encrypted_keywords=encrypted_keywords,
        encrypted_drawing=encrypted_drawing,
        signature=signature,
    )
    session.add(new_note)
    session.commit()
    session.refresh(new_note)
    return new_note

@router.get("/search", response_model=List[NoteRead])
def search_notes(
    q: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Search notes by keywords and content for the current user only."""
    if not q.strip():
        return []

    # Scope to the current user
    notes = session.exec(
        select(Note).where(Note.user_id == current_user.id)
    ).all()

    matching_notes: list[Note] = []
    search_term = q.lower()

    for note in notes:
        try:
            decrypted_keywords = decrypt_note(note.encrypted_keywords)
            if search_term in decrypted_keywords.lower():
                matching_notes.append(note)
        except Exception:
            # Skip notes that can't be decrypted (e.g., corrupted)
            continue

    return matching_notes

@router.get("/{note_id}")
def read_note(
    note_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    note = session.exec(
        select(Note).where(Note.id == note_id, Note.user_id == current_user.id)
    ).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    if not verify_note_signature(note.encrypted_content, note.signature):
        raise HTTPException(status_code=400, detail="Invalid signature")

    decrypted_title = decrypt_note(note.encrypted_title)
    decrypted = decrypt_note(note.encrypted_content)
    decrypted_keywords = decrypt_note(note.encrypted_keywords)
    
    decrypted_drawing = None
    if note.encrypted_drawing:
        decrypted_drawing = decrypt_note(note.encrypted_drawing)
    
    return {
        "id": note.id,
        "title": decrypted_title,
        "content": decrypted,
        "keywords": decrypted_keywords,
        "drawing": decrypted_drawing,
        "created_at": note.created_at,
        "updated_at": note.updated_at
    }

# @router.get("/{note_id}")
# def read_note(
#     note_id: int,
#     session: Session = Depends(get_session),
#     current_user: User = Depends(get_current_user),
# ):
#     note = session.exec(
#         select(Note).where(Note.id == note_id, Note.user_id == current_user.id)
#     ).first()
#     if not note:
#         raise HTTPException(status_code=404, detail="Note not found")

#     if not verify_note_signature(note.encrypted_content, note.signature):
#         raise HTTPException(status_code=400, detail="Invalid signature")

#     decrypted_title = decrypt_note(note.encrypted_title)  # NEW
#     decrypted = decrypt_note(note.encrypted_content)
#     decrypted_keywords = decrypt_note(note.encrypted_keywords)
#     return {
#         "id": note.id,
#         "title": decrypted_title,  # NEW
#         "content": decrypted,
#         "keywords": decrypted_keywords,
#         "created_at": note.created_at,
#         "updated_at": note.updated_at
#     }


@router.get("/", response_model=List[NoteRead])
def get_all_notes(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # Return only the caller's notes
    notes = session.exec(
        select(Note).where(Note.user_id == current_user.id)
    ).all()
    return notes
