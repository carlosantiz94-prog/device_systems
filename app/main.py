from fastapi import FastAPI, Request
from app.routes import device_routes, loan_routes, user_loan_routes, user_routes

app = FastAPI(
    title="device_systems API",
    description="API REST para la gestion de usuarios, dispositivos y prestamos del sistema device_systems, con migraciones controladas mediante Alembic.",
    version="4.0.0",
    contact={"name": "Juan Camilo Sarrazola", "email": "camilo@correo.com"},
    openapi_tags=[
        {"name": "Users", "description": "Operaciones sobre usuarios y su historial de prestamos"},
        {"name": "Devices", "description": "Operaciones CRUD sobre dispositivos y su historial de prestamos"},
        {"name": "Loans", "description": "Gestion de prestamos de dispositivos"},
    ],
)


@app.middleware("http")
async def agregar_cabeceras_personalizadas(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-App-Name"] = "device_systems"
    response.headers["X-API-Version"] = "4.0.0"
    return response


app.include_router(user_routes.router)
app.include_router(user_loan_routes.router)
app.include_router(device_routes.router)
app.include_router(loan_routes.router)


@app.get("/", tags=["Raiz"])
def raiz():
    return {"mensaje": "Bienvenido a device_systems API v4.0. Visita /docs para ver la documentacion."}
