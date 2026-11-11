from fastapi import FastAPI
from sqlalchemy import text

from app.controllers import auth_controller, beneficiario_controller
from app.db.session import engine

app = FastAPI(title="Monteverde")

app.include_router(auth_controller.router, prefix="/api/v1")
app.include_router(beneficiario_controller.router, prefix="/api/v1")


@app.get("/health")
def health():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"estado": "ok", "base_de_datos": "conectada"}
