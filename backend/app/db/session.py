from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker


def make_engine(url: str):
    engine = create_engine(
        url,
        pool_pre_ping=True,
        connect_args=({"check_same_thread": False} if url.startswith("sqlite") else {}),
    )
    if engine.dialect.name == "sqlite":

        @event.listens_for(engine, "connect")
        def enable_fk(connection, _):
            connection.execute("PRAGMA foreign_keys=ON")

    return engine


def make_sessions(engine):
    return sessionmaker(engine, expire_on_commit=False)
