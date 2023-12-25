#! /usr/bin/python3
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from src.config import settings


class DbAPI:
    def __init__(self) -> None:
        db_url = f"{settings.db_dialect}://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
        self.engine = create_engine(db_url)
        self.session_factory = sessionmaker(bind=self.engine)

    @contextmanager
    def session_local(self) -> Iterator[Session]:
        session = self.session_factory()
        session.begin()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
