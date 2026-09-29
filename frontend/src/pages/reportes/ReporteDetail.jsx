// src/pages/reportes/ReporteDetail.jsx
import { useEffect, useState } from "react";
import { Link, useParams, useNavigate } from "react-router-dom";
import api from "../../api/client";
import BadgeEstado from "../../components/BadgeEstado";
import { useAuth } from "../../context/AuthContext";
import { ESTADOS } from "../../constants";
import { ArrowLeft, FileDown, FileSpreadsheet, Edit } from "lucide-react";

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

  if (!reporte) return <p>Cargando reporte…</p>;

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
      .then((res) => res.blob())
      .then((blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `${reporte.codigo}.${formato === "excel" ? "xlsx" : "pdf"}`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
      })
      .catch(() => alert("Error al exportar. Verifica el endpoint del backend."));
  }

  return (
    <div>
      <div className="encabezado-lista">
        <div>
          <button className="btn btn--fantasma" onClick={() => navigate(-1)} style={{ marginBottom: 8 }}>
            <ArrowLeft size={16} /> Volver al listado
          </button>
          <h1 className="titulo-pagina">
            {reporte.codigo} <BadgeEstado estado={reporte.estado} texto={reporte.estado_display} />
          </h1>
          <p className="subtitulo-pagina">{reporte.titulo}</p>
        </div>
        <div className="acciones-detalle">
          <button className="btn btn--secundario" onClick={() => exportar("pdf")}>
            <FileDown size={16} /> PDF
          </button>
          <button className="btn btn--secundario" onClick={() => exportar("excel")}>
            <FileSpreadsheet size={16} /> Excel
          </button>
          {puedeGestionar && (
            <Link className="btn btn--primario" to={`/reportes/${id}/editar`}>
              <Edit size={16} /> Editar
            </Link>
          )}
        </div>
      </div>

      <div className="grid-detalle">
        <div className="tarjeta">
          <h2>Información general</h2>
          <dl className="lista-datos">
            <Dato etiqueta="Tipo de tarea" valor={reporte.tipo_tarea_display} />
            <Dato etiqueta="Prioridad" valor={reporte.prioridad_display} />
            <Dato etiqueta="Área" valor={reporte.area_nombre} />
            <Dato etiqueta="Ubicación" valor={reporte.ubicacion_nombre || "—"} />
            <Dato etiqueta="Usuario afectado" valor={reporte.usuario_nombre} />
            <Dato etiqueta="Cargo / dependencia" valor={reporte.usuario_cargo || "—"} />
            <Dato etiqueta="Correo del usuario" valor={reporte.usuario_correo || "—"} />
            <Dato etiqueta="Técnico asignado" valor={reporte.tecnico_nombre || "Sin asignar"} />
            <Dato etiqueta="Creado por" valor={reporte.creado_por_nombre} />
            <Dato etiqueta="Fecha de creación" valor={new Date(reporte.fecha_creacion).toLocaleString("es-CO")} />
            <Dato
              etiqueta="Fecha de resolución"
              valor={reporte.fecha_resolucion ? new Date(reporte.fecha_resolucion).toLocaleString("es-CO") : "—"}
            />
            <Dato
              etiqueta="Tiempo de resolución"
              valor={reporte.tiempo_resolucion_horas ? `${reporte.tiempo_resolucion_horas} h` : "—"}
            />
          </dl>

          {reporte.equipos && reporte.equipos.length > 0 && (
            <>
              <h3>Equipos / activos</h3>
              {reporte.equipos.map((eq, idx) => (
                <dl className="lista-datos" key={idx} style={{ borderBottom: "1px solid #eee", paddingBottom: 8, marginBottom: 8 }}>
                  <Dato etiqueta={`Equipo #${idx + 1} - Código`} valor={eq.codigo_activo || "—"} />
                  <Dato etiqueta="Marca" valor={eq.marca || "—"} />
                  <Dato etiqueta="Modelo" valor={eq.modelo || "—"} />
                  <Dato etiqueta="N.º de serie" valor={eq.serie || "—"} />
                </dl>
              ))}
            </>
          )}

          <h3>Descripción</h3>
          <p className="texto-parrafo">{reporte.descripcion}</p>

          <h3>Solución / notas técnicas</h3>
          <p className="texto-parrafo">{reporte.solucion || "Sin registrar aún."}</p>

          {/* Archivos adjuntos */}
          {reporte.archivos && reporte.archivos.length > 0 && (
            <>
              <h3>Archivos adjuntos</h3>
              <ul>
                {reporte.archivos.map((archivo) => (
                  <li key={archivo.id}>
                    <a href={archivo.url} target="_blank" rel="noopener noreferrer">
                      {archivo.nombre}
                    </a>
                  </li>
                ))}
              </ul>
            </>
          )}
        </div>

        <div>
          {puedeGestionar && (
            <div className="tarjeta">
              <h2>Cambiar estado</h2>
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
                <button className="btn btn--primario" type="submit" disabled={guardando}>
                  {guardando ? "Guardando…" : "Guardar cambio"}
                </button>
              </form>
            </div>
          )}

          <div className="tarjeta">
            <h2>Historial</h2>
            <ul className="linea-tiempo">
              {reporte.historial.map((h) => (
                <li key={h.id}>
                  <div className="linea-tiempo__punto" />
                  <div>
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
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

function Dato({ etiqueta, valor }) {
  return (
    <div className="lista-datos__item">
      <dt>{etiqueta}</dt>
      <dd>{valor}</dd>
    </div>
  );
}