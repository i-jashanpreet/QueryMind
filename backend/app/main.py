from fastapi import FastAPI

app = FastAPI(title="QueryMind API")


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "QueryMind API is running"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
