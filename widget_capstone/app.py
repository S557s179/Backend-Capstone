from fastapi import FastAPI

app = FastAPI(
    title="FlyRank Embeddable Widget Platform",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "message": "FlyRank Embeddable Widget Platform API",
        "status": "running",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
