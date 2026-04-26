from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/marketplace")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, 
                            autocommit=False, 
                            autoflush=False)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db    
    finally:
        db.close()
        
    