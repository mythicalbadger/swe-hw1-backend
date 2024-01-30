"""Router for user endpoints."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session

from src.database import get_session
from src.models.users import User
from src.schemas.users import UserCreate
from src.services.users import UserService
from src.utils import hasher

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get("/api/get-current-user", response_model=User, tags=["users"])
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Session = Depends(get_session),
) -> User:
    """
    Get the current user.

    :param token: The authentication token.
    :param session: The database session.
    :return: The current user object.
    """
    user = UserService(session).get_user_by_username(username=token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


@router.post(
    "/register",
    tags=["users"],
    status_code=status.HTTP_201_CREATED,
    response_model=User,
)
async def register(
    user_info: UserCreate, session: Session = Depends(get_session)
) -> User:
    """
    Register a new user.

    :param user_info: User info object.
    :param session: Database session.
    :return: The created user object.
    """
    if (
        UserService(session).get_user_by_username(username=user_info.username)
        is not None
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Username already taken."
        )

    user: User = User(
        username=user_info.username,
        full_name=user_info.full_name,
        hashed_password=hasher.hash(user_info.password),
    )
    user = UserService(session).create_user(user=user)

    return user


@router.post("/token", tags=["users"], status_code=status.HTTP_200_OK)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(get_session),
) -> dict:
    """
    Log in a user.

    :param form_data: The form data containing the username and password.
    :param session: The database session.
    :return: The authentication token.
    """
    user: User = UserService(session).get_user_by_username(username=form_data.username)
    if not user or not hasher.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
        )

    return {"access_token": user.username, "token_type": "bearer"}
