from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

# Base reutilizable
class MovieBase(BaseModel):
    tmdb_id: Optional[int] = None
    title: str
    overview: Optional[str] = None
    release_date: Optional[date] = None
    genre_ids: Optional[str] = None
    vote_average: Optional[float] = None
    vote_count: Optional[int] = None
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None

# Para crear una película
class MovieCreate(MovieBase):
    pass

# Para actualizar una película
class MovieUpdate(MovieBase):
    pass

# Para mostrar una película (respuesta)
class MovieOut(MovieBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
