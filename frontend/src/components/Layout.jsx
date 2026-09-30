// src/components/Layout.jsx
import { useState, useEffect } from "react";
import { NavLink, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useTheme } from "../hooks/useTheme";
import { Sun, Moon } from "lucide-react";
import {
  LayoutDashboard,
  FileText,
  BarChart3,
  Star,
  LogOut,
  Menu,
  X,
  ShieldCheck,
  Wrench,
} from "lucide-react";

export default function Layout() {
  const { usuario, logout } = useAuth();
  const location = useLocation();
  const [menuAbierto, setMenuAbierto] = useState(false);
  const { tema, toggleTema } = useTheme();

  const esAdmin = usuario?.is_superuser || usuario?.roles?.includes("Administrador");
  const puedeGestionar = esAdmin || usuario?.roles?.includes("Tecnico");

  // Cerrar menú al cambiar de ruta
  useEffect(() => {
    setMenuAbierto(false);
  }, [location.pathname]);

  // Bloquear scroll cuando el menú está abierto en móvil
  useEffect(() => {
    if (menuAbierto) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [menuAbierto]);

  const navItems = [
    { to: "/", end: true, icon: <LayoutDashboard size={18} />, label: "Inicio" },
    { to: "/reportes", icon: <FileText size={18} />, label: "Reportes" },
    { to: "/estadisticas", icon: <BarChart3 size={18} />, label: "Estadísticas" },
    { to: "/ranking", icon: <Star size={18} />, label: "Ranking" },
  ];

  return (
    <div className="app-shell">
      {/* ============ TOPBAR ============ */}
      <header className="app-header">
        {/* Marca */}
        <NavLink to="/" className="app-header__marca">
          <span className="app-header__logo">
            <Wrench size={22} />
          </span>
          <div className="app-header__marca-texto">
            <strong>Reportes Técnicos</strong>
            <small>Universidad</small>
          </div>
        </NavLink>

        {/* Nav desktop */}
        <nav className="app-nav app-nav--desktop">
          {navItems.map((item) => (
            <NavLink key={item.to} to={item.to} end={item.end}>
              {item.icon}
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        {/* Usuario + logout */}
        <div className="app-header__usuario">
          <div className="app-header__usuario-info">
            <strong>{usuario?.nombre || "Usuario"}</strong>
            <small className="app-header__rol">
              <ShieldCheck size={11} />
              {usuario?.rol_principal || usuario?.roles?.join(", ") || "Sin rol"}
            </small>
          </div>
          <button
            className="btn-tema"
            onClick={toggleTema}
            title={tema === "light" ? "Modo oscuro" : "Modo claro"}
          >
            {tema === "light" ? <Moon size={18} /> : <Sun size={18} />}
          </button>
          <button
            className="btn-salir"
            onClick={logout}
            title="Cerrar sesión"
            aria-label="Cerrar sesión"
          >
            <LogOut size={16} />
            <span className="btn-salir__texto">Salir</span>
          </button>
        </div>

        {/* Hamburguesa (solo visible en móvil/tablet) */}
        <button
          className="app-header__hamburguesa"
          onClick={() => setMenuAbierto((v) => !v)}
          aria-label={menuAbierto ? "Cerrar menú" : "Abrir menú"}
        >
          {menuAbierto ? <X size={22} /> : <Menu size={22} />}
        </button>
      </header>

      {/* ============ MENÚ MÓVIL ============ */}
      {menuAbierto && (
        <>
          <div className="app-menu-overlay" onClick={() => setMenuAbierto(false)} />
          <nav className="app-menu-movil">
            <div className="app-menu-movil__header">
              <span className="app-menu-movil__usuario">
                <strong>{usuario?.nombre || "Usuario"}</strong>
                <small>{usuario?.rol_principal || usuario?.roles?.join(", ") || "Sin rol"}</small>
              </span>
            </div>

            <div className="app-menu-movil__links">
              {navItems.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.end}
                  className={({ isActive }) =>
                    isActive ? "app-menu-movil__link activo" : "app-menu-movil__link"
                  }
                >
                  {item.icon}
                  <span>{item.label}</span>
                </NavLink>
              ))}

              {puedeGestionar && (
                <NavLink
                  to="/reportes/nuevo"
                  className="app-menu-movil__link app-menu-movil__link--cta"
                >
                  <FileText size={18} />
                  <span>Nuevo reporte</span>
                </NavLink>
              )}
            </div>

            <button className="app-menu-movil__salir" onClick={logout}>
              <LogOut size={18} />
              <span>Cerrar sesión</span>
            </button>
          </nav>
        </>
      )}

      {/* ============ CONTENIDO ============ */}
      <main className="app-contenido">
        <Outlet />
      </main>
    </div>
  );
}