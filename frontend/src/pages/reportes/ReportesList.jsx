// src/pages/reportes/ReportesList.jsx
import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../../api/client";
import BadgeEstado from "../../components/BadgeEstado";
import { useAuth } from "../../context/AuthContext";
import { ESTADOS, PRIORIDADES, TIPOS_TAREA } from "../../constants";
import { ArrowLeft, FileSpreadsheet, Edit2, Check, X, User } from "lucide-react";

export default function ReportesList() {
  const navigate = useNavigate();
  const { usuario } = useAuth();
  const esAdmin = usuario.is_superuser || usuario.roles.includes("Administrador");
  const puedeEditar = esAdmin || usuario.roles.includes("Tecnico");

  const [reportes, setReportes] = useState([]);
  const [areas, setAreas] = useState([]);
  const [tecnicos, setTecnicos] = useState([]);
  const [filtros, setFiltros] = useState({ estado: "", tipo_tarea: "", prioridad: "", area: "", search: "" });
  const [pagina, setPagina] = useState(1);
  const [totalPaginas, setTotalPaginas] = useState(1);
  const [cargando, setCargando] = useState(true);
  const [editandoId, setEditandoId] = useState(null);
  const [valoresEdicion, setValoresEdicion] = useState({ estado: "", tecnico_asignado: "" });

  useEffect(() => {
    api.get("/areas/").then(({ data }) => setAreas(data.results || data));
    if (puedeEditar) {
      api.get("/tecnicos/").then(({ data }) => setTecnicos(data.results || data));
    }
  }, [puedeEditar]);

  useEffect(() => {
    cargar();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filtros, pagina]);

  function cargar() {
    setCargando(true);
    const params = { page: pagina, ordering: "-fecha_creacion" };
    Object.entries(filtros).forEach(([k, v]) => {
      if (v) params[k] = v;
    });
    api
      .get("/reportes/", { params })
      .then(({ data }) => {
        if (Array.isArray(data)) {
          setReportes(data);
          setTotalPaginas(1);
        } else {
          setReportes(data.results);
          setTotalPaginas(Math.max(1, Math.ceil(data.count / 20)));
        }
      })
      .finally(() => setCargando(false));
  }

  function actualizarFiltro(campo, valor) {
    setPagina(1);
    setFiltros((f) => ({ ...f, [campo]: valor }));
  }

  function exportarExcel() {
    const params = new URLSearchParams();
    Object.entries(filtros).forEach(([k, v]) => v && params.append(k, v));
    const token = localStorage.getItem("access");
    const base = import.meta.env.VITE_API_URL || "http://localhost:8000/api";
    fetch(`${base}/exportar/reportes/excel/?${params.toString()}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => res.blob())
      .then((blob) => descargar(blob, "reportes.xlsx"))
      .catch(() => alert("Error al exportar. Verifica el endpoint del backend."));
  }

  function descargar(blob, nombre) {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = nombre;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  }

  function iniciarEdicion(reporte) {
    setEditandoId(reporte.id);
    setValoresEdicion({
      estado: reporte.estado,
      tecnico_asignado: reporte.tecnico_asignado || "",
    });
  }

  function cancelarEdicion() {
    setEditandoId(null);
    setValoresEdicion({ estado: "", tecnico_asignado: "" });
  }

  async function guardarEdicion(id) {
    try {
      const payload = {
        estado: valoresEdicion.estado,
      };
      if (valoresEdicion.tecnico_asignado !== "") {
        payload.tecnico_asignado = valoresEdicion.tecnico_asignado;
      }
      const { data } = await api.patch(`/reportes/${id}/`, payload);
      setReportes((prev) => prev.map((r) => (r.id === id ? { ...r, ...data } : r)));
      setEditandoId(null);
    } catch (err) {
      alert("No se pudo actualizar. Revisa los permisos.");
    }
  }

  return (
    <div>
      <div className="encabezado-lista">
        <div>
          <button className="btn btn--fantasma" onClick={() => navigate(-1)} style={{ marginBottom: 8 }}>
            <ArrowLeft size={16} /> Volver
          </button>
          <h1 className="titulo-pagina">Reportes</h1>
          <p className="subtitulo-pagina">Consulta, filtra y exporta los reportes técnicos.</p>
        </div>
        <button className="btn btn--secundario" onClick={exportarExcel}>
          <FileSpreadsheet size={16} /> Exportar a Excel
        </button>
      </div>

      <div className="tarjeta tarjeta--filtros">
        <input
          type="text"
          placeholder="Buscar por código, título, usuario…"
          value={filtros.search}
          onChange={(e) => actualizarFiltro("search", e.target.value)}
        />
        <select value={filtros.estado} onChange={(e) => actualizarFiltro("estado", e.target.value)}>
          <option value="">Todos los estados</option>
          {ESTADOS.map((e) => (
            <option key={e.value} value={e.value}>{e.label}</option>
          ))}
        </select>
        <select value={filtros.tipo_tarea} onChange={(e) => actualizarFiltro("tipo_tarea", e.target.value)}>
          <option value="">Todos los tipos</option>
          {TIPOS_TAREA.map((t) => (
            <option key={t.value} value={t.value}>{t.label}</option>
          ))}
        </select>
        <select value={filtros.prioridad} onChange={(e) => actualizarFiltro("prioridad", e.target.value)}>
          <option value="">Toda prioridad</option>
          {PRIORIDADES.map((p) => (
            <option key={p.value} value={p.value}>{p.label}</option>
          ))}
        </select>
        <select value={filtros.area} onChange={(e) => actualizarFiltro("area", e.target.value)}>
          <option value="">Toda área</option>
          {areas.map((a) => (
            <option key={a.id} value={a.id}>{a.nombre}</option>
          ))}
        </select>
      </div>

      <div className="tarjeta">
        <table className="tabla">
          <thead>
            <tr>
              <th>Código</th>
              <th>Título</th>
              <th>Tipo</th>
              <th>Área</th>
              <th>Prioridad</th>
              <th>Estado</th>
              <th>Técnico Asignado</th>
              <th>Fecha Creación</th>
              {puedeEditar && <th>Acciones</th>}
            </tr>
          </thead>
          <tbody>
            {cargando ? (
              <tr><td colSpan={puedeEditar ? 9 : 8} className="tabla__vacio">Cargando…</td></tr>
            ) : reportes.length === 0 ? (
              <tr><td colSpan={puedeEditar ? 9 : 8} className="tabla__vacio">No hay reportes con estos filtros.</td></tr>
            ) : (
              reportes.map((r) => (
                <tr key={r.id}>
                  <td><Link to={`/reportes/${r.id}`}>{r.codigo}</Link></td>
                  <td>{r.titulo}</td>
                  <td>{r.tipo_tarea_display}</td>
                  <td>{r.area_nombre}</td>
                  <td>{r.prioridad_display}</td>
                  <td>
                    {editandoId === r.id ? (
                      <select
                        value={valoresEdicion.estado}
                        onChange={(e) => setValoresEdicion((v) => ({ ...v, estado: e.target.value }))}
                      >
                        {ESTADOS.map((e) => (
                          <option key={e.value} value={e.value}>{e.label}</option>
                        ))}
                      </select>
                    ) : (
                      <BadgeEstado estado={r.estado} texto={r.estado_display} />
                    )}
                  </td>
                  <td>
                    {editandoId === r.id ? (
                      <select
                        value={valoresEdicion.tecnico_asignado}
                        onChange={(e) => setValoresEdicion((v) => ({ ...v, tecnico_asignado: e.target.value }))}
                      >
                        <option value="">Sin asignar</option>
                        {tecnicos.map((t) => (
                          <option key={t.id} value={t.id}>{t.nombre_completo}</option>
                        ))}
                      </select>
                    ) : (
                      r.tecnico_nombre || "Sin asignar"
                    )}
                  </td>
                  <td>{new Date(r.fecha_creacion).toLocaleDateString("es-CO")}</td>
                  {puedeEditar && (
                    <td>
                      {editandoId === r.id ? (
                        <div style={{ display: "flex", gap: 4 }}>
                          <button className="btn btn--primario" onClick={() => guardarEdicion(r.id)} title="Guardar">
                            <Check size={14} />
                          </button>
                          <button className="btn btn--fantasma" onClick={cancelarEdicion} title="Cancelar">
                            <X size={14} />
                          </button>
                        </div>
                      ) : (
                        <button className="btn btn--fantasma" onClick={() => iniciarEdicion(r)} title="Editar">
                          <Edit2 size={14} />
                        </button>
                      )}
                    </td>
                  )}
                </tr>
              ))
            )}
          </tbody>
        </table>

        {totalPaginas > 1 && (
          <div className="paginacion">
            <button disabled={pagina <= 1} onClick={() => setPagina((p) => p - 1)}>← Anterior</button>
            <span>Página {pagina} de {totalPaginas}</span>
            <button disabled={pagina >= totalPaginas} onClick={() => setPagina((p) => p + 1)}>Siguiente →</button>
          </div>
        )}
      </div>
    </div>
  );
}