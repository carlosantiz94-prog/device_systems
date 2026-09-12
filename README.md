# device_systems

**Aprendiz:** Juan Camilo Sarrazola
**Actividad:** GA1-220501096-01-AA1-EV08 — FastAPI Intermedio: Evolución de device_systems con CRUD completo, manejo de errores, Swagger/OpenAPI y Dependency Injection

---

## Descripción de la API

`device_systems` es una API REST construida con FastAPI para gestionar los usuarios de un sistema. Esta versión (**v2.0.0**) evoluciona la API básica de la actividad anterior (EV07, solo `GET`/`POST`) hacia un **CRUD completo**: ahora permite crear, listar, consultar, filtrar, actualizar (completa o parcialmente) y eliminar usuarios, con manejo de errores estructurado, códigos de estado HTTP correctos, reutilización de lógica mediante `Depends()`, y documentación automática mejorada con Swagger/OpenAPI.

## Tecnologías utilizadas

| Tecnología | Uso en el proyecto |
|---|---|
| **FastAPI** | Framework principal para construir la API |
| **Uvicorn** | Servidor ASGI que ejecuta la aplicación |
| **Pydantic v2** | Validación y serialización de datos de entrada/salida |
| **email-validator** | Validación del formato de correos (requerido por `EmailStr`) |


## Explicación de la estructura del proyecto

```
device_systems/
├── app/
│   ├── __init__.py
│   ├── main.py                       ← arranca la app, metadatos Swagger, cabeceras
│   ├── routes/
│   │   └── user_routes.py            ← endpoints: GET, POST, PUT, PATCH, DELETE
│   ├── schemas/
│   │   └── user_schema.py            ← UserCreate, UserUpdate, UserPatch, UserResponse
│   ├── services/
│   │   └── user_service.py           ← lógica de negocio (CRUD sobre users_db)
│   ├── dependencies/
│   │   └── user_dependencies.py      ← funciones reutilizables con Depends()
│   └── data/
│       └── users_db.py               ← "base de datos" en memoria
├── images/                           ← capturas de Swagger UI, ReDoc y Postman
├── requirements.txt
└── README.md
```

Cada carpeta tiene una sola responsabilidad, siguiendo el principio de separación de capas:

- **`routes/`** solo define endpoints (qué URL, qué método, qué modelo espera). No sabe cómo se buscan o guardan los usuarios.
- **`services/`** contiene toda la lógica de negocio (buscar, crear, actualizar, eliminar). Las rutas la llaman; nunca tocan `users_db` directamente.
- **`schemas/`** define la forma de los datos de entrada y salida, con sus validaciones.
- **`dependencies/`** contiene funciones reutilizables (como buscar un usuario y lanzar `404` si no existe), inyectadas con `Depends()`.
- **`data/`** simula la base de datos. Si mañana se conecta una base real, solo cambia este archivo.

## Tabla de endpoints

| Operación | Método | Ruta | Código esperado |
|---|---|---|---|
| Listar usuarios | GET | `/users` | `200 OK` |
| Filtrar por rol/estado | GET | `/users?role=admin` / `?is_active=true` | `200 OK` |
| Consultar usuario | GET | `/users/{user_id}` | `200 OK` / `404 Not Found` |
| Crear usuario | POST | `/users` | `201 Created` / `400` / `422` |
| Actualizar completo | PUT | `/users/{user_id}` | `200 OK` / `404` / `400` |
| Actualizar parcial | PATCH | `/users/{user_id}` | `200 OK` / `404` / `400` |
| Eliminar usuario | DELETE | `/users/{user_id}` | `200 OK` / `404 Not Found` |

## Modelos Pydantic (entrada y salida)

```python
class UserBase(BaseModel):
    name: str = Field(..., min_length=3)
    email: EmailStr
    role: Literal["admin", "support", "user"]
    is_active: bool = True

class UserCreate(UserBase): pass      # POST: todos los campos obligatorios
class UserUpdate(UserBase): pass      # PUT: todos los campos obligatorios (reemplazo total)

class UserPatch(BaseModel):           # PATCH: todos los campos OPCIONALES
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[Literal["admin", "support", "user"]] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int                           # lo único que se agrega en la salida
```

## Ejemplos de peticiones y respuestas

### GET /users?role=admin

```bash
curl "http://127.0.0.1:8000/users?role=admin"
```
```json
[{"name": "Ana Torres", "email": "ana@correo.com", "role": "admin", "is_active": true, "id": 1}]
```

### POST /users

```bash
curl -X POST http://127.0.0.1:8000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Sofía Restrepo", "email": "sofia@correo.com", "role": "user", "is_active": true}'
```
```json
{"name": "Sofía Restrepo", "email": "sofia@correo.com", "role": "user", "is_active": true, "id": 4}
```
Código: `201 Created`

### PUT /users/2 (reemplazo completo)

```bash
curl -X PUT http://127.0.0.1:8000/users/2 \
  -H "Content-Type: application/json" \
  -d '{"name": "Luis Ramirez G.", "email": "luisg@correo.com", "role": "admin", "is_active": false}'
```
```json
{"name": "Luis Ramirez G.", "email": "luisg@correo.com", "role": "admin", "is_active": false, "id": 2}
```
Código: `200 OK`

### PATCH /users/3 (actualización parcial)

```bash
curl -X PATCH http://127.0.0.1:8000/users/3 \
  -H "Content-Type: application/json" \
  -d '{"role": "support"}'
```
```json
{"name": "Camilo Sarrazola", "email": "camilo@correo.com", "role": "support", "is_active": false, "id": 3}
```
Solo cambió `role`; el resto de los campos quedó intacto. Código: `200 OK`

### PATCH /users/3 (sin campos → error)

```bash
curl -X PATCH http://127.0.0.1:8000/users/3 -H "Content-Type: application/json" -d '{}'
```
```json
{"detail": "Debes enviar al menos un campo para actualizar"}
```
Código: `400 Bad Request`

### DELETE /users/1

```bash
curl -X DELETE http://127.0.0.1:8000/users/1
```
```json
{"detail": "Usuario con id 1 eliminado correctamente"}
```
Código: `200 OK`

## Códigos de estado usados

| Código | Cuándo se usa |
|---|---|
| `200 OK` | Operación exitosa (GET, PUT, PATCH, DELETE) |
| `201 Created` | Usuario creado exitosamente (POST) |
| `400 Bad Request` | Correo duplicado, o PATCH enviado sin ningún campo |
| `404 Not Found` | El usuario solicitado no existe |
| `422 Unprocessable Content` | Datos inválidos según Pydantic (nombre corto, email mal formado, rol no permitido) |

## Evidencia de errores controlados

| Escenario | Método | Código | Respuesta |
|---|---|---|---|
| Usuario inexistente | GET / PUT / PATCH / DELETE `/users/999` | `404` | `{"detail": "Usuario no encontrado"}` |
| Correo duplicado | POST / PUT / PATCH | `400` | `{"detail": "Ya existe un usuario registrado con el correo ..."}` |
| PATCH sin campos | PATCH | `400` | `{"detail": "Debes enviar al menos un campo para actualizar"}` |
| Nombre corto (< 3 caracteres) | POST / PUT / PATCH | `422` | Error de Pydantic: `"String should have at least 3 characters"` |
| Rol no permitido | POST / PUT / PATCH | `422` | Error de Pydantic: `"Input should be 'admin', 'support' or 'user'"` |
| Correo con formato inválido | POST / PUT / PATCH | `422` | Error de Pydantic: `"value is not a valid email address"` |

## Explicación del manejo de errores implementado

Los errores de **negocio** (usuario no encontrado, correo duplicado, PATCH vacío) se manejan explícitamente con `HTTPException`, devolviendo siempre un JSON simple y consistente:

```python
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
```
```json
{"detail": "Usuario no encontrado"}
```

Los errores de **validación de datos** (nombre corto, email mal escrito, rol no permitido) los maneja **Pydantic automáticamente** a partir de las reglas definidas en los modelos (`min_length`, `EmailStr`, `Literal`) — FastAPI responde `422` antes de que el código del endpoint se ejecute, sin que se tenga que validar nada manualmente.

## Explicación del uso de Depends() (Dependency Injection)

La dependencia principal es `get_user_or_404`, definida en `app/dependencies/user_dependencies.py`:

```python
def get_user_or_404(user_id: int):
    usuario = user_service.buscar_usuario_por_id(user_id)
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario
```

Se reutiliza en **4 rutas distintas** (`GET`, `PUT`, `PATCH` y `DELETE` de `/users/{user_id}`):

```python
def obtener_usuario(usuario: dict = Depends(get_user_or_404)):
    return usuario
```

FastAPI ejecuta la dependencia **antes** de entrar al cuerpo del endpoint. Si el usuario no existe, la petición nunca llega a ejecutarse — el `404` se lanza directo desde la dependencia. Gracias a esto, ninguna de esas 4 rutas repite la lógica de "buscar el usuario y verificar que exista".

También se agregaron dos dependencias adicionales como ejemplo del patrón: `obtener_configuracion_api` (centraliza metadatos fijos de la API) y `verificar_api_key` (simula una autenticación básica leyendo la cabecera `X-API-Key` con `Header()`, sin ser obligatoria en esta actividad).

## Capturas de Swagger UI

![Swagger UI - vista general con el CRUD completo](images/evo8/swagger_general.png)


## Evidencia de pruebas de cada endpoint (Postman)

Todas las capturas están en `images/evo8/`.

### GET /users

![GET /users](images/evo8/postman_get_users.png)

`200 OK` — lista completa de usuarios.

### GET /users/999 (usuario inexistente)

![GET /users/999](images/evo8/postman_get_user_404.png)

`404 Not Found` — `{"detail": "Usuario no encontrado"}`

### POST /users (exitoso)

![POST /users exitoso](images/evo8/postman_post_exitoso.png)

`201 Created` — usuario creado con `id` asignado automáticamente.

### POST /users (correo duplicado)

![POST /users correo duplicado](images/evo8/postman_post_duplicado_400.png)

`400 Bad Request` — `{"detail": "Ya existe un usuario registrado con el correo sofia@correo.com"}`

### POST /users (datos inválidos)

![POST /users datos inválidos](images/evo8/postman_post_invalido_422.png)

`422 Unprocessable Content` — Pydantic detalla exactamente qué campo(s) fallaron (nombre muy corto, en este caso).

### PUT /users/{id} (reemplazo completo, exitoso)

![PUT /users/2 exitoso](images/evo8/postman_put_exitoso.png)

`200 OK` — todos los campos del usuario quedan reemplazados por los nuevos valores enviados.

### PATCH /users/{id} (actualización parcial)

![PATCH /users/3 parcial](images/evo8/postman_patch_parcial.png)

`200 OK` — solo se modifica el campo `role`; el resto de los datos del usuario permanece igual.

### PATCH /users/{id} (sin campos)

![PATCH /users/3 vacío](images/evo8/postman_patch_vacio_400.png)

`400 Bad Request` — `{"detail": "Debes enviar al menos un campo para actualizar"}`

### DELETE /users/{id} (exitoso)

![DELETE /users/1 exitoso](images/evo8/postman_delete_exitoso.png)

`200 OK` — `{"detail": "Usuario con id 1 eliminado correctamente"}`

### DELETE /users/{id} (usuario ya eliminado)

![DELETE /users/1 ya eliminado](images/evo8/postman_delete_404.png)

`404 Not Found` — porque ya no existe (se había eliminado en la prueba anterior).

## Reflexión final sobre la evolución del proyecto

Lo que más me costó entender fue `Depends()`. Al principio no tenía claro cómo `get_user_or_404` "sabía" cuál era el `user_id` sin que yo se lo pasara explícitamente en cada endpoint. Cuando entendí que FastAPI simplemente hace coincidir el nombre del parámetro con el de la ruta, todo tuvo sentido, y ahí valoré por qué se llama "inyección de dependencias" — la dependencia se ejecuta sola, antes de que mi función siquiera empiece, y si el usuario no existe, ni se molesta en llamar al resto del código.

También aprendí la diferencia real entre PUT y PATCH, no solo en teoría sino haciéndolo: PUT pide todos los campos porque reemplaza el usuario completo, mientras que PATCH usa `exclude_unset=True` para saber exactamente qué envió el cliente y no pisar los demás datos por accidente. Y agregar el DELETE fue el más simple de todos, casi una recompensa después de resolver los otros dos.

En general, este ejercicio me mostró cómo una API pequeña, si no se organiza bien desde el principio, se vuelve difícil de mantener apenas se le agrega una operación más. Separar por responsabilidades no fue un capricho de la guía, fue la única forma de que agregar PUT, PATCH y DELETE no significara reescribir todo lo que ya funcionaba.

