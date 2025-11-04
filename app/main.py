from fastapi import FastAPI
from app.db.database import init_db
from app.routers import auth
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, allow all origins. For production, specify your frontend URL(s).
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def read_root():
    return {"message": "Encrypted Notes App is running!"}

from app.routers import notes
app.include_router(notes.router)
