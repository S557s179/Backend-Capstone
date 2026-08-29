import secrets

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from database import get_db
from models import User, Widget
from schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    WidgetCreate,
    WidgetResponse,
)


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    existing_user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email is already registered",
        )

    hashed_password = hash_password(user_data.password)

    user = User(
        email=user_data.email,
        password_hash=hashed_password,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post("/login")
def login_user(
    user_data: UserLogin,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if not user or not verify_password(
        user_data.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    access_token = create_access_token(user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user


widget_router = APIRouter(
    prefix="/api/widgets",
    tags=["Widgets"],
)


@widget_router.post(
    "/",
    response_model=WidgetResponse,
    status_code=201,
)
def create_widget(
    widget_data: WidgetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    api_key = secrets.token_urlsafe(32)

    widget = Widget(
        user_id=current_user.id,
        name=widget_data.name,
        config=widget_data.config,
        api_key=api_key,
    )

    db.add(widget)
    db.commit()
    db.refresh(widget)

    return widget


@widget_router.get(
    "/",
    response_model=list[WidgetResponse],
)
def get_widgets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    widgets = (
        db.query(Widget)
        .filter(Widget.user_id == current_user.id)
        .all()
    )

    return widgets


@widget_router.get(
    "/{widget_id}",
    response_model=WidgetResponse,
)
def get_widget(
    widget_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    widget = (
        db.query(Widget)
        .filter(
            Widget.id == widget_id,
            Widget.user_id == current_user.id,
        )
        .first()
    )

    if widget is None:
        raise HTTPException(
            status_code=404,
            detail="Widget not found",
        )

    return widget


@widget_router.put(
    "/{widget_id}",
    response_model=WidgetResponse,
)
def update_widget(
    widget_id: int,
    widget_data: WidgetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    widget = (
        db.query(Widget)
        .filter(
            Widget.id == widget_id,
            Widget.user_id == current_user.id,
        )
        .first()
    )

    if widget is None:
        raise HTTPException(
            status_code=404,
            detail="Widget not found",
        )

    widget.name = widget_data.name
    widget.config = widget_data.config

    db.commit()
    db.refresh(widget)

    return widget


@widget_router.delete(
    "/{widget_id}",
    status_code=204,
)
def delete_widget(
    widget_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    widget = (
        db.query(Widget)
        .filter(
            Widget.id == widget_id,
            Widget.user_id == current_user.id,
        )
        .first()
    )

    if widget is None:
        raise HTTPException(
            status_code=404,
            detail="Widget not found",
        )

    db.delete(widget)
    db.commit()

    return None


public_router = APIRouter(
    prefix="/api/public",
    tags=["Public Widget"],
)


@public_router.get(
    "/widgets/{api_key}",
    response_model=WidgetResponse,
)
def get_public_widget(
    api_key: str,
    db: Session = Depends(get_db),
):
    widget = (
        db.query(Widget)
        .filter(Widget.api_key == api_key)
        .first()
    )

    if widget is None:
        raise HTTPException(
            status_code=404,
            detail="Widget not found",
        )

    return widget
