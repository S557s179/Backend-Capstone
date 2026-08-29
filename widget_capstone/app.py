from fastapi import FastAPI

from database import Base, engine
from models import User, Widget
from routes import public_router, router, widget_router


app = FastAPI(
    title="FlyRank Embeddable Widget Platform",
    version="1.0.0",
)


Base.metadata.create_all(bind=engine)

app.include_router(router)
app.include_router(widget_router)
app.include_router(public_router)


@app.get("/")
def root():
    return {
        "message": "FlyRank Embeddable Widget Platform API",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "database": "connected",
    }
