// src/pages/reportes/ReporteDetail.jsx
import { useEffect, useState } from "react";
import { Link, useParams, useNavigate } from "react-router-dom";
import api from "../../api/client";
import BadgeEstado from "../../components/BadgeEstado";
import { useAuth } from "../../context/AuthContext";
import { ESTADOS } from "../../constants";
import {
  ArrowLeft, FileDown, FileSpreadsheet, FileText, Edit,
  User, Building2, MapPin, Mail,
  Calendar, Clock, Wrench, CheckCircle, AlertCircle,
  Package, History, Send,
} from "lucide-react";

export default function ReporteDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { usuario } = useAuth();
  const [reporte, setReporte] = useState(null);
  const [nuevoEstado, setNuevoEstado] = useState("");
  const [comentario, setComentario] = useState("");
  const [solucion, setSolucion] = useState("");
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    cargar();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  function cargar() {
    api.get(`/reportes/${id}/`).then(({ data }) => {
      setReporte(data);
      setNuevoEstado(data.estado);
      setSolucion(data.solucion || "");
    });
  }

  if (!reporte) {
    return (
      <div className="pantalla-carga">
        <div className="spinner"></div>
        <p>Cargando reporte…</p>
      </div>
    );
  }

  const esAdmin = usuario.is_superuser || usuario.roles.includes("Administrador");
  const puedeGestionar =
    esAdmin ||
    (usuario.roles.includes("Tecnico") &&
      (reporte.creado_por === usuario.id || reporte.tecnico_asignado === usuario.id));

  async function cambiarEstado(e) {
    e.preventDefault();
    setGuardando(true);
    setError("");

    // Construir payload limpio
    const payload = {
      estado: nuevoEstado,
      comentario: comentario || "",
    };
    if (solucion.trim()) payload.solucion = solucion;

    try {
      const { data } = await api.post(`/reportes/${id}/cambiar-estado/`, payload);
      setReporte(data);
      setComentario("");
    } catch (err) {
      // Log detallado para diagnóstico
      console.error("Error al cambiar estado:");
      console.error("  Status:", err.response?.status);
      console.error("  Data:", err.response?.data);
      console.error("  Message:", err.message);

      // Mensaje específico según el error
      const detalle = err.response?.data?.detail
        || err.response?.data?.error
        || JSON.stringify(err.response?.data || {})
        || "Error desconocido";

      setError(`No se pudo actualizar: ${detalle}`);
    } finally {
      setGuardando(false);
    }
  }

  function exportar(formato) {
    const token = localStorage.getItem("access");
    const base = import.meta.env.VITE_API_URL || "http://localhost:8000/api";
    fetch(`${base}/exportar/reportes/${id}/${formato}/`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => {
        if (!res.ok) throw new Error("Error exportando");
        return res.blob();
      })
      .then((blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `${reporte.codigo}.${formato === "excel" ? "xlsx" : formato === "word" ? "docx" : "pdf"}`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
      })
      .catch(() => alert("Error al exportar. Verifica el endpoint del backend."));
  }

  return (
    <div className="reporte-detalle">
      {/* HEADER */}
      <div className="reporte-header">
        <button className="btn-atras" onClick={() => navigate(-1)}>
          <ArrowLeft size={16} /> Volver
        </button>

        <div className="reporte-header__titulo">
          <div>
            <div className="reporte-codigo">{reporte.codigo}</div>
            <h1 className="reporte-titulo">
              {reporte.tipo_tarea_nombre || "Reporte Técnico"}
            </h1>
          </div>
          <BadgeEstado estado={reporte.estado} texto={reporte.estado_display} />
        </div>

        <div className="reporte-header__acciones">
          <button className="btn-export btn-export--pdf" onClick={() => exportar("pdf")}>
            <FileDown size={16} /> PDF
          </button>
          <button className="btn-export btn-export--excel" onClick={() => exportar("excel")}>
            <FileSpreadsheet size={16} /> Excel
          </button>
          <button className="btn-export btn-export--word" onClick={() => exportar("word")}>
            <FileText size={16} /> Word
          </button>
          {puedeGestionar && (
            <Link className="btn btn--primario" to={`/reportes/${id}/editar`}>
              <Edit size={16} /> Editar
            </Link>
          )}
        </div>
      </div>

      <div className="reporte-grid">
        {/* COLUMNA IZQUIERDA */}
        <div className="reporte-columna-principal">
          <div className="tarjeta">
            <div className="tarjeta__encabezado" style={{ marginBottom: "1rem" }}>
              <h2><Wrench size={18} /> Información general</h2>
            </div>
            <dl className="lista-datos">
              <Dato icono={<Package size={16} />} etiqueta="Tipo de tarea" valor={reporte.tipo_tarea_nombre} />
              <Dato icono={<AlertCircle size={16} />} etiqueta="Prioridad" valor={reporte.prioridad_display} />
              <Dato icono={<Building2 size={16} />} etiqueta="Área" valor={reporte.area_nombre} />
              <Dato icono={<MapPin size={16} />} etiqueta="Ubicación" valor={reporte.ubicacion || "—"} />
              <Dato icono={<User size={16} />} etiqueta="Usuario afectado" valor={reporte.usuario_nombre || "—"} />
              <Dato icono={<User size={16} />} etiqueta="Cargo" valor={reporte.usuario_cargo || "—"} />
              <Dato icono={<Mail size={16} />} etiqueta="Correo" valor={reporte.usuario_correo || "—"} />
              <Dato icono={<Wrench size={16} />} etiqueta="Técnico asignado" valor={reporte.tecnico_nombre || "Sin asignar"} />
              <Dato icono={<User size={16} />} etiqueta="Creado por" valor={reporte.creado_por_nombre} />
              <Dato icono={<Calendar size={16} />} etiqueta="Fecha de creación" valor={new Date(reporte.fecha_creacion).toLocaleString("es-CO")} />
              <Dato icono={<CheckCircle size={16} />} etiqueta="Fecha de resolución" valor={reporte.fecha_resolucion ? new Date(reporte.fecha_resolucion).toLocaleString("es-CO") : "—"} />
              <Dato icono={<Clock size={16} />} etiqueta="Tiempo de resolución" valor={reporte.tiempo_resolucion_horas ? `${reporte.tiempo_resolucion_horas} h` : "—"} />
            </dl>
          </div>

          {reporte.equipos && reporte.equipos.length > 0 && (
            <div className="tarjeta">
              <div className="tarjeta__encabezado" style={{ marginBottom: "1rem" }}>
                <h2><Package size={18} /> Equipos / Activos ({reporte.equipos.length})</h2>
              </div>
              <div className="equipos-lista">
                {reporte.equipos.map((eq, idx) => (
                  <div key={idx} className="equipo-item">
                    <div className="equipo-item__numero">#{idx + 1}</div>
                    <div className="equipo-item__datos">
                      <span><strong>Código:</strong> {eq.codigo_activo || "—"}</span>
                      <span><strong>Marca:</strong> {eq.marca || "—"}</span>
                      <span><strong>Modelo:</strong> {eq.modelo || "—"}</span>
                      <span><strong>Serie:</strong> {eq.serie || "—"}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="tarjeta">
            <div className="tarjeta__encabezado" style={{ marginBottom: "1rem" }}>
              <h2><AlertCircle size={18} /> Descripción del problema</h2>
            </div>
            <p className="texto-parrafo">{reporte.descripcion}</p>
          </div>

          <div className="tarjeta tarjeta--solucion">
            <div className="tarjeta__encabezado" style={{ marginBottom: "1rem" }}>
              <h2><CheckCircle size={18} /> Solución / Notas técnicas</h2>
            </div>
            <p className="texto-parrafo">
              {reporte.solucion || "Sin registrar aún."}
            </p>
          </div>
        </div>

        {/* COLUMNA DERECHA */}
        <div className="reporte-columna-lateral">
          {puedeGestionar && (
            <div className="tarjeta">
              <div className="tarjeta__encabezado" style={{ marginBottom: "1rem" }}>
                <h2><Send size={18} /> Cambiar estado</h2>
              </div>
              <form onSubmit={cambiarEstado} className="formulario">
                <label>
                  Nuevo estado
                  <select value={nuevoEstado} onChange={(e) => setNuevoEstado(e.target.value)}>
                    {ESTADOS.map((e) => (
                      <option key={e.value} value={e.value}>{e.label}</option>
                    ))}
                  </select>
                </label>
                <label>
                  Solución / notas técnicas
                  <textarea rows={4} value={solucion} onChange={(e) => setSolucion(e.target.value)} />
                </label>
                <label>
                  Comentario del cambio (opcional)
                  <input type="text" value={comentario} onChange={(e) => setComentario(e.target.value)} />
                </label>
                {error && <div className="alerta alerta--error">{error}</div>}
                <button className="btn btn--primario btn--block" type="submit" disabled={guardando}>
                  {guardando ? "Guardando…" : "Guardar cambio"}
                </button>
              </form>
            </div>
          )}

          <div className="tarjeta">
            <div className="tarjeta__encabezado" style={{ marginBottom: "1rem" }}>
              <h2><History size={18} /> Historial de cambios</h2>
            </div>
            <ul className="linea-tiempo">
              {reporte.historial && reporte.historial.length > 0 ? (
                reporte.historial.map((h) => (
                  <li key={h.id}>
                    <div className="linea-tiempo__punto" />
                    <div className="linea-tiempo__contenido">
                      <strong>
                        {h.estado_anterior ? `${h.estado_anterior} → ` : ""}
                        {h.estado_nuevo}
                      </strong>
                      <p>{h.comentario || "Sin comentario"}</p>
                      <small>
                        {h.usuario_nombre} · {new Date(h.fecha).toLocaleString("es-CO")}
                      </small>
                    </div>
                  </li>
                ))
              ) : (
                <li className="tabla__vacio">Sin cambios registrados aún.</li>
              )}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

function Dato({ icono, etiqueta, valor }) {
  return (
    <div className="dato">
      <div className="dato__icono">{icono}</div>
      <div className="dato__texto">
        <dt>{etiqueta}</dt>
        <dd>{valor ?? "—"}</dd>
      </div>
    </div>
  );
}