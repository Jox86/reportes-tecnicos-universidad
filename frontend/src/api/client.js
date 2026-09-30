// src/api/client.js
import axios from "axios";

// Determinar la URL base del backend:
// 1. Si VITE_API_URL está definida (en .env), usarla
// 2. Si no, usar localhost:8000/api como fallback
const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

console.log("🌐 API Base URL:", BASE_URL);

const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// ---------------------------------------------------------------------------
// Helpers de tokens
// ---------------------------------------------------------------------------
function getTokens() {
  return {
    access: localStorage.getItem("access"),
    refresh: localStorage.getItem("refresh"),
  };
}

export function setTokens({ access, refresh }) {
  if (access) localStorage.setItem("access", access);
  if (refresh) localStorage.setItem("refresh", refresh);
}

export function clearTokens() {
  localStorage.removeItem("access");
  localStorage.removeItem("refresh");
}

// ---------------------------------------------------------------------------
// Interceptor: agregar token de acceso a cada request
// ---------------------------------------------------------------------------
api.interceptors.request.use((config) => {
  const { access } = getTokens();
  if (access) config.headers.Authorization = `Bearer ${access}`;
  return config;
});

// ---------------------------------------------------------------------------
// Interceptor: refrescar token en 401
// ---------------------------------------------------------------------------
let refrescando = null;

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;

    // No intentar refrescar si:
    // - No hay response (error de red)
    // - Ya se reintentó
    // - La URL es la de login o refresh (evita loops infinitos)
    const esLoginORefresh =
      original.url?.includes("/auth/login/") ||
      original.url?.includes("/auth/refresh/");

    if (
      error.response?.status === 401 &&
      !original._reintentado &&
      !esLoginORefresh
    ) {
      original._reintentado = true;
      const { refresh } = getTokens();

      if (refresh) {
        try {
          refrescando =
            refrescando ||
            axios
              .post(`${BASE_URL}/auth/refresh/`, { refresh })
              .finally(() => {
                refrescando = null;
              });
          const { data } = await refrescando;
          setTokens({ access: data.access });
          original.headers.Authorization = `Bearer ${data.access}`;
          return api(original);
        } catch (e) {
          clearTokens();
          window.location.href = "/login";
        }
      } else {
        clearTokens();
        // No redirigir si ya estamos en /login
        if (window.location.pathname !== "/login") {
          window.location.href = "/login";
        }
      }
    }
    return Promise.reject(error);
  }
);

export default api;