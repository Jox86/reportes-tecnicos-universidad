import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const PALETA = ["#1e3a5f", "#3b82f6", "#22c55e", "#f59e0b", "#ef4444", "#8b5cf6", "#06b6d4", "#ec4899"];

export function LineChartReportes({ datos }) {
  if (!datos?.length) return <SinDatos />;
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={datos} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis dataKey="mes" tick={{ fontSize: 12 }} />
        <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
        <Tooltip />
        <Line
          type="monotone"
          dataKey="total"
          name="Reportes"
          stroke="#1e3a5f"
          strokeWidth={3}
          dot={{ r: 4, fill: "#1e3a5f" }}
          activeDot={{ r: 6 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}

export function PieChartModerno({ datos, dataKey = "total", nameKey = "tipo" }) {
  if (!datos?.length) return <SinDatos />;
  return (
    <ResponsiveContainer width="100%" height={320}>
      <PieChart>
        <Pie
          data={datos}
          dataKey={dataKey}
          nameKey={nameKey}
          cx="50%"
          cy="50%"
          innerRadius={70}
          outerRadius={110}
          paddingAngle={3}
          cornerRadius={8}
        >
          {datos.map((_, i) => (
            <Cell key={i} fill={PALETA[i % PALETA.length]} stroke="#fff" strokeWidth={2} />
          ))}
        </Pie>
        <Tooltip />
        <Legend verticalAlign="bottom" height={48} wrapperStyle={{ fontSize: 12 }} />
      </PieChart>
    </ResponsiveContainer>
  );
}

export function BarChartReportes({ datos, dataKey = "total", nameKey = "area", barName = "Total" }) {
  if (!datos?.length) return <SinDatos />;
  return (
    <ResponsiveContainer width="100%" height={320}>
      <BarChart data={datos} margin={{ top: 10, right: 20, left: -10, bottom: 30 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis dataKey={nameKey} tick={{ fontSize: 11 }} angle={-20} textAnchor="end" interval={0} />
        <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
        <Tooltip />
        <Bar dataKey={dataKey} name={barName} fill="#3b82f6" radius={[6, 6, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

function SinDatos() {
  return <div className="sin-datos">Sin datos suficientes para graficar todavía.</div>;
}
