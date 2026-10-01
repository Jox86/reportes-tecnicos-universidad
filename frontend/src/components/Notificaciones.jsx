// src/components/Notificaciones.jsx
import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api/client";
import { Bell, Check, X, FileText, RefreshCw } from "lucide-react";

export default function Notificaciones() {
  const [abierto, setAbierto] = useState(false);
  const [notificaciones, setNotificaciones] = useState([]);
  const [noLeidas, setNoLeidas] = useState(0);
  const dropdownRef = useRef(null);

  // Cargar notificaciones al montar y cada 30 segundos
  useEffect(() => {
    cargar();
    const intervalo = setInterval(cargar, 30000);
    return () => clearInterval(intervalo);
  }, []);

  // Cerrar al hacer clic fuera
  useEffect(() => {
    function handler(e) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setAbierto(false);
      }
    }
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  async function cargar() {
    try {
      const { data } = await api.get("/notificaciones/pendientes/");
      setNotificaciones(data.no_leidas || []);
      setNoLeidas(data.total || 0);
    } catch {
      // Silencioso si no hay notificaciones
    }
  }

  async function marcarTodas() {
    await api.post("/notificaciones/marcar-leidas/");
    setNotificaciones([]);
    setNoLeidas(0);
  }

  async function marcarUna(id) {
    await api.post(`/notificaciones/${id}/marcar-leida/`);
    setNotificaciones((prev) => prev.filter((n) => n.id !== id));
    setNoLeidas((n) => Math.max(0, n - 1));
  }

  function iconoTipo(tipo) {
    if (tipo === "cambio_estado") return <RefreshCw size={14} />;
    if (tipo === "nuevo_reporte") return <FileText size={14} />;
    return <Bell size={14} />;
  }

  return (
    <div className="notificaciones" ref={dropdownRef}>
      <button
        className="btn-notificaciones"
        onClick={() => setAbierto((v) => !v)}
        aria-label="Notificaciones"
      >
        <Bell size={18} />
        {noLeidas > 0 && (
          <span className="badge-notificaciones">{noLeidas > 9 ? "9+" : noLeidas}</span>
        )}
      </button>

      {abierto && (
        <div className="notificaciones-dropdown">
          <div className="notificaciones-dropdown__header">
            <strong>Notificaciones</strong>
            {noLeidas > 0 && (
              <button className="notificaciones-dropdown__marcar" onClick={marcarTodas}>
                <Check size={12} /> Marcar todas
              </button>
            )}
          </div>

          <div className="notificaciones-dropdown__body">
            {notificaciones.length === 0 ? (
              <p className="notificaciones-dropdown__vacio">
                <Bell size={24} style={{ opacity: 0.3 }} />
                <span>Sin notificaciones nuevas</span>
              </p>
            ) : (
              notificaciones.map((n) => (
                <div key={n.id} className="notificacion-item">
                  <div className="notificacion-item__icono">{iconoTipo(n.tipo)}</div>
                  <div className="notificacion-item__cuerpo">
                    <Link
                      to={n.reporte ? `/reportes/${n.reporte}` : "#"}
                      className="notificacion-item__titulo"
                      onClick={() => marcarUna(n.id)}
                    >
                      {n.titulo}
                    </Link>
                    <p className="notificacion-item__mensaje">{n.mensaje}</p>
                    <small>{n.fecha_relativa}</small>
                  </div>
                  <button
                    className="notificacion-item__cerrar"
                    onClick={() => marcarUna(n.id)}
                    title="Marcar como leída"
                  >
                    <X size={12} />
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}