#! /usr/bin/python3
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from src.config import settings


class DBClientError(Exception):
    ...


class DbAPI:
    def __init__(self) -> None:
        if settings.db_dialect == "sqlite":
            db_url_suffix = f"/{settings.DB_FILE}"
        else:
            db_url_suffix = (
                f"{settings.DB_USER}:{settings.DB_PASSWORD}"
                f"@{settings.DB_HOST}:{settings.DB_PORT}"
                f"/{settings.DB_NAME}"
            )
        db_url = f"{settings.db_dialect}://{db_url_suffix}"
        self.engine = create_engine(db_url)
        self.session_factory = sessionmaker(bind=self.engine)

    @contextmanager
    def session_local(self) -> Iterator[Session]:
        session = self.session_factory()
        session.begin()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise DBClientError("There was a problem connecting to the DB") from e
        finally:
            session.close()
