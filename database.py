import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Obtenemos la URL de las variables de entorno de Render
DATABASE_URL = os.getenv("DATABASE_URL")

# Si por alguna razón llega vacía o con formato postgres://, la ajustamos
if not DATABASE_URL:
    raise ValueError("La variable DATABASE_URL no está configurada en Render.")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
