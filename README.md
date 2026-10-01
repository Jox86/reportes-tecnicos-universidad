# Sistema de Reportes Técnicos — Universidad

App web (backend Django + frontend React) para que los técnicos de TI registren
reportes (gestión de activos fijos, reparación de hardware, actualización de
sistema, recuperación de cuentas, etc.), con login por roles, exportación
profesional (PDF, Excel, Word) y gráficos estadísticos dinámicos.

Pensada para desplegarse **dentro de la red interna** de la universidad.

## Estructura del proyecto

```
proyecto/
├── backend/     → API REST (Django + Django REST Framework + SQLite)
└── frontend/    → Interfaz web (React + Vite)
```

Ver `backend/README.md` y `frontend/README.md` (o la sección de instalación
más abajo) para ponerlo en marcha.

## Roles del sistema

| Rol            | Puede…                                                                 |
|----------------|-------------------------------------------------------------------------|
| **Administrador** | Todo: crear/editar/eliminar reportes y catálogos, gestionar usuarios (vía `/admin/`) |
| **Auditor**       | Solo lectura de todos los reportes + exportar (PDF/Excel/Word) + ver historial |
| **Director**      | Solo lectura + panel de estadísticas + exportar |
| **Técnico**       | Crear reportes, editar/cambiar estado solo de los suyos (creados o asignados) |

Los roles se manejan como **Grupos de Django** (`Administrador`, `Auditor`,
`Director`, `Tecnico`). Se crean con el comando `setup_roles` (ver abajo).

## Requisitos

- Python 3.11+
- Node.js 18+ y npm
- (Opcional, más adelante) Servidor Active Directory / LDAP de la universidad, si vas a usar
  login con AD. Si no lo tienes a mano todavía, el sistema funciona con
  usuarios locales de Django sin ningún cambio.

## Puesta en marcha — Backend

```bash
cd backend
python -m venv .venv

# Activar entorno virtual (debe aparecer "(.venv)" al inicio de la línea)
.venv\Scripts\activate           # Windows CMD
.\.venv\Scripts\Activate.ps1     # Windows PowerShell
source .venv/bin/activate        # Linux / macOS / WSL

python -m pip install --upgrade pip
python -m pip install -r requirements.txt     # usa siempre "python -m pip"

copy .env.example .env           # Windows   (cp en Linux / macOS)

python manage.py makemigrations core
python manage.py migrate
python manage.py setup_roles
python manage.py seed_demo       # opcional: usuarios, catálogos y reportes de prueba
python manage.py runserver 0.0.0.0:8000
```

La app **no necesita internet, ni el proxy, ni Active Directory** para funcionar:
usa SQLite, usuarios locales y correo en consola. El proxy solo afecta a
`pip`/`npm` durante la instalación.

Si no usas `seed_demo`, crea tu primer administrador con
`python manage.py createsuperuser`.

### Si aparece "No module named 'django'"

Significa que `python` no es el mismo intérprete donde se instalaron los paquetes.
Comprueba:

```bash
python -c "import sys; print(sys.executable)"   # ¿apunta a ...\.venv\Scripts\python.exe?
python -m pip show django                        # debe mostrar la versión instalada
```

Si no aparece, activa el entorno virtual y reinstala con `python -m pip install -r requirements.txt`.
Fíjate que `pip install` termine sin errores: si un solo paquete falla, pip no instala ninguno.

### Datos de prueba (modo demo, sin AD)

`python manage.py seed_demo` crea usuarios, catálogos y 45 reportes de prueba; el comando está bloqueado cuando `DEBUG=False`.
distribuidos en 6 meses. La contraseña demo se genera aleatoriamente en cada ejecución (o puede definirse mediante `DEMO_PASSWORD`).

| Usuario         | Rol            |
|-----------------|----------------|
| `admin_demo`    | Administrador (también entra a `/admin/`) |
| `auditor_demo`  | Auditor        |
| `director_demo` | Director       |
| `tecnico1..3`   | Técnico        |

### LDAP / Active Directory (opcional)

`django-auth-ldap` no viene en `requirements.txt` porque en Windows `python-ldap`
suele fallar al compilar. Cuando quieras conectar con el AD:

```bash
python -m pip install -r requirements-ldap.txt
```

Ver más abajo la configuración del `.env`.

### Asignar roles a usuarios (modo local, sin AD)

1. Entra a `http://localhost:8000/admin/` con tu superusuario.
2. Crea usuarios en **Usuarios** y agrégalos al grupo correspondiente
   (Administrador / Auditor / Director / Tecnico) en **Grupos**.

### Conectar con Active Directory (cuando lo tengas disponible)

Edita `backend/.env`:

```
AUTH_LDAP_SERVER_URI=ldap://tu-servidor-ad.universidad.edu
AUTH_LDAP_BIND_DN=cn=servicio,dc=universidad,dc=edu
AUTH_LDAP_BIND_PASSWORD=********
AUTH_LDAP_USER_SEARCH_BASE=dc=universidad,dc=edu
AUTH_LDAP_GROUP_SEARCH_BASE=dc=universidad,dc=edu
AD_GROUP_ADMIN=TI-Administradores
AD_GROUP_AUDITOR=TI-Auditores
AD_GROUP_DIRECTOR=TI-Directores
AD_GROUP_TECNICO=TI-Tecnicos
```

Ajusta los 4 `AD_GROUP_*` a los nombres CN reales de los grupos de seguridad
en tu Active Directory. El sistema traduce automáticamente esos grupos del AD
a los 4 roles internos al iniciar sesión.

## Puesta en marcha — Frontend

```bash
cd frontend
npm install
copy .env.example .env      # Windows
cp .env.example .env        # Linux / macOS
npm run dev
```

Abre `http://localhost:5173`. Inicia sesión con el superusuario que creaste
(o cualquier usuario asignado a un grupo/rol).

Para producción: `npm run build` genera `frontend/dist/` (archivos estáticos
que puedes servir desde Nginx/Apache/IIS en el servidor de la red interna).

## Datos de catálogo iniciales

Antes de crear reportes necesitas al menos un **Tipo de área**, un **Área** y
una **Ubicación**. Como Administrador, ve a **Catálogos** en el menú y
agrégalos (o hazlo desde `/admin/`).

## Funcionalidades incluidas

- Reportes con código automático (`RPT-2026-0001`), tipo de tarea, prioridad,
  estado (Pendiente → En proceso → Resuelto → Cerrado), datos de
  área/tipo de área/ubicación/usuario afectado y datos opcionales de
  equipo/activo (código de activo, marca, modelo, serie).
- Historial de cambios de estado por reporte (auditable).
- Notificaciones automáticas por correo al crear un reporte y al marcarlo
  como Resuelto/Cerrado (usa el backend de consola en desarrollo si no
  configuras SMTP en `.env`).
- Exportación: PDF y Word individual por reporte, Excel masivo (respeta los
  filtros activos en el listado, incluye hoja de resumen con gráficos).
- Estadísticas dinámicas: línea (reportes por mes), pastel moderno
  (distribución por tipo de tarea), barras (por área y por técnico), con
  filtro de rango de fechas.
- Permisos por rol aplicados tanto en la API (backend) como en la interfaz
  (frontend).

## Posibles siguientes pasos (no incluidos aún)

- Adjuntar fotos/archivos a un reporte (dijiste que no era necesario por
  ahora; si cambia, es una extensión sencilla: agregar un modelo `Adjunto`
  con `FileField` y un endpoint de subida).
- Gestión de usuarios/roles desde la propia interfaz React (hoy se hace
  desde `/admin/`, que ya es funcional pero no tiene la misma imagen que el
  resto de la app).
- Empaquetado para producción (Docker, Nginx, Gunicorn) si finalmente se
  quiere accesible fuera de la red interna.
