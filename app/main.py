# app/main.py
from fastapi import FastAPI, Request
from app.routes import user_routes

app = FastAPI(
    title="device_systems API",
    description="API REST para la gestion de usuarios del sistema device_systems",
    version="2.0.0",
    contact={"name": "Juan Camilo Sarrazola", "email": "camilo@correo.com"},
    openapi_tags=[{"name": "Users", "description": "Operaciones CRUD sobre usuarios"}],
)


@app.middleware("http")
async def agregar_cabeceras_personalizadas(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-App-Name"] = "device_systems"
    response.headers["X-API-Version"] = "2.0.0"
    return response


app.include_router(user_routes.router)


@app.get("/", tags=["Raiz"])
def raiz():
    return {"mensaje": "Bienvenido a device_systems API v2.0. Visita /docs para ver la documentacion."}