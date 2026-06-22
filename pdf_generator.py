"""
Flotilla Control — Generador de Reportes PDF.
Genera reportes de gastos profesionales en formato PDF utilizando ReportLab.
"""

import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def format_db_date(date_str):
    """Convierte una fecha en formato YYYY-MM-DD a DD/MM/AAAA."""
    if not date_str:
        return ""
    try:
        return datetime.datetime.strptime(date_str, "%Y-%m-%d").strftime("%d/%m/%Y")
    except Exception:
        return date_str

def generate_report_pdf(filename, mode, selected_name, date_from_db, date_to_db, rows):
    """
    Genera un archivo PDF con el reporte de gastos en base a los filtros aplicados.
    
    :param filename: Ruta completa donde guardar el archivo PDF.
    :param mode: 'vehiculo' o 'conductor'.
    :param selected_name: Nombre del vehículo o conductor seleccionado.
    :param date_from_db: Rango de fecha inicio de la BD (YYYY-MM-DD o None).
    :param date_to_db: Rango de fecha fin de la BD (YYYY-MM-DD o None).
    :param rows: Lista de filas de gastos.
    """
    # 1. Configurar documento
    # Ancho carta: 612pt, alto carta: 792pt. Margen de 54pt (0.75 in). Ancho imprimible = 504pt.
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    # 2. Configurar estilos
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#1E3A8A'),
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#3B82F6'),
        spaceAfter=15
    )
    
    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#4B5563')
    )
    
    cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=11,
        textColor=colors.HexColor('#1F2937')
    )
    
    cell_bold_style = ParagraphStyle(
        'TableCellBold',
        parent=cell_style,
        fontName='Helvetica-Bold'
    )
    
    header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12,
        textColor=colors.white
    )
    
    total_label_style = ParagraphStyle(
        'TotalLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#064E3B')
    )
    
    total_val_style = ParagraphStyle(
        'TotalVal',
        parent=total_label_style,
        alignment=2 # Alineado a la derecha
    )

    story = []
    
    # Título principal
    story.append(Paragraph("Reporte Flotilla", title_style))
    
    # Subtítulo (Vehículo o Conductor)
    if mode == 'vehiculo':
        story.append(Paragraph(f"Vehículo: {selected_name}", subtitle_style))
    else:
        story.append(Paragraph(f"Conductor: {selected_name}", subtitle_style))
        
    # Metadatos del reporte (Fechas de rango y generación)
    now_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    
    date_from_disp = format_db_date(date_from_db)
    date_to_disp = format_db_date(date_to_db)
    
    date_filter_str = "Todos los registros"
    if date_from_disp and date_to_disp:
        date_filter_str = f"Desde {date_from_disp} hasta {date_to_disp}"
    elif date_from_disp:
        date_filter_str = f"Desde {date_from_disp}"
    elif date_to_disp:
        date_filter_str = f"Hasta {date_to_disp}"
        
    meta_html = f"<b>Período:</b> {date_filter_str} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Generado el:</b> {now_str}"
    story.append(Paragraph(meta_html, meta_style))
    story.append(Spacer(1, 15))
    
    # Resumen rápido (Cards estilo PDF)
    total_spent = sum(r[5] for r in rows)
    expense_count = len([r for r in rows if r[5] > 0])
    
    summary_data = [
        [
            Paragraph(f"<b>💰 Total Gastado:</b> ${total_spent:,.2f}", cell_bold_style),
            Paragraph(f"<b>📝 Número de Gastos:</b> {expense_count}", cell_bold_style)
        ]
    ]
    summary_table = Table(summary_data, colWidths=[252, 252])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F3F4F6')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#E5E7EB')),
        ('PADDING', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 20))
    
    # Tabla de gastos
    # Headers cambian según el modo
    if mode == 'vehiculo':
        headers = ["Fecha", "Categoría", "Concepto", "Conductor", "Monto"]
        # Col widths: Fecha=70, Categoria=90, Concepto=174, Conductor=100, Monto=70 => total 504
        col_widths = [70, 90, 174, 100, 70]
    else:
        headers = ["Fecha", "Vehículo", "Categoría", "Concepto", "Monto"]
        # Col widths: Fecha=70, Vehiculo=110, Categoria=90, Concepto=164, Monto=70 => total 504
        col_widths = [70, 110, 90, 164, 70]
        
    table_data = []
    
    # Fila de headers
    header_row = [Paragraph(h, header_style) for h in headers]
    table_data.append(header_row)
    
    # Filas de datos
    for idx, r in enumerate(rows):
        # r = (id, plates, vehicle_name, category, concept, amount, date, observations, vehicle_id, maint_id, driver_name)
        date_disp = format_db_date(r[6])
        amount_disp = f"${r[5]:,.2f}"
        
        if mode == 'vehiculo':
            driver_disp = r[10] if r[10] else "—"
            row_cells = [
                Paragraph(date_disp, cell_style),
                Paragraph(r[3], cell_style),
                Paragraph(r[4], cell_style),
                Paragraph(driver_disp, cell_style),
                Paragraph(amount_disp, cell_style),
            ]
        else:
            vehicle_disp = f"{r[1]} - {r[2]}"
            row_cells = [
                Paragraph(date_disp, cell_style),
                Paragraph(vehicle_disp, cell_style),
                Paragraph(r[3], cell_style),
                Paragraph(r[4], cell_style),
                Paragraph(amount_disp, cell_style),
            ]
        table_data.append(row_cells)
        
    # Fila de TOTAL al final de la tabla
    total_row = [
        Paragraph("TOTAL", total_label_style),
        "", "", "", # Celdas vacías para el span
        Paragraph(f"${total_spent:,.2f}", total_val_style)
    ]
    table_data.append(total_row)
    
    # Construir tabla
    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    
    # Estilo base de tabla
    t_styles = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -2), 0.5, colors.HexColor('#E5E7EB')),
        ('SPAN', (0, -1), (3, -1)), # Combinar primeras 4 columnas en la última fila
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#D1FAE5')), # Fondo verde para el total
        ('BOTTOMPADDING', (0, -1), (-1, -1), 10),
        ('TOPPADDING', (0, -1), (-1, -1), 10),
        ('LINEABOVE', (0, -1), (-1, -1), 1.5, colors.HexColor('#059669')),
    ]
    
    # Alternancia de colores para filas de datos
    for i in range(1, len(rows) + 1):
        bg_color = colors.HexColor('#F9FAFB') if i % 2 == 1 else colors.white
        t_styles.append(('BACKGROUND', (0, i), (-1, i), bg_color))
        t_styles.append(('TOPPADDING', (0, i), (-1, i), 6))
        t_styles.append(('BOTTOMPADDING', (0, i), (-1, i), 6))
        
    t.setStyle(TableStyle(t_styles))
    story.append(t)
    
    # Construir documento
    doc.build(story)
