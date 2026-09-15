# device_systems

**Aprendiz:** Carlos Santis
**Actividad:** GA1-220501096-01-AA1-EV09 — FastAPI con SQLAlchemy: Persistencia de Datos y CRUD sobre Base de Datos

---

## Descripción de la API

`device_systems` evoluciona de la EV08 (CRUD completo, pero con los usuarios guardados en una simple lista en memoria) a la **v3.0**: ahora los usuarios se almacenan en una **base de datos real** (SQLite) mediante **SQLAlchemy**. Esto significa que los datos ya **no se pierden** al reiniciar el servidor — quedan guardados en el archivo `device_systems.db`.

La API sigue exponiendo el recurso `/users` con el CRUD completo (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`), pero ahora cada operación ejecuta consultas reales contra la base de datos, con restricciones (`constraints`) definidas directamente en el modelo.

## Tecnologías utilizadas

| Tecnología | Uso en el proyecto |
|---|---|
| **FastAPI** | Framework principal para construir la API |
| **Uvicorn** | Servidor ASGI que ejecuta la aplicación |
| **SQLAlchemy** | ORM: traduce clases de Python en tablas y filas de base de datos |
| **SQLite** | Motor de base de datos (un solo archivo, ideal para desarrollo) |
| **Pydantic v2** | Validación y serialización de datos de entrada/salida |
| **email-validator** | Validación del formato de correos (requerido por `EmailStr`) |

## Instalación de dependencias

```bash
git clone https://github.com/TU-USUARIO/device_systems.git
cd device_systems

python3 -m venv venv
source venv/bin/activate        # En Windows: venv\Scripts\activate

pip install -r requirements.txt
```

## Ejecutar el servidor

```bash
uvicorn app.main:app --reload
```

- API: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

Al arrancar por primera vez, se crea automáticamente el archivo `device_systems.db` (SQLite) con la tabla `users` ya lista — no hay que ejecutar ningún script aparte.

## Estructura del proyecto

```
device_systems/
├── app/
│   ├── main.py                        ← arranca la app, crea las tablas, metadatos Swagger
│   ├── database/
│   │   └── connection.py              ← engine, SessionLocal, Base declarativa
│   ├── models/
│   │   └── user_model.py              ← modelo SQLAlchemy (la tabla "users")
│   ├── schemas/
│   │   └── user_schema.py             ← UserCreate, UserUpdate, UserPatch, UserResponse
│   ├── routes/
│   │   └── user_routes.py             ← endpoints: GET, POST, PUT, PATCH, DELETE
│   ├── services/
│   │   └── user_service.py            ← lógica CRUD ejecutada contra la base de datos
│   └── dependencies/
│       ├── database_dependency.py     ← get_db(): entrega una sesión de BD por petición
│       └── user_dependencies.py       ← get_user_or_404(): reutilizada en 4 rutas
├── images/                            ← capturas: estructura, BD, Swagger, pruebas
├── requirements.txt
├── .gitignore                          ← ignora venv/, __pycache__/ y el .db generado
└── README.md
```

*(Captura de la estructura de carpetas en VS Code: se agrega en `images/`)*

## Configuración de la base de datos

`app/database/connection.py` define 3 piezas clave:

```python
DATABASE_URL = "sqlite:///./device_systems.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

- **`engine`**: la conexión real hacia el archivo SQLite.
- **`SessionLocal`**: una "fábrica" de sesiones — cada petición HTTP obtiene su propia sesión nueva.
- **`Base`**: la clase de la que heredan todos los modelos (tablas).

En `app/main.py`, la línea `Base.metadata.create_all(bind=engine)` es la que efectivamente crea la tabla `users` en el archivo `.db`, leyendo la definición desde `user_model.py`.

## Diferencia entre modelo SQLAlchemy y schema Pydantic

Esta es la distinción más importante de esta actividad — son **dos clases distintas, con propósitos distintos**, aunque ambas describan "un usuario":

| | Modelo SQLAlchemy (`app/models/user_model.py`) | Schema Pydantic (`app/schemas/user_schema.py`) |
|---|---|---|
| ¿Qué representa? | Una **tabla** de la base de datos | La **forma de los datos** que entran/salen por HTTP |
| ¿De qué hereda? | `Base` (de SQLAlchemy) | `BaseModel` (de Pydantic) |
| ¿Qué hace con los datos? | Los **guarda y consulta** en SQLite | Los **valida y serializa** (JSON ↔ Python) |
| ¿Sabe algo de HTTP? | No, nunca ve una petición | Sí, es lo que FastAPI usa en el `body` y la respuesta |
| ¿Sabe algo de SQL? | Sí (`Column`, `nullable`, `unique`) | No, nunca genera una consulta |
| Ejemplo de un campo | `email = Column(String, unique=True, nullable=False)` | `email: EmailStr` |

```python
# app/models/user_model.py — DESCRIBE LA TABLA
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    ...

# app/schemas/user_schema.py — DESCRIBE LA ENTRADA/SALIDA DE LA API
class UserCreate(BaseModel):
    email: EmailStr
    ...
```

**¿Por qué no usar uno solo?** Porque cumplen reglas distintas. El modelo necesita reglas de *base de datos* (`unique=True` evita duplicados a nivel de tabla, `nullable=False` es una restricción de columna). El schema necesita reglas de *validación de entrada* (`EmailStr` verifica el formato, `Literal[...]` restringe valores permitidos) — y además, el schema de **salida** (`UserResponse`) no debería exponer necesariamamente los mismos campos que tiene la tabla (por ejemplo, si hubiera una contraseña en el modelo, jamás debería aparecer en `UserResponse`).

La conexión entre ambos ocurre en el servicio: `user_service.crear_usuario()` recibe un diccionario (validado por el schema `UserCreate`) y crea un objeto `User` (el modelo) con esos datos, para guardarlo en la base de datos.

## El modelo SQLAlchemy (constraints aplicados)

```python
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    role = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

| Campo | Tipo | Restricción |
|---|---|---|
| `id` | `Integer` | `primary_key=True` (clave única autogenerada) |
| `name` | `String` | `nullable=False` (obligatorio) |
| `email` | `String` | `unique=True, nullable=False` (único y obligatorio) |
| `role` | `String` | `nullable=False` (obligatorio) |
| `is_active` | `Boolean` | `default=True` |
| `created_at` | `DateTime` | `default=datetime.utcnow` (se asigna sola al crear) |

## Tabla de endpoints

| Operación | Método | Ruta | Código esperado |
|---|---|---|---|
| Listar usuarios | GET | `/users` | `200 OK` |
| Filtrar/ordenar | GET | `/users?role=admin` / `?is_active=true` / `?order_by=name` | `200 OK` |
| Consultar usuario | GET | `/users/{user_id}` | `200 OK` / `404 Not Found` |
| Crear usuario | POST | `/users` | `201 Created` / `400` / `422` |
| Actualizar completo | PUT | `/users/{user_id}` | `200 OK` / `404` / `400` |
| Actualizar parcial | PATCH | `/users/{user_id}` | `200 OK` / `404` / `400` |
| Eliminar usuario | DELETE | `/users/{user_id}` | `200 OK` / `404 Not Found` |

## Schemas Pydantic

```python
class UserBase(BaseModel):
    name: str = Field(..., min_length=3)
    email: EmailStr
    role: Literal["admin", "support", "user"]
    is_active: bool = True

class UserCreate(UserBase): pass
class UserUpdate(UserBase): pass

class UserPatch(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[Literal["admin", "support", "user"]] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
```

`from_attributes=True` es la pieza clave que conecta ambos mundos: le permite a `UserResponse` construirse directamente a partir de un objeto `User` (SQLAlchemy), leyendo sus atributos como si fuera un diccionario.

## Ejemplos de peticiones y respuestas

### POST /users

```bash
curl -X POST http://127.0.0.1:8000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Ana Torres", "email": "ana@correo.com", "role": "admin", "is_active": true}'
```
```json
{"name": "Ana Torres", "email": "ana@correo.com", "role": "admin", "is_active": true, "id": 1, "created_at": "2026-09-12T15:51:40.123456"}
```
`201 Created` — nótese que `id` y `created_at` los genera la base de datos, no se envían en la petición.

### GET /users?order_by=name

```bash
curl "http://127.0.0.1:8000/users?order_by=name"
```
Devuelve todos los usuarios ordenados alfabéticamente por `name`.

### PUT /users/2

```bash
curl -X PUT http://127.0.0.1:8000/users/2 \
  -H "Content-Type: application/json" \
  -d '{"name": "Luis Ramirez G.", "email": "luisg@correo.com", "role": "admin", "is_active": false}'
```
`200 OK` — reemplazo completo.

### PATCH /users/3

```bash
curl -X PATCH http://127.0.0.1:8000/users/3 -H "Content-Type: application/json" -d '{"role": "admin"}'
```
`200 OK` — solo cambia `role`.

### DELETE /users/1

```bash
curl -X DELETE http://127.0.0.1:8000/users/1
```
`200 OK` — `{"detail": "Usuario con id 1 eliminado correctamente"}`. Una consulta posterior a `GET /users/1` confirma `404 Not Found`, es decir, el registro se eliminó de verdad de la base de datos.

## Códigos de estado usados

| Código | Cuándo se usa |
|---|---|
| `200 OK` | Operación exitosa (GET, PUT, PATCH, DELETE) |
| `201 Created` | Usuario creado exitosamente (POST) |
| `400 Bad Request` | Correo duplicado, o PATCH sin ningún campo |
| `404 Not Found` | El usuario solicitado no existe |
| `422 Unprocessable Entity` | Datos inválidos según Pydantic |

## Evidencia de pruebas (las 11 de la Fase 12), verificadas

Todas estas pruebas se ejecutaron y confirmaron contra la base de datos real (no en memoria):

| # | Prueba | Resultado |
|---|---|---|
| 1 | Crear un usuario válido | `201 Created`, con `id=1` y `created_at` asignados por la BD |
| 2 | Crear con email repetido | `400 Bad Request` |
| 3 | Listar usuarios | `200 OK`, 3 usuarios devueltos |
| 4 | Consultar usuario por ID | `200 OK` |
| 5 | Consultar usuario inexistente | `404 Not Found` |
| 6 | Filtrar por rol | `200 OK`, solo los del rol solicitado |
| 7 | Filtrar por activos | `200 OK`, solo `is_active=true` |
| 8 | Actualizar completo (PUT) | `200 OK`, todos los campos reemplazados |
| 9 | Actualizar parcial (PATCH) | `200 OK`, solo el campo enviado cambia |
| 10 | Eliminar usuario (DELETE) | `200 OK` |
| 11 | Confirmar que el eliminado ya no existe | `404 Not Found` al volver a consultarlo |

*(Capturas de Postman/Swagger de cada una: pendientes de agregar en `images/`)*

## Evidencia de errores controlados

| Escenario | Código | Respuesta |
|---|---|---|
| Usuario inexistente | `404` | `{"detail": "Usuario no encontrado"}` |
| Correo duplicado (POST/PUT/PATCH) | `400` | `{"detail": "Ya existe un usuario registrado con el correo ..."}` |
| PATCH sin campos | `400` | `{"detail": "Debes enviar al menos un campo para actualizar"}` |
| Nombre corto / email inválido / rol no permitido | `422` | Error detallado de Pydantic por campo |


## Reflexión final sobre la importancia de la persistencia

el aspecto más enriquecedor de esta práctica fue comprender la **separación de responsabilidades entre Modelos (SQLAlchemy) y Schemas (Pydantic)**. Entender que el modelo define la estructura física y las reglas de almacenamiento en la base de datos, mientras que los esquemas definen el contrato de entrada/salida HTTP y la validación de negocio, es clave para construir arquitecturas escalables, seguras y mantenibles. Esta distinción evita exponer datos sensibles, previene errores de tipado antes de llegar a la base de datos y facilita la evolución del software a futuro.


