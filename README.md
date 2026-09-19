# device_systems

**Aprendiz:** Carlos Santis
**Actividad:** GA1-220501096-01-AA1-EV09 — FastAPI con SQLAlchemy: Persistencia de Datos y CRUD sobre Base de Datos

---

##  Descripción de la API

`device_systems` evoluciona  (CRUD completo, pero con los usuarios guardados en una simple lista en memoria) a la **v3.0**: ahora los usuarios se almacenan en una **base de datos real** (SQLite) mediante **SQLAlchemy**. Esto significa que los datos ya **no se pierden** al reiniciar el servidor — quedan guardados en el archivo `device_systems.db`.

La API sigue exponiendo el recurso `/users` con el CRUD completo (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`), pero ahora cada operación ejecuta consultas reales contra la base de datos, con restricciones (`constraints`) definidas directamente en el modelo.


## 🗂️ Estructura del proyecto

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
├── images/evo9/                       ← capturas de esta entrega
├── requirements.txt
├── .gitignore                          ← ignora venv/, __pycache__/ y el .db generado
└── README.md
```

📸 *Estructura real del proyecto en VS Code, con el servidor levantado en la terminal:*

![Estructura del proyecto y servidor corriendo](imagenes/evo9/2026-09-16_08h30_53.png)

## 🗄️ Configuración y evidencia de la base de datos

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

En `app/main.py`, la línea `Base.metadata.create_all(bind=engine)` es la que efectivamente crea la tabla `users` en el archivo `device_systems.db`, leyendo la definición desde `user_model.py`.

La prueba real de que la persistencia funciona no es solo que el archivo `.db` exista, sino que los datos sobreviven entre peticiones y reinicios: se creó un usuario por `POST`, se reinició el servidor y al volver a consultarlo con `GET` seguía ahí — algo que con la lista en memoria de la EV08 era imposible.

## 🔄 Diferencia entre modelo SQLAlchemy y schema Pydantic

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

**¿Por qué no usar uno solo?** Porque cumplen reglas distintas. El modelo necesita reglas de *base de datos* (`unique=True` evita duplicados a nivel de tabla, `nullable=False` es una restricción de columna). El schema necesita reglas de *validación de entrada* (`EmailStr` verifica el formato, `Literal[...]` restringe valores permitidos) — y además, el schema de **salida** (`UserResponse`) no debería exponer necesariamente los mismos campos que tiene la tabla (por ejemplo, si hubiera una contraseña en el modelo, jamás debería aparecer en `UserResponse`).

La conexión entre ambos ocurre en el servicio: `user_service.crear_usuario()` recibe un diccionario (ya validado por el schema `UserCreate`) y crea un objeto `User` (el modelo) con esos datos, para guardarlo en la base de datos.

### El modelo SQLAlchemy (constraints aplicados)

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

### Schemas Pydantic

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

## 📖 Documentación interactiva (Swagger UI)

FastAPI genera automáticamente la documentación a partir de las rutas, los schemas y los modelos. Ahí se ven de un vistazo los 6 endpoints de `/users` más la raíz `/`:

![Swagger UI - vista general de los endpoints](imagenes/evo9/swagger_general.png)

## 📋 Tabla de endpoints

| Operación | Método | Ruta | Código esperado |
|---|---|---|---|
| Listar usuarios | GET | `/users` | `200 OK` |
| Filtrar/ordenar | GET | `/users?role=admin` / `?is_active=true` / `?order_by=name` | `200 OK` |
| Consultar usuario | GET | `/users/{user_id}` | `200 OK` / `404 Not Found` |
| Crear usuario | POST | `/users` | `201 Created` / `400` / `422` |
| Actualizar completo | PUT | `/users/{user_id}` | `200 OK` / `404` / `400` |
| Actualizar parcial | PATCH | `/users/{user_id}` | `200 OK` / `404` / `400` |
| Eliminar usuario | DELETE | `/users/{user_id}` | `200 OK` / `404 Not Found` |

##  Evidencia de prueba de cada endpoint

Todas estas pruebas se ejecutaron con Postman contra el servidor real, verificando que la información quedara efectivamente persistida en la base de datos:

**Crear usuario (`POST /users`)** — `201 Created`, con `id` y `created_at` asignados por la base de datos:
![POST exitoso](imagenes/evo9/postman_post_exitoso.png)

**Listar usuarios (`GET /users`)** — `200 OK`:
![GET listar usuarios](imagenes/evo9/postman_get_users.png)

**Filtrar por rol (`GET /users?role=admin`)** — `200 OK`, solo los usuarios del rol solicitado:
![Filtro por rol](imagenes/evo9/postman_filtro_rol.png)

**Filtrar por activos (`GET /users?is_active=true`)** — `200 OK`:
![Filtro por activos](imagenes/evo9/postman_filtro_activos.png)

**Actualizar completo (`PUT /users/{id}`)** — `200 OK`, todos los campos reemplazados:
![PUT exitoso](imagenes/evo9/postman_put_exitoso.png)

**Actualizar parcial (`PATCH /users/{id}`)** — `200 OK`, solo cambia el campo enviado:
![PATCH parcial](imagenes/evo9/postman_patch_parcial.png)

**Eliminar usuario (`DELETE /users/{id}`)** — `200 OK`:
![DELETE exitoso](imagenes/evo9/postman_delete_exitoso.png)

**Confirmación de la eliminación** — al volver a consultar el mismo id, responde `404 Not Found`, es decir, el registro se borró de verdad de la base de datos y no solo de la respuesta:
![Confirmación DELETE - 404](imagenes/evo9/postman_delete_confirmado_404.png)

## ⚠️ Evidencia de errores controlados

| Escenario | Código | Captura |
|---|---|---|
| Usuario inexistente (`GET /users/999`) | `404 Not Found` | ![404 usuario no encontrado](imagenes/evo9/postman_get_users_404.png) |
| Correo duplicado (`POST /users`) | `400 Bad Request` | ![400 correo duplicado](imagenes/evo9/postman_post_duplicado_400.png) |
| PATCH sin ningún campo enviado | `400 Bad Request` | ![400 patch vacío](imagenes/evo9/postman_patch_vacio_400.png) |
| Datos inválidos — nombre corto / email mal formado / rol no permitido | `422 Unprocessable Entity` | ![422 datos inválidos](imagenes/evo9/postman_post_invalido_422.png) |

En ningún caso la API se cae o responde con un error genérico de servidor: cada escenario devuelve un código HTTP coherente y un mensaje claro sobre qué salió mal, gracias a la combinación de las validaciones de Pydantic (schemas) y las reglas de negocio explícitas en `user_service.py` y `user_routes.py`.

##  Reflexión final sobre la importancia de la persistencia

Pasar de una lista en memoria a una base de datos real con SQLAlchemy cambió por completo la forma en que pienso esta API. Con la lista, "funcionar" era una ilusión parcial: mientras el servidor seguía encendido todo se veía bien, pero bastaba un `--reload`, un error o simplemente apagar la máquina para que toda la información desapareciera sin dejar rastro. Eso es inaceptable en cualquier sistema que alguien vaya a usar de verdad — nadie confiaría en una API de inventario, usuarios o dispositivos que se "olvida" de todo cada vez que se reinicia.

Trabajar con SQLAlchemy también obligó a pensar en los datos de una forma distinta. Ya no basta con que el dato "quepa" en una variable de Python; ahora tiene que respetar restricciones reales de base de datos, como que el correo sea único (`unique=True`) o que ciertos campos nunca puedan quedar vacíos (`nullable=False`). Eso llevó a un aprendizaje que considero el núcleo de esta entrega: **el modelo y el schema no son lo mismo, aunque se parezcan**. El modelo protege la integridad de lo que se guarda; el schema protege la calidad de lo que entra y controla lo que se muestra hacia afuera. Separarlos evita mezclar responsabilidades y hace que, por ejemplo, agregar un campo sensible en el futuro no implique exponerlo automáticamente en las respuestas de la API.


