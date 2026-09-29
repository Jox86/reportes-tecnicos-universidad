// src/pages/Dashboard.jsx
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api/client";
import { useAuth } from "../context/AuthContext";
import BadgeEstado from "../components/BadgeEstado";
import { FileText, CheckCircle, Clock, AlertTriangle, FileSpreadsheet, FileDown, ArrowUpRight, ArrowDownRight, Trophy, Medal } from "lucide-react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import * as XLSX from 'xlsx';
import jsPDF from 'jspdf';
import 'jspdf-autotable';

export default function Dashboard() {
  const { usuario } = useAuth();
  const [resumen, setResumen] = useState(null);
  const [recientes, setRecientes] = useState([]);
  const [ranking, setRanking] = useState([]);
  const [cargando, setCargando] = useState(true);

  const dataGraficoLineas = [
    { name: 'Lun', reportes: 12 }, { name: 'Mar', reportes: 19 },
    { name: 'Mié', reportes: 15 }, { name: 'Jue', reportes: 22 },
    { name: 'Vie', reportes: 30 }, { name: 'Sáb', reportes: 10 },
    { name: 'Dom', reportes: 5 },
  ];

  const dataGraficoCircular = [
    { name: 'Hardware', value: 400, color: '#3b82f6' },
    { name: 'Software', value: 300, color: '#10b981' },
    { name: 'Redes', value: 300, color: '#f59e0b' },
    { name: 'Otros', value: 200, color: '#ef4444' },
  ];

  useEffect(() => {
    Promise.all([
      api.get("/estadisticas/resumen/"),
      api.get("/reportes/", { params: { ordering: "-fecha_creacion", page_size: 5 } }),
      api.get("/estadisticas/ranking/").catch(() => ({ data: [] })),
    ])
      .then(([r1, r2, r3]) => {
        setResumen(r1.data);
        setRecientes((r2.data.results || r2.data).slice(0, 5));
        setRanking(r3.data || []);
      })
      .catch(err => console.error("Error cargando dashboard", err))
      .finally(() => setCargando(false));
  }, []);

  const exportarExcel = () => {
    const ws = XLSX.utils.json_to_sheet(recientes);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Reportes Recientes");
    XLSX.writeFile(wb, `Reportes_${new Date().toISOString().split('T')[0]}.xlsx`);
  };

  const exportarPDF = () => {
    const doc = new jsPDF();
    doc.text("Reporte General de Incidentes", 14, 15);
    doc.autoTable({
      startY: 25,
      head: [['Código', 'Título', 'Área', 'Técnico', 'Estado', 'Fecha Creación']],
      body: recientes.map(r => [
        r.codigo, 
        r.titulo, 
        r.area_nombre, 
        r.tecnico_asignado_nombre || "Sin asignar",
        r.estado_display, 
        new Date(r.fecha_creacion).toLocaleDateString()
      ]),
      theme: 'grid',
      headStyles: { fillColor: '#1e3a5f' }
    });
    doc.save(`Reporte_${new Date().toISOString().split('T')[0]}.pdf`);
  };

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <div>
          <h1 className="titulo-pagina">Hola, {usuario?.nombre?.split(" ")[0] || "Usuario"} 👋</h1>
          <p className="subtitulo-pagina">Panorama general del sistema de reportes técnicos.</p>
        </div>
        <div className="dashboard-actions">
          <button onClick={exportarExcel} className="btn-export-sm btn-export-sm--excel" title="Exportar a Excel">
            <FileSpreadsheet size={16} /> Excel
          </button>
          <button onClick={exportarPDF} className="btn-export-sm btn-export-sm--pdf" title="Exportar a PDF">
            <FileDown size={16} /> PDF
          </button>
        </div>
      </header>

      {cargando ? (
        <div className="loading-state">Cargando panel de control...</div>
      ) : (
        <>
          <div className="grid-kpis">
            <TarjetaKpi titulo="Total Reportes" valor={resumen?.total || 0} icono={<FileText size={24} />} color="#1e3a5f" tendencia="+12%" />
            <TarjetaKpi titulo="Resueltos" valor={resumen?.resueltos || 0} icono={<CheckCircle size={24} />} color="#10b981" tendencia="+8%" />
            <TarjetaKpi titulo="Pendientes" valor={resumen?.pendientes || 0} icono={<Clock size={24} />} color="#f59e0b" tendencia="-5%" negativa />
            <TarjetaKpi titulo="Críticos" valor={resumen?.criticos || 0} icono={<AlertTriangle size={24} />} color="#ef4444" tendencia="+2%" negativa />
          </div>

          <div className="grid-charts">
            <div className="tarjeta chart-card">
              <h3>Reportes últimos 7 días</h3>
              <div className="chart-wrapper">
                <ResponsiveContainer width="100%" height={250}>
                  <LineChart data={dataGraficoLineas}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                    <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 12}} />
                    <YAxis axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 12}} />
                    <Tooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }} />
                    <Line type="monotone" dataKey="reportes" stroke="#3b82f6" strokeWidth={3} dot={{r: 4, fill: '#3b82f6', strokeWidth: 2, stroke: '#fff'}} activeDot={{r: 6}} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="tarjeta chart-card">
              <h3>Distribución por tipo</h3>
              <div className="chart-wrapper pie-wrapper">
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie data={dataGraficoCircular} innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                      {dataGraficoCircular.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
                <div className="leyenda-circular">
                  {dataGraficoCircular.map(item => (
                    <div key={item.name} className="leyenda-item">
                      <span className="dot" style={{backgroundColor: item.color}}></span>
                      <span>{item.name}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Ranking de Técnicos */}
          <div className="tarjeta">
            <div className="tarjeta__encabezado">
              <h2><Trophy size={20} /> Ranking de Técnicos</h2>
            </div>
            <div className="ranking-list">
              {ranking.map((tecnico, index) => (
                <div key={tecnico.id} className="ranking-item">
                  <span className="ranking-posicion">
                    {index === 0 ? <Medal color="gold" /> : index === 1 ? <Medal color="silver" /> : index === 2 ? <Medal color="brown" /> : `#${index + 1}`}
                  </span>
                  <span className="ranking-nombre">{tecnico.nombre}</span>
                  <span className="ranking-puntos">{tecnico.reportes_resueltos} resueltos</span>
                </div>
              ))}
              {ranking.length === 0 && <p className="sin-datos">Aún no hay datos de ranking.</p>}
            </div>
          </div>

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
                    <th>Título</th>
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
                      <td>{r.titulo}</td>
                      <td>{r.area_nombre}</td>
                      <td>{r.tecnico_asignado_nombre || "Sin asignar"}</td>
                      <td><BadgeEstado estado={r.estado} texto={r.estado_display} /></td>
                      <td className="text-gray-500">{new Date(r.fecha_creacion).toLocaleDateString("es-CO")}</td>
                    </tr>
                  ))}
                  {recientes.length === 0 && (
                    <tr><td colSpan={6} className="tabla__vacio">Aún no hay reportes registrados.</td></tr>
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
// Componente: Tarjeta KPI estilo RPG
// ============================================================
function TarjetaKpi({ titulo, valor, icono, color, tendencia, negativa, tier }) {
  return (
    <div className={`kpi-medieval kpi-medieval--${tier}`} style={{ "--kpi-color": color }}>
      <div className="kpi-medieval__glow" />
      <div className="kpi-medieval__header">
        <span className="kpi-medieval__icon">{icono}</span>
        {tendencia && (
          <span className={`kpi-medieval__tendencia ${negativa ? "negativa" : "positiva"}`}>
            {negativa ? <ArrowDownRight size={12} /> : <ArrowUpRight size={12} />}
            {tendencia}
          </span>
        )}
      </div>
      <div className="kpi-medieval__body">
        <span className="kpi-medieval__valor">{valor ?? "—"}</span>
        <span className="kpi-medieval__titulo">{titulo}</span>
      </div>
      <div className="kpi-medieval__barra">
        <div className="kpi-medieval__barra-fill" />
      </div>
    </div>
  );
}