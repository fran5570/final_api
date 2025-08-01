from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import status


from app.services import tmdb_service
from app import models
from app.database import SessionLocal
from app.schemas.movie import MovieCreate, MovieUpdate, MovieOut
from datetime import datetime

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Crear película manualmente
@router.post("/", response_model=MovieOut)
def create_movie(movie: MovieCreate, db: Session = Depends(get_db)):
    db_movie = models.Movie(**movie.dict())
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie

# Listar películas con filtros opcionales
@router.get("/", response_model=List[MovieOut])
def get_movies(
    skip: int = 0,
    limit: int = 10,
    title: Optional[str] = Query(None, description="Buscar por título"),
    db: Session = Depends(get_db)
):
    query = db.query(models.Movie)
    if title:
        query = query.filter(models.Movie.title.ilike(f"%{title}%"))
    return query.offset(skip).limit(limit).all()

# Obtener película por ID
@router.get("/{movie_id}", response_model=MovieOut)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    return movie

# Actualizar película
@router.put("/{movie_id}", response_model=MovieOut)
def update_movie(movie_id: int, updated_data: MovieUpdate, db: Session = Depends(get_db)):
    movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    
    for field, value in updated_data.dict(exclude_unset=True).items():
        setattr(movie, field, value)

    db.commit()
    db.refresh(movie)
    return movie

# Eliminar película
@router.delete("/{movie_id}")
def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    
    db.delete(movie)
    db.commit()
    return {"message": "Película eliminada"}


# Importar películas populares
@router.post("/import/popular", status_code=status.HTTP_201_CREATED)
def import_popular_movies(db: Session = Depends(get_db)):
    results = tmdb_service.fetch_popular_movies()
    count = 0

    for data in results:
        # Verifica si ya existe
        exists = db.query(models.Movie).filter(models.Movie.tmdb_id == data["id"]).first()
        if exists:
            continue

        # Convertir release_date (str → date)
        release_date_str = data.get("release_date")
        release_date = datetime.strptime(release_date_str, "%Y-%m-%d").date() if release_date_str else None

        # Crear instancia de película
        movie = models.Movie(
            tmdb_id=data["id"],
            title=data["title"],
            overview=data.get("overview"),
            release_date=release_date,  # ← corregido aquí
            genre_ids=str(data.get("genre_ids", [])),
            vote_average=data.get("vote_average"),
            vote_count=data.get("vote_count"),
            poster_path=data.get("poster_path"),
            backdrop_path=data.get("backdrop_path"),
        )
        db.add(movie)
        count += 1

    db.commit()
    return {"message": f"{count} películas importadas"}


# Importar película desde TMDB por ID
@router.post("/import/{tmdb_id}", response_model=MovieOut)
def import_movie_by_tmdb_id(tmdb_id: int, db: Session = Depends(get_db)):

    # Verificar si ya existe
    existing = db.query(models.Movie).filter(models.Movie.tmdb_id == tmdb_id).first()
    if existing:
        return existing  # ya está en la base

    data = tmdb_service.fetch_movie_by_id(tmdb_id)

    # Convertir string a date si es posible
    release_date_str = data.get("release_date")
    release_date = None
    if release_date_str:
        try:
            release_date = datetime.strptime(release_date_str, "%Y-%m-%d").date()
        except ValueError:
            release_date = None

    movie = models.Movie(
        tmdb_id=data["id"],
        title=data["title"],
        overview=data.get("overview"),
        release_date=release_date,
        genre_ids=str(data.get("genre_ids", [])),
        vote_average=data.get("vote_average"),
        vote_count=data.get("vote_count"),
        poster_path=data.get("poster_path"),
        backdrop_path=data.get("backdrop_path"),
    )

    db.add(movie)
    db.commit()
    db.refresh(movie)
    return movie

# Buscar películas por nombre en TMDB
@router.get("/search/{query}")
def search_movie_tmdb(query: str):
    results = tmdb_service.search_movies(query)
    return results
