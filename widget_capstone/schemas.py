from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class WidgetCreate(BaseModel):
    name: str
    config: dict


class WidgetResponse(BaseModel):
    id: int
    name: str
    config: dict
    api_key: str

    class Config:
        from_attributes = True
