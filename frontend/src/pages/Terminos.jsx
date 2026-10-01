// src/pages/Terminos.jsx
import { ArrowLeft, FileText, Users, Shield, AlertCircle, Clock } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";

export default function Terminos() {
  const navigate = useNavigate();
  const ultimaActualizacion = "01 de octubre de 2026";

  return (
    <div className="legal-page">
      <button className="btn-atras" onClick={() => navigate(-1)}>
        <ArrowLeft size={16} /> Volver
      </button>

      <header className="legal-header">
        <div className="legal-header__icon">
          <FileText size={32} />
        </div>
        <h1>Términos y Condiciones de Uso</h1>
        <p className="legal-header__subtitulo">
          <strong>Sistema de Reportes Técnicos</strong>
        </p>
        <p className="legal-header__meta">
          <Clock size={14} /> Última actualización: {ultimaActualizacion}
        </p>
      </header>

      <div className="legal-content">
        {/* 1. Aceptación */}
        <section>
          <h2><Shield size={20} /> 1. Aceptación de los Términos</h2>
          <p>
            El acceso y uso del <strong>Sistema de Reportes Técnicos</strong> implica la
            aceptación plena e incondicional de los presentes Términos y Condiciones.
            Si el usuario no está de acuerdo con alguno de ellos, debe abstenerse de utilizar
            el sistema.
          </p>
        </section>

        {/* 2. Objeto */}
        <section>
          <h2><FileText size={20} /> 2. Objeto del Sistema</h2>
          <p>El sistema tiene como objeto:</p>
          <ul>
            <li>Registrar y gestionar reportes técnicos e incidentes</li>
            <li>Asignar tareas a técnicos responsables</li>
            <li>Dar seguimiento a la resolución de los reportes</li>
            <li>Generar estadísticas internas de desempeño</li>
          </ul>
        </section>

        {/* 3. Acceso */}
        <section>
          <h2><Users size={20} /> 3. Acceso al Sistema</h2>
          <p>
            El acceso está restringido a usuarios autorizados por la Dirección de Innovación
            Digital. Las credenciales son personales e intransferibles.
          </p>
          <p>
            El usuario es responsable de mantener la confidencialidad de su contraseña y de
            notificar de inmediato cualquier uso no autorizado.
          </p>
        </section>

        {/* 4. Uso aceptable */}
        <section>
          <h2><Shield size={20} /> 4. Uso Aceptable</h2>
          <p>El usuario se compromete a:</p>
          <ul>
            <li>Proporcionar información veraz, completa y actualizada</li>
            <li>Utilizar el sistema exclusivamente para fines institucionales</li>
            <li>No compartir credenciales con terceros</li>
            <li>No realizar acciones que comprometan la seguridad del sistema</li>
            <li>Reportar incidentes de seguridad al administrador</li>
          </ul>
        </section>

        {/* 5. Usos prohibidos */}
        <section>
          <h2><AlertCircle size={20} /> 5. Usos Prohibidos</h2>
          <p>Queda expresamente prohibido:</p>
          <ul>
            <li>Utilizar el sistema para fines distintos a los institucionales</li>
            <li>Intentar acceder a cuentas o datos de otros usuarios</li>
            <li>Introducir código malicioso o realizar ataques informáticos</li>
            <li>Reproducir, distribuir o modificar el sistema sin autorización</li>
            <li>Utilizar los datos para fines comerciales o personales</li>
          </ul>
        </section>

        {/* 6. Propiedad intelectual */}
        <section>
          <h2><FileText size={20} /> 6. Propiedad Intelectual</h2>
          <p>
            El Sistema de Reportes Técnicos y todos sus componentes (código, diseño, contenido)
            son propiedad de la Dirección de Innovación Digital o de sus respectivos autores.
            No se concede ninguna licencia de uso fuera del alcance institucional.
          </p>
        </section>

        {/* 7. Responsabilidad */}
        <section>
          <h2><AlertCircle size={20} /> 7. Limitación de Responsabilidad</h2>
          <p>
            La Dirección de Innovación Digital no se hace responsable por:
          </p>
          <ul>
            <li>Daños derivados del uso indebido del sistema</li>
            <li>Interrupciones del servicio por causas técnicas o de fuerza mayor</li>
            <li>Pérdida de datos por causas externas al sistema</li>
            <li>Uso de credenciales por parte de terceros no autorizados</li>
          </ul>
        </section>

        {/* 8. Modificaciones */}
        <section>
          <h2><FileText size={20} /> 8. Modificaciones</h2>
          <p>
            Nos reservamos el derecho de modificar el sistema, sus funcionalidades o estos
            Términos y Condiciones en cualquier momento. Los cambios serán notificados a
            través del sistema.
          </p>
        </section>

        {/* 9. Suspensión */}
        <section>
          <h2><Shield size={20} /> 9. Suspensión de Cuenta</h2>
          <p>
            La Dirección de Innovación Digital podrá suspender o cancelar el acceso de
            cualquier usuario que incumpla estos Términos y Condiciones, sin previo aviso.
          </p>
        </section>

        {/* 10. Legislación */}
        <section>
          <h2><Shield size={20} /> 10. Legislación Aplicable</h2>
          <p>
            Estos Términos y Condiciones se rigen por las leyes de la República de Colombia y,
            en lo aplicable, por las normativas internas de la institución.
          </p>
        </section>

        {/* 11. Contacto */}
        <section>
          <h2><Users size={20} /> 11. Contacto</h2>
          <p>Para consultas sobre estos Términos y Condiciones:</p>
          <ul>
            <li>
              <strong>Correo:</strong>{" "}
              <a href="mailto:innovacion.did@iris.uh.cu">innovacion.did@iris.uh.cu</a>
            </li>
          </ul>
        </section>

        <div className="legal-actions">
          <Link to="/privacidad" className="btn btn--secundario">
            Ver Política de Privacidad
          </Link>
        </div>
      </div>
    </div>
  );
}