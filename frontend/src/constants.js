// src/constants.js

// Estados del reporte (coinciden con el backend)
export const ESTADOS = [
  { value: "pendiente", label: "Pendiente" },
  { value: "en_proceso", label: "En proceso" },
  { value: "resuelto", label: "Resuelto" },
  { value: "cerrado", label: "Cerrado" },
];

// Prioridades del reporte
export const PRIORIDADES = [
  { value: "baja", label: "Baja" },
  { value: "media", label: "Media" },
  { value: "alta", label: "Alta" },
  { value: "critica", label: "Crítica" },
];

// Tipos de tarea (solo como fallback — lo ideal es cargarlos del backend)
export const TIPOS_TAREA = [
  { value: "activos_fijos", label: "Activos fijos" },
  { value: "reparacion_hardware", label: "Reparación de hardware" },
  { value: "actualizacion_sistema", label: "Actualización de sistema" },
  { value: "recuperacion_cuentas", label: "Recuperación de cuentas" },
  { value: "mantenimiento_preventivo", label: "Mantenimiento preventivo" },
  { value: "soporte_red", label: "Soporte de red" },
  { value: "instalacion_software", label: "Instalación de software" },
  { value: "otro", label: "Otro" },
];