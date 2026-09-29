App Reportes Tecnicos

Proyecto
Una app para pc para reportes de tecnicos informaticos
Última actualización
27 sept 2026
Resumen

App de reportes para técnicos de TI universitarios — stack Python/Django/React/SQLite, login por roles, exportación y gráficos estadísticos.

Detalles
Herramientas base definidas: Python, SQLite, React, Django, npm, Node.js
Tareas ejemplo que generan reportes: gestión de activos fijos, reparación de hardware, actualizaciones de sistema, recuperación de cuentas, entre otras
Datos imprescindibles en los reportes: área, tipo de área, ubicación y usuario, entre otros
Necesita gráficos estadísticos dinámicos: de línea, pastel moderno y de barras
Login por roles: auditor, admin, director, técnicos
Requiere exportación de reportes profesional y completa
Pidió que se le hagan preguntas básicas antes de generar la app
Despliegue elegido: app web en red interna (navegador, servidor local)
Formatos de exportación elegidos: PDF, Excel y Word
Login elegido: integración con Active Directory/LDAP de la universidad
Flujo de estados elegido: Pendiente → En proceso → Resuelto → Cerrado (estándar)
No necesita adjuntar archivos/fotos como evidencia
Sí necesita notificaciones automáticas por correo al crear/resolver reportes
Corre el backend en Windows; su red (probablemente universitaria) tiene un proxy que corta la conexión de pip a PyPI (ProxyError/RemoteDisconnected al instalar Django)
Quiere probar la app primero en local, sin conectarla a la red/proxy de la universidad ni al AD; pypi.org sí abre en su navegador