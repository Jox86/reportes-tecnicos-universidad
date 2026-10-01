// src/components/LegalFooter.jsx
import { Link } from "react-router-dom";
import { Shield, FileText } from "lucide-react";

export default function LegalFooter() {
  return (
    <footer className="legal-footer">
      <div className="legal-footer__contenido">
        <span className="legal-footer__copy">
          © {new Date().getFullYear()} Dirección de Innovación Digital — Todos los derechos reservados.
        </span>
        <div className="legal-footer__links">
          <Link to="/privacidad">
            <Shield size={14} /> Privacidad
          </Link>
          <Link to="/terminos">
            <FileText size={14} /> Términos
          </Link>
        </div>
      </div>
    </footer>
  );
}