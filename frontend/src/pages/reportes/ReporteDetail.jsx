// src/pages/reportes/ReporteDetail.jsx
import { useEffect, useState } from "react";
import { Link, useParams, useNavigate } from "react-router-dom";
import api from "../../api/client";
import BadgeEstado from "../../components/BadgeEstado";
import { useAuth } from "../../context/AuthContext";
import { ESTADOS } from "../../constants";
import {
  ArrowLeft, FileDown, FileSpreadsheet, Edit,
  User, Building2, MapPin, Mail, Phone,
  Calendar, Clock, Wrench, CheckCircle, AlertCircle,
  Paperclip, Package, History, Send
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
      <div className="loading-realm">
        <div className="loading-sword"></div>
        <p>Cargando reporte...</p>
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
    try {
      const { data } = await api.post(`/reportes/${id}/cambiar-estado/`, {
        estado: nuevoEstado,
        comentario,
        solucion,
      });
      setReporte(data);
      setComentario("");
    } catch (err) {
      setError("No se pudo actualizar el estado. Verifica los datos.");
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
          <button className="btn-export" onClick={() => exportar("pdf")} title="Exportar PDF">
            <FileDown size={16} /> PDF
          </button>
          <button className="btn-export" onClick={() => exportar("excel")} title="Exportar Excel">
            <FileSpreadsheet size={16} /> Excel
          </button>
          <button className="btn-export" onClick={() => exportar("word")} title="Exportar Word">
            <FileDown size={16} /> Word
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
          {/* Info general */}
          <div className="tarjeta-medieval">
            <div className="tarjeta-medieval__header">
              <Wrench size={18} />
              <h3>Información General</h3>
            </div>
            <dl className="lista-datos-medieval">
              <DatoMedieval icono={<Package size={16} />} etiqueta="Tipo de tarea" valor={reporte.tipo_tarea_nombre} />
              <DatoMedieval icono={<AlertCircle size={16} />} etiqueta="Prioridad" valor={reporte.prioridad_display} />
              <DatoMedieval icono={<Building2 size={16} />} etiqueta="Área" valor={reporte.area_nombre} />
              <DatoMedieval icono={<MapPin size={16} />} etiqueta="Ubicación" valor={reporte.ubicacion || "—"} />
              <DatoMedieval icono={<User size={16} />} etiqueta="Usuario afectado" valor={reporte.usuario_nombre || "—"} />
              <DatoMedieval icono={<User size={16} />} etiqueta="Cargo" valor={reporte.usuario_cargo || "—"} />
              <DatoMedieval icono={<Mail size={16} />} etiqueta="Correo" valor={reporte.usuario_correo || "—"} />
              <DatoMedieval icono={<Wrench size={16} />} etiqueta="Técnico asignado" valor={reporte.tecnico_nombre || "Sin asignar"} />
              <DatoMedieval icono={<User size={16} />} etiqueta="Creado por" valor={reporte.creado_por_nombre} />
              <DatoMedieval icono={<Calendar size={16} />} etiqueta="Fecha de creación" valor={new Date(reporte.fecha_creacion).toLocaleString("es-CO")} />
              <DatoMedieval icono={<CheckCircle size={16} />} etiqueta="Fecha de resolución" valor={reporte.fecha_resolucion ? new Date(reporte.fecha_resolucion).toLocaleString("es-CO") : "—"} />
              <DatoMedieval icono={<Clock size={16} />} etiqueta="Tiempo de resolución" valor={reporte.tiempo_resolucion_horas ? `${reporte.tiempo_resolucion_horas} h` : "—"} />
            </dl>
          </div>

          {/* Equipos */}
          {reporte.equipos && reporte.equipos.length > 0 && (
            <div className="tarjeta-medieval">
              <div className="tarjeta-medieval__header">
                <Package size={18} />
                <h3>Equipos / Activos ({reporte.equipos.length})</h3>
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

          {/* Descripción */}
          <div className="tarjeta-medieval">
            <div className="tarjeta-medieval__header">
              <AlertCircle size={18} />
              <h3>Descripción del Problema</h3>
            </div>
            <p className="texto-parrafo-medieval">{reporte.descripcion}</p>
          </div>

          {/* Solución */}
          <div className="tarjeta-medieval tarjeta-medieval--solucion">
            <div className="tarjeta-medieval__header">
              <CheckCircle size={18} />
              <h3>Solución / Notas Técnicas</h3>
            </div>
            <p className="texto-parrafo-medieval">
              {reporte.solucion || "Sin registrar aún."}
            </p>
          </div>

          {/* Archivos adjuntos */}
          {reporte.archivos && reporte.archivos.length > 0 && (
            <div className="tarjeta-medieval">
              <div className="tarjeta-medieval__header">
                <Paperclip size={18} />
                <h3>Archivos Adjuntos ({reporte.archivos.length})</h3>
              </div>
              <ul className="archivos-lista">
                {reporte.archivos.map((archivo) => (
                  <li key={archivo.id}>
                    <a href={archivo.url} target="_blank" rel="noopener noreferrer">
                      <Paperclip size={14} /> {archivo.nombre}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* COLUMNA DERECHA */}
        <div className="reporte-columna-lateral">
          {/* Cambiar estado */}
          {puedeGestionar && (
            <div className="tarjeta-medieval">
              <div className="tarjeta-medieval__header">
                <Send size={18} />
                <h3>Cambiar Estado</h3>
              </div>
              <form onSubmit={cambiarEstado} className="formulario-medieval">
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
                <button className="btn-rune btn-rune--primario" type="submit" disabled={guardando}>
                  {guardando ? "Guardando…" : "Guardar Cambio"}
                </button>
              </form>
            </div>
          )}

          {/* Historial */}
          <div className="tarjeta-medieval">
            <div className="tarjeta-medieval__header">
              <History size={18} />
              <h3>Historial de Cambios</h3>
            </div>
            <ul className="linea-tiempo-medieval">
              {reporte.historial && reporte.historial.length > 0 ? (
                reporte.historial.map((h) => (
                  <li key={h.id}>
                    <div className="linea-tiempo-medieval__punto" />
                    <div className="linea-tiempo-medieval__contenido">
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
                <li className="sin-datos-medieval">Sin cambios registrados aún.</li>
              )}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

// ============================================================
// Componente: Dato individual con icono
// ============================================================
function DatoMedieval({ icono, etiqueta, valor }) {
  return (
    <div className="dato-medieval">
      <div className="dato-medieval__icono">{icono}</div>
      <div className="dato-medieval__texto">
        <dt>{etiqueta}</dt>
        <dd>{valor ?? "—"}</dd>
      </div>
    </div>
  );
}