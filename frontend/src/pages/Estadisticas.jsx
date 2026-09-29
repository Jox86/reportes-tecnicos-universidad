// src/pages/Estadisticas.jsx
import { useEffect, useState } from "react";
import api from "../api/client";
import { BarChartReportes, LineChartReportes, PieChartModerno } from "../components/charts/Charts";
import { FileSpreadsheet, FileDown } from "lucide-react";
import * as XLSX from 'xlsx';
import jsPDF from 'jspdf';
import 'jspdf-autotable';

export default function Estadisticas() {
  const [filtros, setFiltros] = useState({ desde: "", hasta: "" });
  const [resumen, setResumen] = useState(null);
  const [porMes, setPorMes] = useState([]);
  const [porTipo, setPorTipo] = useState([]);
  const [porArea, setPorArea] = useState([]);
  const [porTecnico, setPorTecnico] = useState([]);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    cargarDatos();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filtros]);

  function cargarDatos() {
    setCargando(true);
    const params = {};
    if (filtros.desde) params.desde = filtros.desde;
    if (filtros.hasta) params.hasta = filtros.hasta;

    Promise.all([
      api.get("/estadisticas/resumen/", { params }),
      api.get("/estadisticas/por-mes/", { params }),
      api.get("/estadisticas/por-tipo/", { params }),
      api.get("/estadisticas/por-area/", { params }),
      api.get("/estadisticas/por-tecnico/", { params }),
    ])
      .then(([r1, r2, r3, r4, r5]) => {
        setResumen(r1.data);
        setPorMes(r2.data);
        setPorTipo(r3.data);
        setPorArea(r4.data);
        setPorTecnico(r5.data);
      })
      .finally(() => setCargando(false));
  }

  function exportarExcel() {
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet([resumen]), "Resumen");
    XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(porMes), "Por Mes");
    XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(porTipo), "Por Tipo");
    XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(porArea), "Por Área");
    XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(porTecnico), "Por Técnico");
    XLSX.writeFile(wb, `Estadisticas_${new Date().toISOString().split('T')[0]}.xlsx`);
  }

  function exportarPDF() {
    const doc = new jsPDF();
    doc.text("Reporte de Estadísticas", 14, 15);
    doc.autoTable({
      startY: 25,
      head: [['Métrica', 'Valor']],
      body: [
        ['Total', resumen.total],
        ['Pendientes', resumen.pendientes],
        ['En proceso', resumen.en_proceso],
        ['Resueltos', resumen.resueltos],
        ['Cerrados', resumen.cerrados],
        ['Tiempo prom. (h)', resumen.tiempo_promedio_resolucion_horas ?? "—"],
      ],
      theme: 'grid',
      headStyles: { fillColor: '#1e3a5f' }
    });
    doc.save(`Estadisticas_${new Date().toISOString().split('T')[0]}.pdf`);
  }

  return (
    <div>
      <div className="encabezado-lista">
        <div>
          <h1 className="titulo-pagina">Estadísticas</h1>
          <p className="subtitulo-pagina">Indicadores y tendencias del sistema de reportes.</p>
        </div>
        <div className="dashboard-actions">
          <button onClick={exportarExcel} className="btn btn--outline">
            <FileSpreadsheet size={16} /> Excel
          </button>
          <button onClick={exportarPDF} className="btn btn--outline">
            <FileDown size={16} /> PDF
          </button>
        </div>
      </div>

      <div className="tarjeta tarjeta--filtros">
        <label>
          Desde
          <input type="date" value={filtros.desde} onChange={(e) => setFiltros((f) => ({ ...f, desde: e.target.value }))} />
        </label>
        <label>
          Hasta
          <input type="date" value={filtros.hasta} onChange={(e) => setFiltros((f) => ({ ...f, hasta: e.target.value }))} />
        </label>
        {(filtros.desde || filtros.hasta) && (
          <button className="btn btn--fantasma" onClick={() => setFiltros({ desde: "", hasta: "" })}>
            Limpiar filtro
          </button>
        )}
      </div>

      {cargando ? (
        <p>Cargando estadísticas…</p>
      ) : (
        <>
          <div className="grid-kpis">
            <MiniKpi titulo="Total" valor={resumen.total} />
            <MiniKpi titulo="Pendientes" valor={resumen.pendientes} />
            <MiniKpi titulo="En proceso" valor={resumen.en_proceso} />
            <MiniKpi titulo="Resueltos" valor={resumen.resueltos} />
            <MiniKpi titulo="Cerrados" valor={resumen.cerrados} />
            <MiniKpi titulo="Tiempo prom. (h)" valor={resumen.tiempo_promedio_resolucion_horas ?? "—"} />
          </div>

          <div className="grid-graficos">
            <div className="tarjeta">
              <h2>Reportes por mes</h2>
              <LineChartReportes datos={porMes} />
            </div>

            <div className="tarjeta">
              <h2>Distribución por tipo de tarea</h2>
              <PieChartModerno datos={porTipo} dataKey="total" nameKey="tipo" />
            </div>

            <div className="tarjeta tarjeta--ancha">
              <h2>Reportes por área</h2>
              <BarChartReportes datos={porArea} dataKey="total" nameKey="area" barName="Reportes" />
            </div>

            {porTecnico.length > 0 && (
              <div className="tarjeta tarjeta--ancha">
                <h2>Carga y resolución por técnico</h2>
                <BarChartReportes datos={porTecnico} dataKey="total" nameKey="tecnico" barName="Asignados" />
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}

function MiniKpi({ titulo, valor }) {
  return (
    <div className="tarjeta-kpi tarjeta-kpi--mini">
      <span className="tarjeta-kpi__valor">{valor ?? "—"}</span>
      <span className="tarjeta-kpi__titulo">{titulo}</span>
    </div>
  );
}