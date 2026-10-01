// src/components/ModalEliminarCuenta.jsx
import { useState } from "react";
import { AlertTriangle, X } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

export default function ModalEliminarCuenta({ abierto, onClose }) {
  const { eliminarCuenta } = useAuth();
  const navigate = useNavigate();
  const [confirmacion, setConfirmacion] = useState("");
  const [procesando, setProcesando] = useState(false);

  const palabraConfirmacion = "ELIMINAR";

  async function handleEliminar() {
    if (confirmacion !== palabraConfirmacion) return;
    setProcesando(true);
    try {
      await eliminarCuenta();
      navigate("/login", { replace: true });
    } catch (err) {
      alert("No se pudo eliminar la cuenta. Contacta al administrador.");
      setProcesando(false);
    }
  }

  if (!abierto) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-eliminar" onClick={(e) => e.stopPropagation()}>
        <div className="modal-eliminar__header">
          <div className="modal-eliminar__icon">
            <AlertTriangle size={28} />
          </div>
          <h2>¿Eliminar tu cuenta?</h2>
          <button className="modal-eliminar__cerrar" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <div className="modal-eliminar__body">
          <p><strong>Esta acción es irreversible.</strong> Al eliminar tu cuenta:</p>
          <ul>
            <li>Tus datos personales serán anonimizados</li>
            <li>Los reportes que creaste conservarán su información</li>
            <li>No podrás volver a iniciar sesión con este usuario</li>
            <li>Perderás acceso al sistema permanentemente</li>
          </ul>

          <label>
            Escribe <strong>{palabraConfirmacion}</strong> para confirmar:
            <input
              type="text"
              value={confirmacion}
              onChange={(e) => setConfirmacion(e.target.value.toUpperCase())}
              placeholder={palabraConfirmacion}
            />
          </label>
        </div>

        <div className="modal-eliminar__acciones">
          <button className="btn btn--fantasma" onClick={onClose} disabled={procesando}>
            Cancelar
          </button>
          <button
            className="btn btn--peligro"
            onClick={handleEliminar}
            disabled={confirmacion !== palabraConfirmacion || procesando}
          >
            {procesando ? "Eliminando…" : "Eliminar cuenta"}
          </button>
        </div>
      </div>
    </div>
  );
}