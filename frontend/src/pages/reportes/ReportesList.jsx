// src/pages/reportes/ReportesList.jsx
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../../api/client";
import BadgeEstado from "../../components/BadgeEstado";
import { useAuth } from "../../context/AuthContext";
import { ESTADOS, PRIORIDADES, TIPOS_TAREA } from "../../constants";
import {
  FileSpreadsheet, FileDown, Edit2, Check, X, Plus, Inbox, Filter
} from "lucide-react";
import * as XLSX from "xlsx";
import jsPDF from "jspdf";
import "jspdf-autotable";

export default function ReportesList() {
  const { usuario } = useAuth();
  const esAdmin = usuario.is_superuser || usuario.roles.includes("Administrador");
  const puedeEditar = esAdmin || usuario.roles.includes("Tecnico");
  const puedeCrear = esAdmin || usuario.roles.includes("Tecnico");

  const [reportes, setReportes] = useState([]);
  const [areas, setAreas] = useState([]);
  const [tecnicos, setTecnicos] = useState([]);
  const [filtros, setFiltros] = useState({
    estado: "", tipo_tarea: "", prioridad: "", area: "", search: "",
  });
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

  // ============ EXPORTAR EXCEL (desde el backend) ============
  function exportarExcel() {
    const params = new URLSearchParams();
    Object.entries(filtros).forEach(([k, v]) => v && params.append(k, v));
    const token = localStorage.getItem("access");
    const base = import.meta.env.VITE_API_URL || "http://localhost:8000/api";
    fetch(`${base}/exportar/reportes/excel/?${params.toString()}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => res.blob())
      .then((blob) => descargar(blob, `Reportes_${new Date().toISOString().split("T")[0]}.xlsx`))
      .catch(() => alert("Error al exportar Excel."));
  }

  // ============ EXPORTAR PDF PROFESIONAL (generado en el frontend) ============
  function exportarPDF() {
    const doc = new jsPDF({ orientation: "landscape" });
    const fecha = new Date().toLocaleString("es-CO");

    // Encabezado institucional
    doc.setFillColor(30, 58, 95);
    doc.rect(0, 0, doc.internal.pageSize.getWidth(), 22, "F");
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(14);
    doc.text("Sistema de Reportes Técnicos", 14, 10);
    doc.setFontSize(9);
    doc.text("Universidad — Reporte General de Incidentes", 14, 17);

    doc.setTextColor(60, 60, 60);
    doc.setFontSize(9);
    doc.text(`Generado: ${fecha}`, 14, 30);
    doc.text(`Total de registros: ${reportes.length}`, 14, 36);

    // Filtros aplicados (si hay)
    const filtrosActivos = Object.entries(filtros)
      .filter(([, v]) => v)
      .map(([k, v]) => `${k}: ${v}`)
      .join("  ·  ");
    if (filtrosActivos) {
      doc.setFontSize(8);
      doc.setTextColor(120, 120, 120);
      doc.text(`Filtros: ${filtrosActivos}`, 14, 42);
    }

    // Tabla de reportes
    doc.autoTable({
      startY: 48,
      head: [["Código", "Tipo", "Área", "Prioridad", "Estado", "Técnico", "Fecha Creación"]],
      body: reportes.map((r) => [
        r.codigo,
        r.tipo_tarea_display || "—",
        r.area_nombre || "—",
        r.prioridad_display || "—",
        r.estado_display || "—",
        r.tecnico_nombre || "Sin asignar",
        new Date(r.fecha_creacion).toLocaleDateString("es-CO"),
      ]),
      theme: "grid",
      headStyles: { fillColor: [30, 58, 95], textColor: 255, fontStyle: "bold" },
      bodyStyles: { fontSize: 9 },
      alternateRowStyles: { fillColor: [248, 250, 252] },
      margin: { left: 14, right: 14 },
    });

    // Pie de página con espacio para firma
    const pageHeight = doc.internal.pageSize.getHeight();
    const pageCount = doc.internal.getNumberOfPages();
    for (let i = 1; i <= pageCount; i++) {
      doc.setPage(i);
      doc.setFontSize(8);
      doc.setTextColor(120, 120, 120);
      doc.text(
        `Página ${i} de ${pageCount}`,
        doc.internal.pageSize.getWidth() - 30,
        pageHeight - 10
      );

      // Línea y espacio para firma
      if (i === pageCount) {
        doc.setDrawColor(180, 180, 180);
        doc.line(14, pageHeight - 30, 90, pageHeight - 30);
        doc.text("Firma responsable", 14, pageHeight - 25);
      }
    }

    doc.save(`Reportes_${new Date().toISOString().split("T")[0]}.pdf`);
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
      const payload = { estado: valoresEdicion.estado };
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
    <div className="reportes-list-page">
      {/* ============ HEADER ============ */}
      <header className="reportes-list-header">
        <div>
          <h1 className="titulo-pagina">Reportes</h1>
          <p className="subtitulo-pagina">Consulta, filtra y exporta los reportes técnicos.</p>
        </div>
        <div className="reportes-list-header__acciones">
          {puedeCrear && (
            <Link to="/reportes/nuevo" className="btn btn--primario">
              <Plus size={16} /> Nuevo reporte
            </Link>
          )}
          <button className="btn-export btn-export--excel" onClick={exportarExcel}>
            <FileSpreadsheet size={16} /> Excel
          </button>
          <button className="btn-export btn-export--pdf" onClick={exportarPDF}>
            <FileDown size={16} /> PDF
          </button>
        </div>
      </header>

      {/* ============ FILTROS COMPACTOS ============ */}
      <div className="tarjeta tarjeta--filtros-compactos">
        <div className="filtros-grid">
          <div className="filtro-search">
            <Filter size={14} className="filtro-search__icon" />
            <input
              type="text"
              placeholder="Buscar código, descripción, usuario…"
              value={filtros.search}
              onChange={(e) => actualizarFiltro("search", e.target.value)}
            />
          </div>
          <select value={filtros.estado} onChange={(e) => actualizarFiltro("estado", e.target.value)}>
            <option value="">Estado</option>
            {ESTADOS.map((e) => <option key={e.value} value={e.value}>{e.label}</option>)}
          </select>
          <select value={filtros.tipo_tarea} onChange={(e) => actualizarFiltro("tipo_tarea", e.target.value)}>
            <option value="">Tipo</option>
            {TIPOS_TAREA.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
          </select>
          <select value={filtros.prioridad} onChange={(e) => actualizarFiltro("prioridad", e.target.value)}>
            <option value="">Prioridad</option>
            {PRIORIDADES.map((p) => <option key={p.value} value={p.value}>{p.label}</option>)}
          </select>
          <select value={filtros.area} onChange={(e) => actualizarFiltro("area", e.target.value)}>
            <option value="">Área</option>
            {areas.map((a) => <option key={a.id} value={a.id}>{a.nombre}</option>)}
          </select>
          {(filtros.estado || filtros.tipo_tarea || filtros.prioridad || filtros.area || filtros.search) && (
            <button
              className="btn btn--fantasma"
              onClick={() => setFiltros({ estado: "", tipo_tarea: "", prioridad: "", area: "", search: "" })}
            >
              Limpiar
            </button>
          )}
        </div>
      </div>

      {/* ============ TABLA ============ */}
      <div className="tarjeta">
        <div className="tabla-contenedor">
          <table className="tabla">
            <thead>
              <tr>
                <th>Código</th>
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
                <tr><td colSpan={puedeEditar ? 8 : 7} className="tabla__vacio">Cargando…</td></tr>
              ) : reportes.length === 0 ? (
                <tr>
                  <td colSpan={puedeEditar ? 8 : 7} className="tabla__vacio">
                    <Inbox size={28} style={{ opacity: 0.4, marginBottom: 6 }} />
                    <div>No hay reportes con estos filtros.</div>
                  </td>
                </tr>
              ) : (
                reportes.map((r) => (
                  <tr key={r.id}>
                    <td><Link to={`/reportes/${r.id}`} className="tabla__codigo">{r.codigo}</Link></td>
                    <td>{r.tipo_tarea_display}</td>
                    <td>{r.area_nombre}</td>
                    <td>{r.prioridad_display}</td>
                    <td>
                      {editandoId === r.id ? (
                        <select value={valoresEdicion.estado} onChange={(e) => setValoresEdicion((v) => ({ ...v, estado: e.target.value }))}>
                          {ESTADOS.map((e) => <option key={e.value} value={e.value}>{e.label}</option>)}
                        </select>
                      ) : (
                        <BadgeEstado estado={r.estado} texto={r.estado_display} />
                      )}
                    </td>
                    <td>
                      {editandoId === r.id ? (
                        <select value={valoresEdicion.tecnico_asignado} onChange={(e) => setValoresEdicion((v) => ({ ...v, tecnico_asignado: e.target.value }))}>
                          <option value="">Sin asignar</option>
                          {tecnicos.map((t) => <option key={t.id} value={t.id}>{t.nombre_completo}</option>)}
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
                            <button className="btn btn--primario btn--sm" onClick={() => guardarEdicion(r.id)} title="Guardar">
                              <Check size={14} />
                            </button>
                            <button className="btn btn--fantasma btn--sm" onClick={cancelarEdicion} title="Cancelar">
                              <X size={14} />
                            </button>
                          </div>
                        ) : (
                          <button className="btn btn--fantasma btn--sm" onClick={() => iniciarEdicion(r)} title="Editar">
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
        </div>

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