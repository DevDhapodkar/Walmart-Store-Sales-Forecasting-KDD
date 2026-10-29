with open('scripts/build_submission_pdf.py', 'r') as f:
    code = f.read()

old_title_block = """# Title Block
story.append(Paragraph("PREDICTIVE ANALYTICS — CONTINUOUS ASSESSMENT 3 (CA3)", st_sub_title))
story.append(Paragraph("Sales Forecasting: End-to-End Predictive Analytics Model Development and Supply Chain Inventory Optimization Using the KDD Process", st_main_title))
story.append(Paragraph("<b>Submitted By:</b> Dev Dilip Dhapodkar &nbsp;&nbsp;|&nbsp;&nbsp; <b>PRN:</b> 24070521505<br/><b>Dataset:</b> Kaggle Walmart Recruiting — Store Sales Forecasting (421,570 Records, 45 Stores, 81 Departments)", st_meta))
story.append(Spacer(1, 4))"""

new_title_block = """# FIRST PAGE: EXACT PROFESSOR NOTIFICATION COVER PAGE
st_cover_title = ParagraphStyle(
    'CoverTitle',
    fontName='Times-Bold',
    fontSize=26,
    leading=32,
    textColor=colors.HexColor('#2563EB'),  # Royal Blue matching screenshot
    alignment=TA_CENTER,
    spaceBefore=70,
    spaceAfter=36
)

st_cover_course = ParagraphStyle(
    'CoverCourse',
    fontName='Times-Bold',
    fontSize=15.5,
    leading=22,
    textColor=colors.HexColor('#0F172A'),
    alignment=TA_CENTER,
    spaceBefore=6,
    spaceAfter=6
)

st_cover_sub = ParagraphStyle(
    'CoverSub',
    fontName='Times-Bold',
    fontSize=15,
    leading=21,
    textColor=colors.HexColor('#0F172A'),
    alignment=TA_CENTER,
    spaceBefore=28,
    spaceAfter=12
)

st_cover_student = ParagraphStyle(
    'CoverStudent',
    fontName='Times-Bold',
    fontSize=16,
    leading=22,
    textColor=colors.HexColor('#0F172A'),
    alignment=TA_CENTER,
    spaceBefore=4,
    spaceAfter=4
)

st_cover_meta = ParagraphStyle(
    'CoverMeta',
    fontName='Times-Roman',
    fontSize=13.5,
    leading=19,
    textColor=colors.HexColor('#1E293B'),
    alignment=TA_CENTER,
    spaceBefore=4,
    spaceAfter=4
)

story.append(Paragraph("CA3: Project Report Submission", st_cover_title))
story.append(Paragraph("Course Name: Predictive Analytics", st_cover_course))
story.append(Paragraph("Course Code: TE7253 / 0705210705", st_cover_course))
story.append(Paragraph("Submitted by", st_cover_sub))
story.append(Paragraph("Dev Dilip Dhapodkar", st_cover_student))
story.append(Paragraph("24070521505", st_cover_student))
story.append(Paragraph("Batch: 2023-27<br/>Semester - VII<br/>Section: Group A", st_cover_meta))

# FIRST PAGE CONTAINS ONLY THE ABOVE CONTENT
story.append(PageBreak())

# PAGE 2: PROJECT TITLE HEADER PRIOR TO CHAPTER 1
st_proj_title = ParagraphStyle(
    'ProjTitle',
    fontName='Times-Bold',
    fontSize=16,
    leading=21,
    textColor=colors.HexColor('#0F2942'),
    alignment=TA_CENTER,
    spaceBefore=6,
    spaceAfter=4
)

st_proj_sub = ParagraphStyle(
    'ProjSub',
    fontName='Times-Italic',
    fontSize=10.5,
    leading=14,
    textColor=colors.HexColor('#475569'),
    alignment=TA_CENTER,
    spaceBefore=2,
    spaceAfter=10
)

story.append(Paragraph("Sales Forecasting: End-to-End Predictive Analytics Model Development and Supply Chain Inventory Optimization Using the KDD Process", st_proj_title))
story.append(Paragraph("Walmart Multi-Store Hierarchical Sales Forecasting Benchmark Study | Knowledge Discovery in Databases (KDD)", st_proj_sub))
story.append(Spacer(1, 4))"""

code = code.replace(old_title_block, new_title_block)

with open('scripts/build_submission_pdf.py', 'w') as f:
    f.write(code)

print("Updated scripts/build_submission_pdf.py!")
