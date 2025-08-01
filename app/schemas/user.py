from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# Base para creación y edición
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None

# Para crear un nuevo usuario (POST)
class UserCreate(UserBase):
    pass

# Para actualizar un usuario (PUT)
class UserUpdate(UserBase):
    is_active: Optional[bool] = True

# Para mostrar un usuario (respuesta)
class UserOut(UserBase):
    id: int
    created_at: datetime
    is_active: bool

    class Config:
        orm_mode = True
