"""
Convert PDF document to Excel (.xlsx) spreadsheet.
Extracts structured tables and tabular text from PDF pages into formatted Excel worksheets.
"""
import os
import time
from typing import Dict, Any
import pymupdf
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

def pdf_to_excel(input_pdf: str, output_xlsx: str) -> Dict[str, Any]:
    t0 = time.time()
    input_abs = os.path.abspath(input_pdf)
    output_abs = os.path.abspath(output_xlsx)

    if not os.path.isfile(input_abs):
        return {"success": False, "error": f"PDF file not found: {input_pdf}"}

    os.makedirs(os.path.dirname(output_abs) or ".", exist_ok=True)

    try:
        doc = pymupdf.open(input_abs)
        wb = openpyxl.Workbook()
        # Remove default sheet
        wb.remove(wb.active)

        thin_border = Border(
            left=Side(style='thin', color='CCCCCC'),
            right=Side(style='thin', color='CCCCCC'),
            top=Side(style='thin', color='CCCCCC'),
            bottom=Side(style='thin', color='CCCCCC')
        )
        header_fill = PatternFill(start_color="3B82F6", end_color="3B82F6", fill_type="solid")
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")

        total_tables = 0
        total_rows = 0

        for page_idx, page in enumerate(doc):
            ws = wb.create_sheet(title=f"Page_{page_idx+1}")
            current_row = 1

            # Try finding structured tables first
            tabs = page.find_tables()
            if tabs.tables:
                for t_idx, table in enumerate(tabs):
                    total_tables += 1
                    data = table.extract()
                    for r_idx, row in enumerate(data):
                        total_rows += 1
                        for c_idx, cell_val in enumerate(row):
                            val = "" if cell_val is None else str(cell_val).strip()
                            cell = ws.cell(row=current_row, column=c_idx+1, value=val)
                            cell.border = thin_border
                            if r_idx == 0:
                                cell.fill = header_fill
                                cell.font = header_font
                                cell.alignment = Alignment(horizontal="center", vertical="center")
                        current_row += 1
                    current_row += 2  # Spacer between tables
            else:
                # Fallback: extract text blocks and split into lines
                blocks = page.get_text("blocks")
                for b in blocks:
                    text = b[4]
                    lines = text.split("\n")
                    for line in lines:
                        if not line.strip():
                            continue
                        total_rows += 1
                        # Split by tabs or multiple spaces
                        parts = [p.strip() for p in line.split("  ") if p.strip()]
                        if not parts:
                            parts = [line.strip()]
                        for c_idx, part in enumerate(parts):
                            cell = ws.cell(row=current_row, column=c_idx+1, value=part)
                        current_row += 1

            # Auto-fit column widths
            for col in ws.columns:
                max_len = 0
                col_letter = col[0].column_letter
                for cell in col:
                    if cell.value:
                        max_len = max(max_len, len(str(cell.value)))
                ws.column_dimensions[col_letter].width = min(max(max_len + 3, 10), 50)

        doc.close()
        wb.save(output_abs)

        return {
            "success": True,
            "input": os.path.basename(input_pdf),
            "output": output_abs,
            "count": f"{len(wb.sheetnames)} sheet(s), {total_rows} row(s)",
            "size_bytes": os.path.getsize(output_abs),
            "duration": time.time() - t0
        }

    except Exception as e:
        return {"success": False, "error": f"PDF to Excel conversion error: {e}"}
