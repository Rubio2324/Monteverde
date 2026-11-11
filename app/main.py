from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.controllers import (
    academico_controller,
    auditoria_controller,
    auth_controller,
    beneficiario_controller,
)
from app.core.errors import Conflicto, NoEncontrado, ReglaNegocio
from app.db.session import engine

app = FastAPI(title="Monteverde")


def _manejador(codigo: int):
    async def manejador(request: Request, exc: Exception):
        return JSONResponse(status_code=codigo, content={"detail": str(exc)})

    return manejador


app.add_exception_handler(NoEncontrado, _manejador(404))
app.add_exception_handler(Conflicto, _manejador(409))
app.add_exception_handler(ReglaNegocio, _manejador(422))

app.include_router(auth_controller.router, prefix="/api/v1")
app.include_router(beneficiario_controller.router, prefix="/api/v1")
app.include_router(academico_controller.router, prefix="/api/v1")
app.include_router(auditoria_controller.router, prefix="/api/v1")


@app.get("/health")
def health():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"estado": "ok", "base_de_datos": "conectada"}
