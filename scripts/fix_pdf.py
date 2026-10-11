with open('build_report.py', 'r') as f:
    code = f.read()

# Replace unicode arrows/symbols in PDF section or globally in tables for clean Type-1 Helvetica rendering
replacements = {
    "↓": "",
    "↑": "",
    "→": "->",
    "Σ": "Sum",
    "ŷ": "y_hat",
    "−": "-",
    "•": "-"
}

# Let's only sanitize for PDF generation while keeping docx rich, or sanitize table headers cleanly
old_pdf_part = code.split("# 2. GENERATE PDF DOCUMENT (.pdf) VIA REPORTLAB")[1]
new_pdf_part = old_pdf_part
for k, v in replacements.items():
    new_pdf_part = new_pdf_part.replace(k, v)

# Also sanitize table strings passed to rl_table
sanitize_fn = """
def clean_pdf_str(s):
    return (str(s)
        .replace('↓', '')
        .replace('↑', '')
        .replace('→', '->')
        .replace('Σ', 'Sum')
        .replace('ŷ', 'y_hat')
        .replace('•', '-')
    )
"""

new_pdf_part = new_pdf_part.replace(
    "def rl_table(data_rows, col_widths):",
    sanitize_fn + "\ndef rl_table(data_rows, col_widths):"
).replace(
    "row_cells.append(Paragraph(str(c), st_th if i == 0 else st_td))",
    "row_cells.append(Paragraph(clean_pdf_str(c), st_th if i == 0 else st_td))"
).replace(
    "topMargin=0.75 * inch,\n    bottomMargin=0.75 * inch",
    "topMargin=0.62 * inch,\n    bottomMargin=0.65 * inch"
).replace(
    "spaceAfter=6",
    "spaceAfter=4.5"
)

full_code = code.split("# 2. GENERATE PDF DOCUMENT (.pdf) VIA REPORTLAB")[0] + "# 2. GENERATE PDF DOCUMENT (.pdf) VIA REPORTLAB" + new_pdf_part
with open('build_report.py', 'w') as f:
    f.write(full_code)

