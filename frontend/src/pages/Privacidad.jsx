// src/pages/Privacidad.jsx
import { ArrowLeft, Shield, Database, Users, Mail, Trash2, FileText, Clock } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";

export default function Privacidad() {
  const navigate = useNavigate();
  const ultimaActualizacion = "01 de octubre de 2026";

  return (
    <div className="legal-page">
      <button className="btn-atras" onClick={() => navigate(-1)}>
        <ArrowLeft size={16} /> Volver
      </button>

      <header className="legal-header">
        <div className="legal-header__icon">
          <Shield size={32} />
        </div>
        <h1>Política de Privacidad y Tratamiento de Datos Personales</h1>
        <p className="legal-header__subtitulo">
          <strong>Sistema de Reportes Técnicos</strong>
        </p>
        <p className="legal-header__meta">
          <Clock size={14} /> Última actualización: {ultimaActualizacion}
        </p>
      </header>

      <div className="legal-content">
        {/* 1. Responsable */}
        <section>
          <h2><Users size={20} /> 1. Responsable del Tratamiento</h2>
          <p>
            El responsable del tratamiento de los datos personales recolectados a través del
            <strong> Sistema de Reportes Técnicos</strong> es:
          </p>
          <ul>
            <li><strong>Entidad:</strong> Departamento de Desarrollo y Soporte — Dirección de Innovación Digital</li>
            <li><strong>Correo de contacto:</strong> <a href="mailto:innovacion.did@iris.uh.cu">innovacion.did@iris.uh.cu</a></li>
            <li><strong>Finalidad:</strong> Gestión de reportes técnicos, incidentes y solicitudes de mantenimiento institucional</li>
          </ul>
        </section>

        {/* 2. Datos recolectados */}
        <section>
          <h2><Database size={20} /> 2. Datos Personales Recolectados</h2>
          <p>El sistema recolecta las siguientes categorías de datos personales:</p>

          <h3>2.1. Datos de los usuarios del sistema</h3>
          <ul>
            <li>Nombre completo</li>
            <li>Correo institucional</li>
            <li>Cargo o dependencia</li>
            <li>Rol asignado en el sistema (Administrador, Técnico, Auditor)</li>
            <li>Fecha de último inicio de sesión</li>
            <li>Historial de acciones realizadas (auditoría de cambios en reportes)</li>
          </ul>

          <h3>2.2. Datos de los reportes técnicos</h3>
          <ul>
            <li>Usuario afectado: nombre, correo y cargo</li>
            <li>Área y ubicación del incidente</li>
            <li>Datos de equipos: código de activo, marca, modelo, número de serie</li>
            <li>Descripción del problema o tarea</li>
            <li>Solución aplicada</li>
            <li>Archivos adjuntos (si el usuario los proporciona)</li>
          </ul>
        </section>

        {/* 3. Finalidad */}
        <section>
          <h2><FileText size={20} /> 3. Finalidad del Tratamiento</h2>
          <p>Los datos personales recolectados serán utilizados exclusivamente para:</p>
          <ul>
            <li>Gestionar y dar seguimiento a los reportes técnicos</li>
            <li>Asignar tareas a técnicos y notificar cambios de estado</li>
            <li>Generar estadísticas internas de desempeño y tiempos de resolución</li>
            <li>Mantener un historial de auditoría de cambios y acciones</li>
            <li>Cumplir con obligaciones institucionales y legales aplicables</li>
          </ul>
          <p><strong>Los datos NO serán utilizados para fines comerciales, publicitarios ni de perfilamiento.</strong></p>
        </section>

        {/* 4. Terceros */}
        <section>
          <h2><Shield size={20} /> 4. Transferencia a Terceros</h2>
          <p>
            Para el funcionamiento técnico del sistema, los datos son procesados por los
            siguientes proveedores de servicios en la nube:
          </p>
          <ul>
            <li><strong>Supabase</strong> (base de datos PostgreSQL) — Estados Unidos 🇺🇸</li>
            <li><strong>Railway</strong> (hosting del backend) — Estados Unidos 🇺🇸</li>
            <li><strong>Netlify</strong> (hosting del frontend) — Estados Unidos 🇺🇸</li>
            <li><strong>Brevo</strong> (envío de correos transaccionales, si se activa) — Francia 🇫🇷</li>
          </ul>
          <p>
            Estos proveedores cuentan con sus propias políticas de privacidad y medidas de
            seguridad. No se comparten datos con terceros para fines distintos a los aquí descritos.
          </p>
        </section>

        {/* 5. IA */}
        <section>
          <h2><Shield size={20} /> 5. Uso de Inteligencia Artificial</h2>
          <p>
            <strong>Este sistema no utiliza inteligencia artificial</strong> para el procesamiento,
            clasificación ni análisis automático de los datos personales de los usuarios.
            Toda clasificación y gestión de reportes se realiza de forma manual por el personal
            autorizado.
          </p>
        </section>

        {/* 6. Retención */}
        <section>
          <h2><Clock size={20} /> 6. Tiempo de Retención</h2>
          <p>Los datos personales serán conservados:</p>
          <ul>
            <li><strong>Mientras la cuenta del usuario esté activa</strong></li>
            <li>
              Tras la eliminación de la cuenta, los datos serán anonimizados o eliminados en un
              plazo máximo de 30 días, salvo obligación legal de conservarlos por más tiempo.
            </li>
          </ul>
        </section>

        {/* 7. Derechos del usuario */}
        <section>
          <h2><Users size={20} /> 7. Derechos del Titular de los Datos</h2>
          <p>
            De conformidad con la <strong>Ley 1581 de 2012</strong> y el <strong>Decreto 1377 de 2013</strong>
            de la República de Colombia, el titular de los datos personales tiene derecho a:
          </p>
          <ul>
            <li><strong>Conocer</strong> los datos personales que sobre él reposan en el sistema</li>
            <li><strong>Actualizar y rectificar</strong> sus datos cuando sean inexactos o incompletos</li>
            <li><strong>Solicitar prueba</strong> de la autorización otorgada</li>
            <li><strong>Ser informado</strong> sobre el uso que se ha dado a sus datos</li>
            <li><strong>Presentar quejas</strong> ante la autoridad competente por infracciones</li>
            <li>
              <strong>Revocar la autorización y/o solicitar la eliminación</strong> de sus datos,
              siempre que no exista un deber legal o contractual de conservarlos
            </li>
            <li><strong>Acceder de forma gratuita</strong> a sus datos personales</li>
          </ul>

          <h3>Cómo ejercer sus derechos</h3>
          <p>El usuario puede ejercer estos derechos de las siguientes formas:</p>
          <ul>
            <li>
              <strong>Eliminación de cuenta:</strong> desde su perfil en el sistema,
              mediante el botón <em>"Eliminar mi cuenta"</em>
            </li>
            <li>
              <strong>Otras solicitudes:</strong> enviando un correo a{" "}
              <a href="mailto:innovacion.did@iris.uh.cu">innovacion.did@iris.uh.cu</a>
            </li>
          </ul>
        </section>

        {/* 8. Seguridad */}
        <section>
          <h2><Shield size={20} /> 8. Medidas de Seguridad</h2>
          <p>El sistema implementa las siguientes medidas de seguridad:</p>
          <ul>
            <li>Conexiones cifradas mediante HTTPS/TLS</li>
            <li>Autenticación mediante tokens JWT con expiración</li>
            <li>Contraseñas almacenadas con hash seguro (PBKDF2)</li>
            <li>Control de acceso basado en roles (RBAC)</li>
            <li>Registro de auditoría de acciones críticas</li>
            <li>Respaldos periódicos de la base de datos</li>
          </ul>
        </section>

        {/* 9. Cookies */}
        <section>
          <h2><Database size={20} /> 9. Uso de Cookies y Almacenamiento Local</h2>
          <p>
            Este sistema utiliza <strong>almacenamiento local del navegador (localStorage)</strong>{" "}
            para guardar los tokens de autenticación JWT y las preferencias de tema (claro/oscuro).
            No se utilizan cookies de rastreo, publicidad ni analítica de terceros.
          </p>
        </section>

        {/* 10. Cambios */}
        <section>
          <h2><FileText size={20} /> 10. Cambios en esta Política</h2>
          <p>
            Nos reservamos el derecho de modificar esta Política de Privacidad en cualquier
            momento. Cualquier cambio será notificado a través del sistema y publicado en esta
            página con la fecha de actualización correspondiente.
          </p>
        </section>

        {/* 11. Aceptación */}
        <section>
          <h2><Shield size={20} /> 11. Aceptación</h2>
          <p>
            Al utilizar el Sistema de Reportes Técnicos, el usuario declara haber leído,
            entendido y aceptado los términos de esta Política de Privacidad.
          </p>
        </section>

        <div className="legal-actions">
          <Link to="/terminos" className="btn btn--secundario">
            Ver Términos y Condiciones
          </Link>
        </div>
      </div>
    </div>
  );
}