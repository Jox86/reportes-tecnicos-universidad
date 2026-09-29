const COLORES = {
  pendiente: "#f59e0b",
  en_proceso: "#3b82f6",
  resuelto: "#22c55e",
  cerrado: "#6b7280",
};

export default function BadgeEstado({ estado, texto }) {
  const color = COLORES[estado] || "#6b7280";
  return (
    <span
      className="badge"
      style={{ backgroundColor: `${color}22`, color, borderColor: `${color}55` }}
    >
      {texto || estado}
    </span>
  );
}
