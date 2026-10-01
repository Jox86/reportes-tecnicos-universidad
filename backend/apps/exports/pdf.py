# apps/exports/pdf.py
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def _pdf_text(value):
    """Escapa texto controlado por usuarios antes de pasarlo a ReportLab Paragraph."""
    return escape(str(value or "—"), {"'": "&apos;", '"': "&quot;"})


def generar_pdf_reporte_individual(reporte):
    """Genera un PDF detallado de un reporte individual."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(f"<b>Reporte {_pdf_text(reporte.codigo)}</b>", styles["Title"]))
    story.append(Spacer(1, 12))

    datos = [
        ["Campo", "Valor"],
        ["Tipo de Tarea", _pdf_text(reporte.tipo_tarea.nombre if reporte.tipo_tarea else "—")],
        ["Área", _pdf_text(reporte.area.nombre if reporte.area else "—")],
        ["Ubicación", _pdf_text(reporte.ubicacion)],
        ["Usuario Afectado", _pdf_text(reporte.usuario_nombre)],
        ["Correo", _pdf_text(reporte.usuario_correo)],
        ["Cargo", _pdf_text(reporte.usuario_cargo)],
        ["Prioridad", _pdf_text(reporte.get_prioridad_display())],
        ["Estado", _pdf_text(reporte.get_estado_display())],
        ["Técnico Asignado", _pdf_text(reporte.tecnico_nombre or "Sin asignar")],
        ["Creado por", _pdf_text(reporte.creado_por_nombre)],
        ["Fecha Creación", _pdf_text(reporte.fecha_creacion.strftime("%d/%m/%Y %H:%M") if reporte.fecha_creacion else "—")],
        ["Fecha Resolución", _pdf_text(reporte.fecha_resolucion.strftime("%d/%m/%Y %H:%M") if reporte.fecha_resolucion else "—")],
        ["Tiempo (h)", _pdf_text(reporte.tiempo_resolucion_horas)],
    ]
    tabla = Table(datos, colWidths=[130, 370])
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a5f")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 1), (0, -1), colors.HexColor("#f2f4f7")),
    ]))
    story.append(tabla)
    story.append(Spacer(1, 20))

    if reporte.equipos.exists():
        story.append(Paragraph("<b>Equipos / Activos</b>", styles["Heading3"]))
        story.append(Spacer(1, 8))
        eq_data = [["Código", "Marca", "Modelo", "Serie"]]
        for eq in reporte.equipos.all():
            eq_data.append([
                _pdf_text(eq.codigo_activo),
                _pdf_text(eq.marca),
                _pdf_text(eq.modelo),
                _pdf_text(eq.serie),
            ])
        eq_tabla = Table(eq_data)
        eq_tabla.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a5f")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(eq_tabla)
        story.append(Spacer(1, 20))

    story.append(Paragraph("<b>Descripción del Problema</b>", styles["Heading3"]))
    story.append(Spacer(1, 6))
    story.append(Paragraph(_pdf_text(reporte.descripcion), styles["BodyText"]))
    story.append(Spacer(1, 16))

    story.append(Paragraph("<b>Solución / Notas Técnicas</b>", styles["Heading3"]))
    story.append(Spacer(1, 6))
    story.append(Paragraph(_pdf_text(reporte.solucion or "Sin registrar aún."), styles["BodyText"]))
    story.append(Spacer(1, 16))

    if reporte.historial.exists():
        story.append(Paragraph("<b>Historial de Estados</b>", styles["Heading3"]))
        story.append(Spacer(1, 8))
        h_data = [["Fecha", "De", "A", "Usuario", "Comentario"]]
        for h in reporte.historial.all().order_by("fecha"):
            h_data.append([
                _pdf_text(h.fecha.strftime("%d/%m/%Y %H:%M")),
                _pdf_text(h.estado_anterior),
                _pdf_text(h.estado_nuevo),
                _pdf_text((h.usuario.get_full_name() or h.usuario.username) if h.usuario else "Sistema"),
                _pdf_text((h.comentario or "—")[:60]),
            ])
        h_tabla = Table(h_data, colWidths=[80, 60, 60, 100, 200])
        h_tabla.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a5f")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
        ]))
        story.append(h_tabla)

    doc.build(story)
    buffer.seek(0)
    return buffer


generar_pdf_reporte = generar_pdf_reporte_individual
