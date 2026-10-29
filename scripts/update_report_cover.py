import re

with open('scripts/build_submission_report.py', 'r') as f:
    code = f.read()

# Replace the TITLE & STUDENT HEADER BLOCK with the exact required first page + page break
old_block_start = "# TITLE & STUDENT HEADER BLOCK"
old_block_end = "# CHAPTER 1: INTRODUCTION"

new_cover_block = """# FIRST PAGE: STRICT PROFESSOR NOTIFICATION FORMAT
# ==============================================================================
# Spacer to balance vertically
p_top_space = doc.add_paragraph()
set_para_format(p_top_space, space_before=72, space_after=0)

# Main Title (Blue, bold, centered)
p_ca3 = doc.add_paragraph()
set_para_format(p_ca3, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=36)
r_ca3 = p_ca3.add_run("CA3: Project Report Submission")
r_ca3.font.name = 'Times New Roman'
r_ca3.font.size = Pt(26)
r_ca3.font.bold = True
r_ca3.font.color.rgb = RGBColor(37, 99, 235)  # Vibrant Royal Blue matching screenshot

# Course Information
p_cname = doc.add_paragraph()
set_para_format(p_cname, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=6)
r_cname = p_cname.add_run("Course Name: Predictive Analytics")
r_cname.font.name = 'Times New Roman'
r_cname.font.size = Pt(16)
r_cname.font.bold = True
r_cname.font.color.rgb = RGBColor(15, 23, 42)

p_ccode = doc.add_paragraph()
set_para_format(p_ccode, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=40)
r_ccode = p_ccode.add_run("Course Code: TE7253 / 0705210705")
r_ccode.font.name = 'Times New Roman'
r_ccode.font.size = Pt(15)
r_ccode.font.bold = True
r_ccode.font.color.rgb = RGBColor(15, 23, 42)

# Submitted by Section
p_subby = doc.add_paragraph()
set_para_format(p_subby, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=16, space_after=12)
r_subby = p_subby.add_run("Submitted by")
r_subby.font.name = 'Times New Roman'
r_subby.font.size = Pt(15)
r_subby.font.bold = True
r_subby.font.color.rgb = RGBColor(15, 23, 42)

p_sname = doc.add_paragraph()
set_para_format(p_sname, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=4)
r_sname = p_sname.add_run("Dev Dilip Dhapodkar")
r_sname.font.name = 'Times New Roman'
r_sname.font.size = Pt(16)
r_sname.font.bold = True
r_sname.font.color.rgb = RGBColor(15, 23, 42)

p_prn = doc.add_paragraph()
set_para_format(p_prn, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=8)
r_prn = p_prn.add_run("24070521505")
r_prn.font.name = 'Times New Roman'
r_prn.font.size = Pt(15)
r_prn.font.bold = True
r_prn.font.color.rgb = RGBColor(15, 23, 42)

p_meta = doc.add_paragraph()
set_para_format(p_meta, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=4)
r_batch = p_meta.add_run("Batch: 2023-27\n")
r_batch.font.name = 'Times New Roman'
r_batch.font.size = Pt(13.5)

r_sem = p_meta.add_run("Semester - VII\n")
r_sem.font.name = 'Times New Roman'
r_sem.font.size = Pt(13.5)

r_sec = p_meta.add_run("Section: Group A")
r_sec.font.name = 'Times New Roman'
r_sec.font.size = Pt(13.5)

# STRICT REQUIREMENT: First page contains ONLY the above content!
doc.add_page_break()

# PAGE 2: PROJECT TITLE HEADER PRIOR TO CHAPTER 1
p_proj_title = doc.add_paragraph()
set_para_format(p_proj_title, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=8, space_after=4)
r_pt = p_proj_title.add_run("Sales Forecasting: End-to-End Predictive Analytics Model Development and Supply Chain Inventory Optimization Using the KDD Process")
r_pt.font.name = 'Times New Roman'
r_pt.font.size = Pt(16)
r_pt.font.bold = True
r_pt.font.color.rgb = RGBColor(15, 41, 66)

p_proj_sub = doc.add_paragraph()
set_para_format(p_proj_sub, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=12)
r_ps = p_proj_sub.add_run("Walmart Multi-Store Hierarchical Sales Forecasting Benchmark Study | Knowledge Discovery in Databases (KDD)")
r_ps.font.name = 'Times New Roman'
r_ps.font.size = Pt(11)
r_ps.font.italic = True
r_ps.font.color.rgb = RGBColor(71, 85, 105)

p_div = doc.add_paragraph()
set_para_format(p_div, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=10)
r_div = p_div.add_run("―" * 52)
r_div.font.name = 'Times New Roman'
r_div.font.color.rgb = RGBColor(203, 213, 225)

"""

pattern = r"# TITLE & STUDENT HEADER BLOCK.*?(?=# CHAPTER 1: INTRODUCTION)"
code = re.sub(pattern, new_cover_block, code, flags=re.DOTALL)

with open('scripts/build_submission_report.py', 'w') as f:
    f.write(code)

print("Updated scripts/build_submission_report.py with exact cover page!")
