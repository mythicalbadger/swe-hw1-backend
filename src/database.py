"""This module contains the database connection logic."""
import os

from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, create_engine, select

from src.models.users import User
from src.utils import hasher

load_dotenv()

DATABASE_USER = os.getenv("DATABASE_USER", "root")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "hardpass")
DATABASE_DB = os.getenv("DATABASE_DB", "leave_request")
DATABASE_PORT = os.getenv("DATABASE_PORT", "3306")

DATABASE_URL = (
    f"mysql://{DATABASE_USER}:{DATABASE_PASSWORD}"
    f"@localhost:{DATABASE_PORT}/{DATABASE_DB}"
)

engine = create_engine(DATABASE_URL)

SQLModel.metadata.create_all(engine)

with Session(engine) as session:
    query = select(User).where(User.username == "admin")
    result = session.exec(query).one_or_none()

    if result is None:
        admin = User(
            username="admin",
            hashed_password=hasher.hash("bigchungus"),
            full_name="Admin Istrator",
            is_admin=True,
        )
        session.add(admin)
        session.commit()


def get_session() -> Session:
    """
    Get a database session.

    :return: database session.
    """
    with Session(engine) as session:
        yield session
