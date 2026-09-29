# apps/exports/pdf.py
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def generar_pdf_reporte_individual(reporte):
    """Genera un PDF detallado de un reporte individual."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Título
    story.append(Paragraph(f"<b>Reporte {reporte.codigo}</b>", styles["Title"]))
    story.append(Spacer(1, 12))

    # Tabla de información general
    datos = [
        ["Campo", "Valor"],
        ["Tipo de Tarea", reporte.tipo_tarea.nombre if reporte.tipo_tarea else "—"],
        ["Área", reporte.area.nombre if reporte.area else "—"],
        ["Ubicación", reporte.ubicacion or "—"],
        ["Usuario Afectado", reporte.usuario_nombre or "—"],
        ["Correo", reporte.usuario_correo or "—"],
        ["Cargo", reporte.usuario_cargo or "—"],
        ["Prioridad", reporte.get_prioridad_display()],
        ["Estado", reporte.get_estado_display()],
        ["Técnico Asignado", reporte.tecnico_nombre or "Sin asignar"],
        ["Creado por", reporte.creado_por_nombre],
        ["Fecha Creación", reporte.fecha_creacion.strftime("%d/%m/%Y %H:%M") if reporte.fecha_creacion else "—"],
        ["Fecha Resolución", reporte.fecha_resolucion.strftime("%d/%m/%Y %H:%M") if reporte.fecha_resolucion else "—"],
        ["Tiempo (h)", str(reporte.tiempo_resolucion_horas or "—")],
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

    # Equipos
    if reporte.equipos.exists():
        story.append(Paragraph("<b>Equipos / Activos</b>", styles["Heading3"]))
        story.append(Spacer(1, 8))
        eq_data = [["Código", "Marca", "Modelo", "Serie"]]
        for eq in reporte.equipos.all():
            eq_data.append([
                eq.codigo_activo or "—",
                eq.marca or "—",
                eq.modelo or "—",
                eq.serie or "—",
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

    # Descripción
    story.append(Paragraph("<b>Descripción del Problema</b>", styles["Heading3"]))
    story.append(Spacer(1, 6))
    story.append(Paragraph(reporte.descripcion or "—", styles["BodyText"]))
    story.append(Spacer(1, 16))

    # Solución
    story.append(Paragraph("<b>Solución / Notas Técnicas</b>", styles["Heading3"]))
    story.append(Spacer(1, 6))
    story.append(Paragraph(reporte.solucion or "Sin registrar aún.", styles["BodyText"]))
    story.append(Spacer(1, 16))

    # Historial
    if reporte.historial.exists():
        story.append(Paragraph("<b>Historial de Estados</b>", styles["Heading3"]))
        story.append(Spacer(1, 8))
        h_data = [["Fecha", "De", "A", "Usuario", "Comentario"]]
        for h in reporte.historial.all().order_by("fecha"):
            h_data.append([
                h.fecha.strftime("%d/%m/%Y %H:%M"),
                h.estado_anterior or "—",
                h.estado_nuevo,
                (h.usuario.get_full_name() or h.usuario.username) if h.usuario else "Sistema",
                (h.comentario or "—")[:60],
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


# Alias para compatibilidad con el views.py actual
generar_pdf_reporte = generar_pdf_reporte_individual