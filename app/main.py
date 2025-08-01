from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from app.database import Base, engine
from app.routers import users, movies

# Crea las tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Instancia de FastAPI
app = FastAPI(title="Final Programación - API Películas")

# Incluir routers
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(movies.router, prefix="/movies", tags=["Movies"])
