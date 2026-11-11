from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    """Dependency: เปิด session ต่อหนึ่ง request แล้วปิดเมื่อจบ"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
