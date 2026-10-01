// src/context/AuthContext.jsx
import { createContext, useContext, useEffect, useState } from "react";
import api, { clearTokens, setTokens } from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [usuario, setUsuario] = useState(null);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    const access = localStorage.getItem("access");
    if (!access) {
      setCargando(false);
      return;
    }
    api
      .get("/auth/me/")
      .then(({ data }) => setUsuario(data))
      .catch(() => setUsuario(null))
      .finally(() => setCargando(false));
  }, []);

  async function login(username, password) {
    const { data } = await api.post("/auth/login/", { username, password });
    setTokens({ access: data.access, refresh: data.refresh });
    setUsuario(data.usuario);
    return data.usuario;
  }

  function logout() {
    clearTokens();
    setUsuario(null);
  }

  async function eliminarCuenta() {
    await api.delete("/auth/me/eliminar/");
    clearTokens();
    setUsuario(null);
  }

  return (
    <AuthContext.Provider value={{ usuario, cargando, login, logout, eliminarCuenta }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}

export const ROLES = {
  ADMIN: "Administrador",
  AUDITOR: "Auditor",
  TECNICO: "Tecnico",
};