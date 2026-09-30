// src/pages/Dashboard.jsx
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api/client";
import { useAuth } from "../context/AuthContext";
import BadgeEstado from "../components/BadgeEstado";
import {
  FileText,
  CheckCircle,
  Clock,
  AlertTriangle,
  FileSpreadsheet,
  FileDown,
  ArrowUpRight,
  ArrowDownRight,
  Trophy,
  Medal,
  Inbox,
} from "lucide-react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import * as XLSX from "xlsx";
import jsPDF from "jspdf";
import "jspdf-autotable";

const COLORES_PIE = ["#1e3a5f", "#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#06b6d4"];

export default function Dashboard() {
  const { usuario } = useAuth();
  const [resumen, setResumen] = useState(null);
  const [recientes, setRecientes] = useState([]);
  const [ranking, setRanking] = useState([]);
  const [porMes, setPorMes] = useState([]);
  const [porTipo, setPorTipo] = useState([]);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    Promise.all([
      api.get("/estadisticas/resumen/"),
      api.get("/reportes/", { params: { ordering: "-fecha_creacion", page_size: 5 } }),
      api.get("/estadisticas/ranking/").catch(() => ({ data: [] })),
      api.get("/estadisticas/por-mes/").catch(() => ({ data: [] })),
      api.get("/estadisticas/por-tipo/").catch(() => ({ data: [] })),
    ])
      .then(([r1, r2, r3, r4, r5]) => {
        setResumen(r1.data);
        setRecientes((r2.data.results || r2.data).slice(0, 5));
        setRanking(r3.data || []);
        setPorMes(r4.data || []);
        setPorTipo(r5.data || []);
      })
      .catch((err) => console.error("Error cargando dashboard", err))
      .finally(() => setCargando(false));
  }, []);

  // ============ Exportación Excel ============
  const exportarExcel = () => {
    const ws = XLSX.utils.json_to_sheet(recientes);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Reportes Recientes");
    XLSX.writeFile(wb, `Reportes_${new Date().toISOString().split("T")[0]}.xlsx`);
  };

  // ============ Exportación PDF ============
  const exportarPDF = () => {
    const doc = new jsPDF();
    doc.setFontSize(16);
    doc.text("Reporte General — Sistema de Reportes Técnicos", 14, 18);
    doc.setFontSize(10);
    doc.text(`Generado: ${new Date().toLocaleString("es-CO")}`, 14, 24);

    doc.autoTable({
      startY: 32,
      head: [["Código", "Tipo", "Área", "Técnico", "Estado", "Fecha"]],
      body: recientes.map((r) => [
        r.codigo,
        r.tipo_tarea_display || "—",
        r.area_nombre || "—",
        r.tecnico_nombre || "Sin asignar",
        r.estado_display,
        new Date(r.fecha_creacion).toLocaleDateString("es-CO"),
      ]),
      theme: "grid",
      headStyles: { fillColor: [30, 58, 95] },
      styles: { fontSize: 9 },
    });
    doc.save(`Reporte_General_${new Date().toISOString().split("T")[0]}.pdf`);
  };

  // ============ ¿Hay datos en gráficos? ============
  const hayDatosMes = porMes.length > 0 && porMes.some((d) => d.total > 0);
  const hayDatosTipo = porTipo.length > 0;

  return (
    <div className="dashboard-container">
      {/* ============ HEADER ============ */}
      <header className="dashboard-header">
        <div>
          <h1 className="titulo-pagina">
            Hola, {usuario?.nombre?.split(" ")[0] || "Usuario"} 👋
          </h1>
          <p className="subtitulo-pagina">
            Panorama general del sistema de reportes técnicos.
          </p>
        </div>
        <div className="dashboard-actions">
          <button onClick={exportarExcel} className="btn-export-sm btn-export-sm--excel">
            <FileSpreadsheet size={16} /> Excel
          </button>
          <button onClick={exportarPDF} className="btn-export-sm btn-export-sm--pdf">
            <FileDown size={16} /> PDF
          </button>
        </div>
      </header>

      {cargando ? (
        <div className="loading-state">Cargando panel de control...</div>
      ) : (
        <>
          {/* ============ KPIs ============ */}
          <div className="grid-kpis">
            <TarjetaKpi
              titulo="Total Reportes"
              valor={resumen?.total ?? 0}
              icono={<FileText size={24} />}
              color="#1e3a5f"
            />
            <TarjetaKpi
              titulo="Resueltos"
              valor={resumen?.resueltos ?? 0}
              icono={<CheckCircle size={24} />}
              color="#10b981"
            />
            <TarjetaKpi
              titulo="Pendientes"
              valor={resumen?.pendientes ?? 0}
              icono={<Clock size={24} />}
              color="#f59e0b"
            />
            <TarjetaKpi
              titulo="Críticos"
              valor={resumen?.criticos ?? 0}
              icono={<AlertTriangle size={24} />}
              color="#ef4444"
            />
          </div>

          {/* ============ GRÁFICOS ============ */}
          <div className="grid-charts">
            {/* Línea: Reportes por mes */}
            <div className="tarjeta chart-card">
              <h3>Reportes por mes</h3>
              <div className="chart-wrapper">
                {hayDatosMes ? (
                  <ResponsiveContainer width="100%" height={250}>
                    <LineChart data={porMes}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                      <XAxis dataKey="mes" axisLine={false} tickLine={false} tick={{ fill: "#64748b", fontSize: 12 }} />
                      <YAxis axisLine={false} tickLine={false} tick={{ fill: "#64748b", fontSize: 12 }} />
                      <Tooltip contentStyle={{ borderRadius: 8, border: "none", boxShadow: "0 4px 12px rgba(0,0,0,0.1)" }} />
                      <Line
                        type="monotone"
                        dataKey="total"
                        stroke="#1e3a5f"
                        strokeWidth={3}
                        dot={{ r: 5, fill: "#1e3a5f", strokeWidth: 2, stroke: "#fff" }}
                        activeDot={{ r: 7 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <EmptyChart texto="Aún no hay datos suficientes este mes." />
                )}
              </div>
            </div>

            {/* Pie: Distribución por tipo */}
            <div className="tarjeta chart-card">
              <h3>Distribución por tipo</h3>
              <div className="chart-wrapper pie-wrapper">
                {hayDatosTipo ? (
                  <>
                    <ResponsiveContainer width="100%" height={250}>
                      <PieChart>
                        <Pie
                          data={porTipo}
                          innerRadius={60}
                          outerRadius={80}
                          paddingAngle={5}
                          dataKey="total"
                          nameKey="tipo"
                        >
                          {porTipo.map((_, i) => (
                            <Cell key={i} fill={COLORES_PIE[i % COLORES_PIE.length]} />
                          ))}
                        </Pie>
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                    <div className="leyenda-circular">
                      {porTipo.map((item, i) => (
                        <div key={item.tipo} className="leyenda-item">
                          <span
                            className="dot"
                            style={{ backgroundColor: COLORES_PIE[i % COLORES_PIE.length] }}
                          />
                          <span>{item.tipo}</span>
                        </div>
                      ))}
                    </div>
                  </>
                ) : (
                  <EmptyChart texto="Sin datos por tipo." circular />
                )}
              </div>
            </div>
          </div>

          {/* ============ RANKING ============ */}
          <div className="tarjeta">
            <div className="tarjeta__encabezado">
              <h2>
                <Trophy size={20} /> Ranking de Técnicos
              </h2>
              <Link to="/ranking" className="enlace-ver-todos">
                Ver completo <ArrowUpRight size={14} />
              </Link>
            </div>
            <div className="ranking-list">
              {ranking.slice(0, 5).map((tecnico, index) => (
                <div key={tecnico.id} className="ranking-item">
                  <span className="ranking-posicion">
                    {index === 0 ? (
                      <Medal color="#f59e0b" />
                    ) : index === 1 ? (
                      <Medal color="#94a3b8" />
                    ) : index === 2 ? (
                      <Medal color="#a16207" />
                    ) : (
                      `#${index + 1}`
                    )}
                  </span>
                  <span className="ranking-nombre">{tecnico.nombre}</span>
                  <span className="ranking-puntos">
                    {tecnico.reportes_resueltos} resueltos
                  </span>
                </div>
              ))}
              {ranking.length === 0 && (
                <p className="sin-datos">Aún no hay datos de ranking.</p>
              )}
            </div>
          </div>

          {/* ============ REPORTES RECIENTES ============ */}
          <div className="tarjeta">
            <div className="tarjeta__encabezado">
              <h2>Reportes Recientes</h2>
              <Link to="/reportes" className="enlace-ver-todos">
                Ver todos <ArrowUpRight size={16} />
              </Link>
            </div>
            <div className="tabla-contenedor">
              <table className="tabla">
                <thead>
                  <tr>
                    <th>Código</th>
                    <th>Tipo</th>
                    <th>Área</th>
                    <th>Técnico Asignado</th>
                    <th>Estado</th>
                    <th>Fecha Creación</th>
                  </tr>
                </thead>
                <tbody>
                  {recientes.map((r) => (
                    <tr key={r.id}>
                      <td className="font-medium text-blue-600">
                        <Link to={`/reportes/${r.id}`}>{r.codigo}</Link>
                      </td>
                      <td>{r.tipo_tarea_display || "—"}</td>
                      <td>{r.area_nombre || "—"}</td>
                      <td>{r.tecnico_nombre || "Sin asignar"}</td>
                      <td>
                        <BadgeEstado estado={r.estado} texto={r.estado_display} />
                      </td>
                      <td className="text-gray-500">
                        {new Date(r.fecha_creacion).toLocaleDateString("es-CO")}
                      </td>
                    </tr>
                  ))}
                  {recientes.length === 0 && (
                    <tr>
                      <td colSpan={6} className="tabla__vacio">
                        <Inbox size={28} style={{ opacity: 0.4, marginBottom: 6 }} />
                        <div>Aún no hay reportes registrados.</div>
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

// ============================================================
// Tarjeta KPI
// ============================================================
function TarjetaKpi({ titulo, valor, icono, color }) {
  return (
    <div className="tarjeta-kpi" style={{ borderTopColor: color }}>
      <div className="kpi-header">
        <span className="kpi-icono" style={{ color, backgroundColor: `${color}15` }}>
          {icono}
        </span>
      </div>
      <div className="kpi-body">
        <span className="tarjeta-kpi__valor" style={{ color }}>
          {valor}
        </span>
        <span className="tarjeta-kpi__titulo">{titulo}</span>
      </div>
    </div>
  );
}

// ============================================================
// Gráfico vacío
// ============================================================
function EmptyChart({ texto, circular = false }) {
  if (circular) {
    return (
      <div className="empty-chart">
        <div className="empty-chart__circulo"></div>
        <p className="empty-chart__texto">{texto}</p>
      </div>
    );
  }
  return (
    <div className="empty-chart">
      <div className="empty-chart__linea"></div>
      <p className="empty-chart__texto">{texto}</p>
    </div>
  );
}