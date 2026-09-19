# app/dependencies/database_dependency.py
from app.database.connection import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()