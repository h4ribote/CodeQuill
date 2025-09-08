import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

os.makedirs("static/articles", exist_ok=True)

SQLALCHEMY_DATABASE_URL = "sqlite:///./blog.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    with open('schema.sql', 'r') as f:
        schema = f.read()
    with engine.connect() as connection:
        for statement in schema.split(';'):
            if statement.strip():
                connection.execute(text(statement))
        connection.commit()
    print("Database initialized successfully.")
