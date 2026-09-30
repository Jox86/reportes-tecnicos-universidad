// src/components/Layout.jsx
import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { LayoutDashboard, FileText, BarChart3, PlusCircle, LogOut, StarCheckIcon, StarHalf, StarX, StarsIcon } from "lucide-react";

export default function Layout() {
  const { usuario, logout } = useAuth();
  const esAdmin = usuario.is_superuser || usuario.roles.includes("Administrador");
  const puedeGestionar = esAdmin || usuario.roles.includes("Tecnico");

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="app-header__marca">
          <span className="app-header__logo">🛠️</span>
          <div>
            <strong>Reportes Técnicos</strong>
            <small>Universidad</small>
          </div>
        </div>

        <nav className="app-nav">
          <NavLink to="/" end>
            <LayoutDashboard size={16} /> Inicio
          </NavLink>
          <NavLink to="/reportes">
            <FileText size={16} /> Reportes
          </NavLink>
          <NavLink to="/estadisticas">
            <BarChart3 size={16} /> Estadísticas
          </NavLink>
          <NavLink to="/ranking">
            <StarsIcon size={16} /> Ranking
          </NavLink>
          {puedeGestionar && (
            <NavLink to="/reportes/nuevo" className="app-nav__cta">
              <PlusCircle size={16} /> Nuevo reporte
            </NavLink>
          )}
        </nav>

        <div className="app-header__usuario">
          <div className="app-header__usuario-info">
            <strong>{usuario.nombre}</strong>
            <small>{usuario.rol_principal || usuario.roles.join(", ") || "Sin rol asignado"}</small>
          </div>
          <button className="btn btn--fantasma" onClick={logout}>
            <LogOut size={16} /> 
          </button>
        </div>
      </header>

      <main className="app-contenido">
        <Outlet />
      </main>
    </div>
  );
}