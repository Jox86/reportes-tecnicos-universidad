import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function ProtectedRoute({ children, rolesPermitidos }) {
  const { usuario, cargando } = useAuth();

  if (cargando) {
    return <div className="pantalla-carga">Cargando…</div>;
  }
  if (!usuario) {
    return <Navigate to="/login" replace />;
  }
  if (rolesPermitidos && !usuario.is_superuser) {
    const tieneAcceso = usuario.roles.some((r) => rolesPermitidos.includes(r));
    if (!tieneAcceso) {
      return <Navigate to="/" replace />;
    }
  }
  return children;
}
