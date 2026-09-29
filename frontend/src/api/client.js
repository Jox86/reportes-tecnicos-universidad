import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

//export const api = axios.create({ baseURL: BASE_URL });
   const api = axios.create({ baseURL: "/api" });
   
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

api.interceptors.request.use((config) => {
  const { access } = getTokens();
  if (access) config.headers.Authorization = `Bearer ${access}`;
  return config;
});

let refrescando = null;

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._reintentado) {
      original._reintentado = true;
      const { refresh } = getTokens();
      if (refresh) {
        try {
          refrescando =
            refrescando ||
            axios.post(`${BASE_URL}/auth/refresh/`, { refresh }).finally(() => {
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
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export default api;
