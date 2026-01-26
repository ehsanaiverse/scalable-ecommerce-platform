from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.src.db.database import Base, engine
from app.src.core.security import create_default_admin
from app.src.routes.user import router as user_routes
from app.src.routes.products import router as product_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    create_default_admin()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
def home():
    return {"message": "Welcome to the E-Commerce Platform API"}

app.include_router(user_routes, prefix="/user", tags=["User"])
app.include_router(product_routes)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)