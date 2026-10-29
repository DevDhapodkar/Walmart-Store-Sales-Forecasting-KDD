import os
import json
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

doc = Document()

# Set Page size to A4: 210mm x 297mm (8.27 in x 11.69 in)
for section in doc.sections:
    section.page_width = Inches(8.27)
    section.page_height = Inches(11.69)
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(1.0)

# Set base Normal Style to Times New Roman, 12pt
style_normal = doc.styles['Normal']
style_normal.font.name = 'Times New Roman'
style_normal.font.size = Pt(12)
style_normal.font.color.rgb = RGBColor(0, 0, 0)

def set_para_format(p, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=6, space_after=6, line_spacing=1.15):
    p.alignment = align
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing

def add_p(doc, text="", bold_prefix=None, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=6, space_after=6, line_spacing=1.15):
    p = doc.add_paragraph()
    set_para_format(p, align, space_before, space_after, line_spacing)
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = 'Times New Roman'
        r_pre.font.size = Pt(12)
        r_pre.font.bold = True
    if text:
        r_text = p.add_run(text)
        r_text.font.name = 'Times New Roman'
        r_text.font.size = Pt(12)
    return p

def add_heading_1(doc, text):
    p = doc.add_paragraph()
    set_para_format(p, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=14, space_after=6)
    r = p.add_run(text)
    r.font.name = 'Times New Roman'
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = RGBColor(15, 41, 66)
    return p

def add_heading_2(doc, text):
    p = doc.add_paragraph()
    set_para_format(p, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=10, space_after=4)
    r = p.add_run(text)
    r.font.name = 'Times New Roman'
    r.font.size = Pt(13.5)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 113, 206)
    return p

def add_heading_3(doc, text):
    p = doc.add_paragraph()
    set_para_format(p, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=8, space_after=4)
    r = p.add_run(text)
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)
    r.font.bold = True
    r.font.color.rgb = RGBColor(30, 41, 59)
    return p

def add_table_with_caption(doc, caption_text, headers, rows_data, col_widths=None):
    # Requirement: Table caption must be ABOVE the table
    p_cap = doc.add_paragraph()
    set_para_format(p_cap, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=8, space_after=4)
    r_cap = p_cap.add_run(caption_text)
    r_cap.font.name = 'Times New Roman'
    r_cap.font.size = Pt(11)
    r_cap.font.bold = True
    r_cap.font.color.rgb = RGBColor(15, 41, 66)

    table = doc.add_table(rows=len(rows_data) + 1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    # Header Row
    hdr_cells = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr_cells[i].text = str(h)
        if col_widths and i < len(col_widths):
            hdr_cells[i].width = Inches(col_widths[i])
        hdr_cells[i].vertical_anchor = WD_ALIGN_VERTICAL.CENTER
        shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="0F2942"/>')
        hdr_cells[i]._tc.get_or_add_tcPr().append(shading)
        p = hdr_cells[i].paragraphs[0]
        set_para_format(p, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=4, line_spacing=1.0)
        for r in p.runs:
            r.font.name = 'Times New Roman'
            r.font.size = Pt(10)
            r.font.bold = True
            r.font.color.rgb = RGBColor(255, 255, 255)

    # Data Rows
    for r_idx, row in enumerate(rows_data):
        row_cells = table.rows[r_idx + 1].cells
        bg_col = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(row):
            row_cells[c_idx].text = str(val)
            if col_widths and c_idx < len(col_widths):
                row_cells[c_idx].width = Inches(col_widths[c_idx])
            row_cells[c_idx].vertical_anchor = WD_ALIGN_VERTICAL.CENTER
            shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{bg_col}"/>')
            row_cells[c_idx]._tc.get_or_add_tcPr().append(shading)
            p = row_cells[c_idx].paragraphs[0]
            # Center if number/short text, Left if descriptive
            align_c = WD_ALIGN_PARAGRAPH.LEFT if c_idx == 0 or len(str(val)) > 25 else WD_ALIGN_PARAGRAPH.CENTER
            set_para_format(p, align=align_c, space_before=3, space_after=3, line_spacing=1.05)
            for r in p.runs:
                r.font.name = 'Times New Roman'
                r.font.size = Pt(9.5)
                r.font.color.rgb = RGBColor(30, 41, 59)

    p_post = doc.add_paragraph()
    set_para_format(p_post, space_before=2, space_after=4)

def add_figure_with_caption(doc, img_path, caption_text, width_inches=6.0):
    # Requirement: Figure name/caption must be BELOW figure
    p_img = doc.add_paragraph()
    set_para_format(p_img, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=8, space_after=3)
    run_img = p_img.add_run()
    run_img.add_picture(img_path, width=Inches(width_inches))

    p_cap = doc.add_paragraph()
    set_para_format(p_cap, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=8)
    r_cap = p_cap.add_run(caption_text)
    r_cap.font.name = 'Times New Roman'
    r_cap.font.size = Pt(10.5)
    r_cap.font.italic = True
    r_cap.font.bold = False
    r_cap.font.color.rgb = RGBColor(71, 85, 105)

def add_equation_block(doc, formula_text, eq_number_str):
    # 1-row, 2-column borderless table to guarantee exact centered formula and right-aligned numbering
    tbl = doc.add_table(rows=1, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    c_left = tbl.cell(0, 0)
    c_right = tbl.cell(0, 1)
    c_left.width = Inches(5.4)
    c_right.width = Inches(0.87)

    # Remove borders
    for c in [c_left, c_right]:
        tcPr = c._tc.get_or_add_tcPr()
        tcBorders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:top w:val="none"/><w:left w:val="none"/><w:bottom w:val="none"/><w:right w:val="none"/></w:tcBorders>')
        tcPr.append(tcBorders)

    p_l = c_left.paragraphs[0]
    set_para_format(p_l, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=4, line_spacing=1.1)
    r_l = p_l.add_run(formula_text)
    r_l.font.name = 'Times New Roman'
    r_l.font.size = Pt(11.5)
    r_l.font.italic = True

    p_r = c_right.paragraphs[0]
    set_para_format(p_r, align=WD_ALIGN_PARAGRAPH.RIGHT, space_before=4, space_after=4, line_spacing=1.1)
    r_r = p_r.add_run(f"({eq_number_str})")
    r_r.font.name = 'Times New Roman'
    r_r.font.size = Pt(11.5)
    r_r.font.bold = True

    p_after = doc.add_paragraph()
    set_para_format(p_after, space_before=0, space_after=2)

print("Document setup complete. Compiling content...")

# ==============================================================================
# FIRST PAGE: STRICT PROFESSOR NOTIFICATION FORMAT
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

# CHAPTER 1: INTRODUCTION
# ==============================================================================
add_heading_1(doc, "Chapter 1: Introduction")

add_p(doc, 
    "In large-scale retail commerce, accurate sales forecasting represents the cornerstone of effective multi-echelon supply chain management. Modern big-box retail operations, exemplified by multinational supermarket networks such as Walmart, encompass thousands of store-department intersections operating across heterogeneous geographical catchments. Each individual retail unit is simultaneously buffeted by long-term macroeconomic fluctuations, local purchasing power variations, weather perturbations, high-velocity promotional markdown events, and extreme calendar-driven holiday surges. Traditional inventory replenishment policies that rely on simple historical moving averages or localized univariate projections frequently exhibit catastrophic forecast mismatch. These planning failures precipitate two mutually destructive operational regimes: costly stockouts during high-velocity holiday peaks, which irreversibly erode revenue and consumer brand loyalty, and severe overstocking during regular replenishment cycles, which inflates working capital lock-up, warehouse handling overhead, and subsequent gross margin erosion through forced post-holiday clearance markdowns.",
    bold_prefix="1.1 Context and Problem Domain: "
)

add_p(doc, 
    "The primary objective of this project is to develop, validate, and interpret an end-to-end predictive analytics regression pipeline that forecasts weekly department-level sales across multiple retail stores using historical sales transactions, promotional price markdown schedules, calendar holiday schedules, and regional macroeconomic indicators. Formulated as a multi-store hierarchical forecasting problem on the benchmark Kaggle Walmart Recruiting dataset, the analytical framework follows the rigorous Knowledge Discovery in Databases (KDD) process. Specifically, the model forecasts weekly revenue across 45 physical Walmart stores and 81 specialized departments spanning three distinct store format architectures (Type A Supercenters, Type B Discount Stores, and Type C Neighborhood Markets).",
    bold_prefix="1.2 Research Objective and Scope: "
)

add_p(doc, 
    "A fundamental characteristic of retail demand forecasting lies in the acute operational asymmetry of prediction error costs. In standard regression formulations, errors are evaluated using uniform symmetric penalties such as Ordinary Least Squares Mean Squared Error (MSE) or Mean Absolute Error (MAE). In practical supply chain operations, however, an under-forecast during a peak retail holiday such as Thanksgiving (Black Friday) or the pre-Christmas shopping week is drastically more damaging than an equivalent magnitude error during a routine non-holiday week in February. During major holiday events, consumer foot traffic peaks by upwards of 40% to 50%, supply chain lead times from distribution centers are saturated, and stockouts cannot be mitigated via emergency freight. Consequently, the operational loss function must heavily penalize holiday forecast discrepancies. This business reality is formalized via the official Kaggle Weighted Mean Absolute Error (WMAE) metric, which explicitly assigns a 5x weighting factor (w = 5) to holiday observation weeks relative to baseline weeks (w = 1). The predictive system developed herein is explicitly calibrated to optimize this asymmetric cost surface.",
    bold_prefix="1.3 Asymmetric Supply Chain Cost Structure: "
)

# ==============================================================================
# CHAPTER 2: LITERATURE REVIEW
# ==============================================================================
add_heading_1(doc, "Chapter 2: Literature Review")

add_p(doc, 
    "The academic and industrial literature surrounding retail demand forecasting has undergone a profound paradigm shift over the past two decades. Early econometric approaches relied almost exclusively on univariate statistical formulations, most notably the classical Autoregressive Integrated Moving Average (ARIMA) and Seasonal ARIMA (SARIMA) models popularized by Box and Jenkins, alongside Holt-Winters Exponential Smoothing state-space models. While mathematically tractable and capable of capturing stationary autocorrelative cycles, univariate parametric formulations exhibit severe structural limitations in modern retail environments. First, they require the fitting and ongoing maintenance of thousands of independent local models across every individual store-department time series. Second, and more critically, univariate models possess limited capacity to ingest high-dimensional, cross-sectional exogenous features—such as simultaneous multi-channel promotional markdowns, regional fuel prices, and macroeconomic consumer indices—without suffering severe parameter instability and degrees-of-freedom depletion.",
    bold_prefix="2.1 Classical Econometric and Parametric Formulations: "
)

add_p(doc, 
    "To overcome the limitations of localized univariate modeling, contemporary predictive analytics leverages global machine learning architectures that pool cross-sectional observations across all store and department hierarchies into a unified high-capacity tabular space. Foundational work by Breiman on Random Forests established the efficacy of bagging randomized decision trees to suppress prediction variance and accommodate complex non-linear feature interactions without overfitting. Subsequently, the advent of extreme gradient boosting architectures—most prominently XGBoost introduced by Chen and Guestrin, and LightGBM developed by Ke et al.—revolutionized retail forecasting. These tree-based ensembles utilize second-order Taylor expansions of the objective loss function, incorporated L1/L2 leaf weight regularization, and histogram-based continuous feature binning. Landmark industrial competitions, notably the M5 Forecasting Accuracy Competition analyzed by Makridakis et al., decisively demonstrated that global gradient-boosted decision trees enriched with multi-horizon lag structures and shifted rolling statistical aggregations consistently outperform both classical statistical methods and deep recurrent neural networks on intermittent, highly promotional retail demand series.",
    bold_prefix="2.2 Global Machine Learning and Gradient Boosted Tree Ensembles: "
)

# Table 1: Literature Review Summary
lit_headers = ["Author(s) & Year", "Methodology / Architecture", "Dataset / Domain", "Key Strengths & Identified Limitations"]
lit_data = [
    ["Box & Jenkins (2015); Hyndman (2021)", "ARIMA, SARIMAX & ETS State-Space Models", "Univariate Retail Series", "Strong linear autocorrelation capture; poor handling of non-linear promotional spikes and cross-store data pooling."],
    ["Breiman (2001)", "Random Forest Regressor (Bagging Ensemble)", "Tabular Machine Learning", "Robust to noisy outliers and non-linear interactions; high computational memory overhead and slower inference."],
    ["Chen & Guestrin (2016)", "XGBoost (Regularized Gradient Tree Boosting)", "High-Dimensional Benchmarks", "Second-order Taylor optimization with L1/L2 leaf penalties; excellent handling of sparse features; depth-wise tree growth."],
    ["Ke et al. (2017)", "LightGBM (Leaf-Wise Histogram Boosting)", "Multi-Store Retail Benchmarks", "Leaf-wise best-first tree growth with histogram binning; >80% reduction in training latency with superior convergence on skewed targets."],
    ["Makridakis et al. (2022)", "M5 Forecasting Competition (Tree Ensembles)", "Walmart Hierarchical (42,840 series)", "Demonstrated that global GBDT ensembles with lag and rolling features decisively surpass classical and deep neural architectures."],
    ["Barrow & Kourentzes (2016)", "Safety Stock Optimization under Asymmetric Loss", "Supply Chain Operations", "Confirmed that targeted reduction in peak-period forecast variance yields disproportionate reductions in buffer stockholding costs."]
]
add_table_with_caption(doc, "Table 1: Synthesis of Relevant Prior Literature in Predictive Retail Analytics and Machine Learning", lit_headers, lit_data, [1.4, 1.6, 1.4, 2.4])

add_p(doc, 
    "Despite the extensive literature on gradient-boosted decision trees in retail, existing empirical implementations frequently suffer from two persistent methodological flaws. First, many published studies compute rolling statistical features across the entire chronological horizon without enforcing a strict t-1 backward shift, thereby inadvertently leaking current-period target variance into historical rolling aggregations. Second, standard models are commonly optimized against symmetric unweighted metrics (such as unweighted RMSE or MAE), ignoring the asymmetric 5x financial penalty of holiday stockout events. This study bridges this gap by engineering a leak-free feature pipeline, enforcing sample-weighted holiday optimization, and directly translating statistical error reductions into dollarized inventory holding and stockout cost mitigation.",
    bold_prefix="2.3 Research Gap and Methodological Contribution: "
)

# ==============================================================================
# CHAPTER 3: WORKFLOW / PREDICTIVE MODELLING PROCESS
# ==============================================================================
add_heading_1(doc, "Chapter 3: Workflow / Predictive Modelling Process")

add_p(doc, 
    "To ensure methodological rigor, reproducibility, and end-to-end traceability, this project operationalizes the classical Knowledge Discovery in Databases (KDD) framework originally formulated by Fayyad et al. The predictive modeling workflow proceeds through seven sequential and interdependent phases: (1) Relational Data Selection and Ingestion, (2) Target-Aligned Data Preprocessing and Outlier Treatment, (3) Multi-Scale Feature Engineering, (4) Exploratory Data Analysis (EDA), (5) Multi-Model Architecture Training, (6) Comprehensive Out-of-Sample Performance Evaluation under Asymmetric WMAE, and (7) Feature Gain Attribution and Supply Chain Business Interpretation.",
    bold_prefix="3.1 The KDD Methodological Architecture: "
)

add_heading_2(doc, "3.2 Stage 1: Data Selection and Relational Ingestion")
add_p(doc, 
    "The analytical dataset was sourced from the benchmark Walmart Recruiting — Store Sales Forecasting repository. The schema comprises four relational tables that were merged into a unified analytical matrix. Historical weekly sales records (train.csv) were merged with exogenous environmental and economic attributes (features.csv) on the composite primary key [Store, Date, IsHoliday], and subsequently merged with structural store metadata (stores.csv) on [Store]. The resulting merged training matrix comprises exactly 421,570 unique store-department-week observations spanning 143 consecutive weeks from February 5, 2010 to October 26, 2012. Table 2 details the structural properties and granularity of each constituent table."
)

tab2_headers = ["File Name", "Record Count", "Attribute Count", "Primary Granularity", "Attribute Schema & Operational Role"]
tab2_data = [
    ["stores.csv", "45", "3", "Store (1–45)", "Store metadata: Store format Type (A: 22 Supercenters, B: 17 Discount Stores, C: 6 Neighborhood Markets) and physical Size (34,875 to 219,622 sq. ft.)."],
    ["features.csv", "8,190", "12", "(Store, Date)", "Contextual attributes: Temperature (°F), Fuel_Price ($/gal), MarkDown1–MarkDown5 promotional channels, CPI, Unemployment (%), and IsHoliday."],
    ["train.csv", "421,570", "5", "(Store, Dept, Date)", "Historical weekly sales: Weekly_Sales ($ USD) across 45 stores and 81 departments over 143 historical weeks."],
    ["test.csv", "115,064", "4", "(Store, Dept, Date)", "Future evaluation horizon spanning 39 weeks (November 2, 2012 to July 26, 2013) for out-of-sample deployment."]
]
add_table_with_caption(doc, "Table 2: Relational Database Schema and Ingestion Properties of the Walmart Forecasting Corpus", tab2_headers, tab2_data, [1.1, 1.0, 0.9, 1.3, 2.5])

add_heading_2(doc, "3.3 Stage 2: Data Preprocessing, Imputation and Outlier Treatment")
add_p(doc, 
    "A systematic diagnostic of the raw ingested dataset revealed three critical data quality anomalies requiring domain-informed preprocessing: promotional markdown missingness, macroeconomic temporal gaps, and accounting returns manifesting as negative sales values."
)

tab3_headers = ["Attribute / Data Column", "Pre-Imputation Missing Count", "Missing Percentage", "Observed Root Cause in Retail Operations", "Engineered Preprocessing & Imputation Strategy"]
tab3_data = [
    ["MarkDown1 (General Dept)", "270,889", "64.26%", "Walmart initiated markdown tracking in Nov 2011; NA denotes zero active promo.", "Extracted Has_MarkDown indicator; structural zero imputation (0.0); clipped < 0."],
    ["MarkDown2 (Seasonal/Holiday)", "310,322", "73.61%", "Active exclusively during specific clearance and post-holiday seasonal windows.", "Extracted Active_MarkDown_Count; structural zero imputation (0.0)."],
    ["MarkDown3 (Event-Specific)", "284,479", "67.48%", "High-depth markdowns tied to Thanksgiving Black Friday promotional events.", "Structural zero imputation (0.0); engineered Promo_Holiday_Interaction term."],
    ["MarkDown4 (Store-Wide)", "286,603", "67.98%", "Multi-department bundled markdown campaigns logged sporadically.", "Structural zero imputation (0.0); aggregated into Total_MarkDown."],
    ["MarkDown5 (Liquidation)", "270,138", "64.08%", "Apparel and consumable clearance liquidations across selected stores.", "Structural zero imputation (0.0); aggregated into Total_MarkDown."],
    ["CPI & Unemployment", "585 (in features.csv)", "7.14%", "Macroeconomic indices lagged during the final weeks of the evaluation horizon.", "Store-grouped chronological forward and backward propagation (ffill and bfill)."],
    ["Weekly_Sales (< $0.00)", "1,285 records", "0.30%", "Post-holiday merchandise returns and retroactive accounting adjustments.", "Floored at $0.00 to guarantee non-negative physical demand target."],
    ["Extreme Sales Outliers", "422 records (> $174.9K)", "0.10%", "Massive bulk sales vs. genuine Thanksgiving/Black Friday demand surges.", "Winsorized non-holiday upper-tail records at 99.95th pct ($183.5K); preserved Holidays."]
]
add_table_with_caption(doc, "Table 3: Comprehensive Diagnostic Profile of Missing Values, Anomalies, and Imputation Protocols", tab3_headers, tab3_data, [1.3, 1.1, 0.9, 1.6, 1.9])

add_p(doc, 
    "To handle promotional markdowns correctly, naive mean or median imputation was strictly avoided. In retail, an unrecorded markdown signifies the structural absence of an active promotional campaign rather than a missing measurement. Consequently, structural zero-imputation was executed, preceded by the extraction of binary indicator features (Has_MarkDown) and continuous aggregation terms (Total_MarkDown and Active_MarkDown_Count). For negative sales records resulting from post-holiday returns, values were floored at $0.00. Crucially, standard statistical outlier filtering techniques (such as global IQR trimming) were rejected because they would erroneously delete genuine Black Friday and Christmas demand spikes. Instead, winsorization at the 99.95th percentile ($183,494.06) was restricted strictly to non-holiday records, thereby preserving genuine holiday surges vital for asymmetric model training."
)

add_heading_2(doc, "3.4 Stage 3: Multi-Scale Feature Engineering Pipeline")
add_p(doc, 
    "To enable tree-based ensembles to model multi-scale temporal dynamics without look-ahead bias, 43 domain-specific predictive features were constructed across five structural families:\n"
    "1. Autoregressive Lag Features: Grouped strictly by [Store, Dept] and sorted chronologically, we generated Lag_1 (immediate prior week demand, capturing local continuity), Lag_2 (two-week lag, capturing bi-weekly wage cycles), Lag_4 (four-week lag, capturing monthly replenishment cycles), and Lag_52 (fifty-two-week lag, capturing the exact year-over-year seasonal demand anchor).\n"
    "2. Leak-Free Shifted Rolling Aggregations: Moving window statistics were computed exclusively on t-1 shifted demand series s.shift(1).rolling(W). This guaranteed zero target leakage. We computed Rolling_Mean_4 (4-week short-term moving average), Rolling_Std_4 (4-week demand volatility), Rolling_Mean_12 (12-week quarterly demand baseline), and a short-term trend velocity indicator Momentum_1_4 = Lag_1 - Rolling_Mean_4.\n"
    "3. Explicit Holiday Calendar Indicators: In addition to the generic IsHoliday boolean, explicit binary flags were engineered for the four major official Walmart holiday events: Is_SuperBowl (Week 6), Is_LaborDay (Week 36), Is_Thanksgiving (Week 47), and Is_Christmas (Week 52), complemented by Pre_Christmas_Peak capturing high-velocity shopping in Weeks 49 through 51.\n"
    "4. Fourier Cyclical Seasonality Transforms: Standard integer calendar features (Week 1–52, Month 1–12) exhibit an artificial numerical discontinuity between late December and early January. To enforce circular continuity, continuous sine and cosine Fourier transformations were computed:"
)

# Equation 1
add_equation_block(doc, "Week_Sin = sin(2π · Week / 52),   Week_Cos = cos(2π · Week / 52)", "1")

add_p(doc, 
    "5. Out-of-Sample Historical Target Statistics: To inject department-level scale without data contamination, historical demand statistics (Store_Dept_Mean, Store_Dept_Median, and Store_Dept_Std) were calculated strictly on the training partition prior to the validation cutoff date and mapped onto the evaluation partition."
)

add_heading_2(doc, "3.5 Stage 5 & 6: Predictive Model Formulation and Evaluation Metric")
add_p(doc, 
    "We benchmarked four diverse algorithmic architectures spanning linear regularization, bagging ensembles, and advanced gradient boosting:\n"
    "• Baseline Model: Ridge Regression with L2 Regularization, optimizing the objective:"
)

# Equation 2
add_equation_block(doc, "min_β { ||y - Xβ||₂² + α ||β||₂² },   where α = 100.0", "2")

add_p(doc, 
    "• Random Forest Regressor: An ensemble of B = 100 decorrelated decision trees constructed via bootstrap sampling with random feature subspace selection (max_features = 0.6, max_depth = 16). The ensemble prediction represents the sample-weighted average across all constituent trees:"
)

# Equation 3
add_equation_block(doc, "ŷ_RF(x) = (1 / B) Σ_{b=1}^{B} T_b(x)", "3")

add_p(doc, 
    "• XGBoost and LightGBM Regressors: Gradient-boosted decision trees that construct an additive expansion of K shallow regression trees ŷ_i = Σ f_k(x_i). At each iteration t, the model minimizes a second-order Taylor expansion of the weighted regularized loss:"
)

# Equation 4
add_equation_block(doc, "L^{(t)} ≈ Σ_{i=1}^{N} w_i [ g_i f_t(x_i) + (1/2) h_i f_t^2(x_i) ] + Ω(f_t)", "4")

add_p(doc, 
    "where g_i and h_i represent the first and second order gradients of the loss with respect to prior predictions, and Ω(f_t) penalizes leaf count and leaf weight magnitudes.\n\n"
    "• Official Evaluation Metric — Weighted Mean Absolute Error (WMAE): Models were evaluated on an out-of-sample chronological validation horizon using the official Kaggle metric, which assigns a weight of 5 to holiday weeks and 1 to regular weeks:"
)

# Equation 5
add_equation_block(doc, "WMAE = [ Σ_{i=1}^{N} w_i · |y_i - ŷ_i| ] / [ Σ_{i=1}^{N} w_i ],   w_i = 5 if IsHoliday_i else 1", "5")

add_p(doc, 
    "• Supply Chain Inventory Mismatch Cost Formulation: To translate WMAE reductions into dollarized operational impact, we modeled total weekly inventory mismatch penalty C_mismatch under an industry-standard holding and stockout penalty coefficient γ = 0.22:"
)

# Equation 6
add_equation_block(doc, "C_mismatch = γ · Σ_{i=1}^{N} |y_i - ŷ_i|,   where γ = 0.22", "6")

add_p(doc, 
    "• Chronological Validation Split Strategy: To eliminate look-ahead bias, the dataset was split chronologically at November 25, 2011. The training partition comprises 263,199 records (February 2010 to November 2011), while the validation horizon comprises 145,237 records spanning exactly 49 consecutive weeks (November 25, 2011 to October 26, 2012). This validation window is structurally ideal because it encompasses all four official holiday events: Thanksgiving 2011, Christmas 2011, Super Bowl 2012, and Labor Day 2012, ensuring an exhaustive test of holiday generalization."
)

# ==============================================================================
# CHAPTER 4: RESULTS AND DISCUSSION
# ==============================================================================
add_heading_1(doc, "Chapter 4: Results and Discussion")

add_heading_2(doc, "4.1 Exploratory Data Analysis Insights")
add_p(doc, 
    "Figure 1 provides an aggregate overview of retail demand dynamics across the 45 Walmart stores. Total weekly revenue across the network averages $47.1M during baseline weeks, but experiences explosive non-linear surges during Q4 holiday events. During Thanksgiving week (encompassing Black Friday), aggregate revenue escalates to $66.6M, representing an average store-level sales surge of +44.0%. This is followed in late December by the pre-Christmas shopping surge (Weeks 49 through 51), where aggregate weekly volume peaks at nearly $80.0M (+40.2% lift). In contrast, Christmas week itself experiences an immediate -6.0% contraction due to store closures and post-holiday trading lulls. Furthermore, Figure 1 (Panel C) confirms a powerful linear relationship (Pearson r = 0.81) between physical store area and average weekly revenue across Type A Supercenters (mean $1.45M/week, avg size 177K sq. ft.), Type B Discount Stores (mean $0.79M/week, avg size 101K sq. ft.), and Type C Neighborhood Markets (mean $0.46M/week, avg size 41K sq. ft.)."
)

add_figure_with_caption(doc, "figures/fig1_eda_sales_overview.png", "Figure 1: Aggregate Weekly Retail Sales Trajectory (2010–2012), Format Type Distribution, and Store Area Size Elasticity.", width_inches=6.2)

add_p(doc, 
    "Figure 2 illustrates the pre-imputation missingness distribution across the dataset, highlighting the severe sparsity of MarkDown1 through MarkDown5 prior to late 2011. Panel B reveals the heavily right-skewed distribution of department weekly sales (median $7,612; IQR fence $47,395) and highlights the zero floor applied to the 1,285 negative return transactions. Panel C details the depth of promotional markdowns during holiday versus non-holiday campaigns: MarkDown3 (event-specific holiday promotions) spikes from a negligible baseline during non-holiday weeks to over $14,000 per store during Thanksgiving, confirming the imperative of engineering promotional-holiday interaction features."
)

add_figure_with_caption(doc, "figures/fig2_outlier_and_markdown_analysis.png", "Figure 2: Missingness Profile Across Variables, Department Sales Distribution with Outlier Fences, and Promotional Markdown Depth.", width_inches=6.2)

add_p(doc, 
    "Figure 3 (Panel A) quantifies the empirical revenue lift across distinct holiday calendar events, demonstrating that Thanksgiving (+44.0%) and Pre-Christmas (+40.2%) dwarf routine holidays like Labor Day (+2.0%) and Super Bowl (+5.6%). Panel B traces the normalized trajectories of macroeconomic indicators from 2010 to 2012, showing a steady expansion in the Consumer Price Index (+7.2%) alongside a multi-year decline in regional Unemployment from 8.6% to 7.1%. Figure 4 presents the comprehensive Pearson correlation matrix, establishing that fifty-two-week seasonal demand (Lag_52, r = 0.97), short-term rolling volume (Rolling_Mean_4, r = 0.96), and immediate prior-week demand (Lag_1, r = 0.95) constitute the dominant linear determinants of weekly sales."
)

add_figure_with_caption(doc, "figures/fig3_holiday_and_macro_effects.png", "Figure 3: Empirical Weekly Revenue Lift by Holiday Calendar Event and Standardized Trajectories of Macroeconomic Indicators.", width_inches=6.2)
add_figure_with_caption(doc, "figures/fig4_correlation_matrix.png", "Figure 4: Pearson Correlation Matrix Across Autoregressive Lags, Rolling Averages, Store Size, and Macroeconomic Attributes.", width_inches=5.8)

add_heading_2(doc, "4.2 Quantitative Model Benchmark Comparison")
add_p(doc, 
    "All four models were trained on the 263,199 historical training records with w = 5 holiday sample weighting and evaluated across the 145,237 records of the chronological validation set. Table 4 presents the comprehensive evaluation metrics: WMAE, RMSE, MAE, R², Holiday MAE, Non-Holiday MAE, and Training Wall-Clock Latency."
)

tab4_headers = ["Model Architecture", "WMAE ($ USD) ↓", "RMSE ($ USD) ↓", "MAE ($ USD) ↓", "R² Score ↑", "Holiday MAE (w=5) ↓", "Regular MAE (w=1) ↓", "Training Latency"]
tab4_data = [
    ["Baseline (Ridge Regression)", "$4,393.17", "$6,616.57", "$2,514.98", "0.9183", "$10,108.52", "$1,835.29", "0.20 s"],
    ["Random Forest Regressor", "$1,791.54", "$4,413.86", "$1,520.75", "0.9637", "$2,615.57", "$1,422.75", "42.88 s"],
    ["XGBoost Regressor", "$1,837.57", "$4,306.19", "$1,523.89", "0.9654", "$2,792.11", "$1,410.37", "6.31 s"],
    ["LightGBM Regressor (Winner)", "$1,758.94", "$3,837.62", "$1,541.31", "0.9725", "$2,421.19", "$1,462.55", "4.91 s"]
]
add_table_with_caption(doc, "Table 4: Comprehensive Model Evaluation Across 145,237 Out-of-Sample Store-Department-Week Validation Observations", tab4_headers, tab4_data, [1.7, 0.9, 0.9, 0.8, 0.7, 1.1, 1.1, 0.6])

add_figure_with_caption(doc, "figures/fig5_model_comparison.png", "Figure 5: Comparative Evaluation of Predictive Architectures Across WMAE, RMSE, MAE, and R² Goodness-of-Fit.", width_inches=6.2)

add_p(doc, 
    "The experimental results establish several pivotal findings regarding model performance:\n"
    "1. Superiority of Gradient Boosting: LightGBM emerged as the top-performing model, achieving the lowest overall WMAE of $1,758.94—representing a massive 60.0% error reduction compared to the Baseline Ridge model ($4,393.17). LightGBM also achieved the lowest RMSE ($3,837.62, a 42.0% improvement over Baseline) and the highest coefficient of determination (R² = 0.9725), demonstrating that the model explains over 97.2% of total sales variance across the retail network.\n"
    "2. Holiday Peak Resilience: The performance divergence between linear and non-linear tree models is starkest during holiday weeks. Baseline Ridge Regression suffered a severe Holiday MAE of $10,108.52 per department-week. Because Ridge assumes linear combinations of recent demand, it over-smoothes dramatic holiday surges and overshoots during post-holiday lulls. LightGBM reduced Holiday MAE by 76.0% down to $2,421.19, providing reliable protection against holiday stockouts.\n"
    "3. Regular Week Precision: On standard non-holiday replenishment weeks, XGBoost achieved the lowest error of $1,410.37, closely matched by Random Forest ($1,422.75) and LightGBM ($1,462.55).\n"
    "4. Computational Efficiency: LightGBM trained across 263,199 records with 43 features in only 4.91 seconds—nearly 9x faster than Random Forest (42.88 seconds)—proving its suitability for real-time production retraining pipelines."
)

add_heading_2(doc, "4.3 Forecast Tracking and Parity Analysis")
add_p(doc, 
    "Figure 6 provides visual confirmation of model tracking across the 49-week out-of-sample validation horizon. In Panel A, aggregate weekly sales (black line) are benchmarked against model forecasts. The dotted grey Baseline Ridge model severely overshoots immediately following Thanksgiving and Christmas, lagging the true turning points. In sharp contrast, LightGBM (blue dashed line) and XGBoost (red dashed line) track the Black Friday $77M surge and the January post-holiday demand trough with remarkable fidelity. In Panel B, the actual versus predicted parity plot across 8,000 sampled validation observations demonstrates tight clustering along the ideal 45-degree line (y = x) across both high-volume departments (e.g., Grocery, Electronics) and small niche categories."
)

add_figure_with_caption(doc, "figures/fig6_actual_vs_predicted.png", "Figure 6: Chronological Validation Set Forecast Tracking (Nov 2011 – Oct 2012) and Actual versus Predicted 45-Degree Parity Scatter.", width_inches=6.2)

add_heading_2(doc, "4.4 Feature Gain Attribution and Interpretation")
add_p(doc, 
    "Table 5 and Figure 7 detail the relative feature importance determined via normalized split gain attribution across XGBoost and LightGBM, alongside Random Forest Gini impurity importance."
)

tab5_headers = ["Rank", "Engineered Feature Name", "Functional Feature Class", "XGBoost Gain (%)", "LightGBM Gain (%)", "Random Forest Imp. (%)"]
tab5_data = [
    ["1", "Lag_52", "Annual Seasonal Autoregression (t-52)", "31.45%", "40.87%", "26.30%"],
    ["2", "Rolling_Mean_4", "Short-Term Moving Average (t-1 shifted)", "24.61%", "17.19%", "29.15%"],
    ["3", "Lag_1", "Immediate Prior Week Demand (t-1)", "12.97%", "22.59%", "20.95%"],
    ["4", "Store_Dept_Mean", "Out-of-Sample Historical Target Mean", "6.56%", "3.91%", "5.38%"],
    ["5", "Is_Thanksgiving", "Holiday Calendar Flag (Week 47, w=5)", "4.36%", "2.32%", "0.79%"],
    ["6", "Lag_2", "Bi-Weekly Paycheck Lag (t-2)", "4.35%", "4.96%", "7.91%"],
    ["7", "Is_Christmas", "Holiday Calendar Flag (Week 52, w=5)", "2.69%", "0.36%", "0.10%"],
    ["8", "Pre_Christmas_Peak", "Pre-Holiday Shopping Surge (W49–W51)", "2.34%", "0.34%", "0.23%"],
    ["9", "Store_Dept_Std", "Historical Department Volatility", "1.73%", "2.28%", "1.63%"],
    ["10", "Store_Dept_Median", "Robust Historical Target Median", "1.57%", "0.35%", "2.99%"]
]
add_table_with_caption(doc, "Table 5: Feature Importance Hierarchy Across Tree Ensembles Derived via Normalized Split Gain Attribution", tab5_headers, tab5_data, [0.6, 1.4, 2.2, 1.0, 1.0, 1.1])

add_figure_with_caption(doc, "figures/fig7_feature_importance.png", "Figure 7: Top 15 Predictive Features Ranked by Relative Split Gain Contribution for XGBoost and LightGBM.", width_inches=6.2)

add_p(doc, 
    "Domain interpretation of the gain attribution confirms that retail demand is anchored primarily by annual seasonality: Lag_52 is the undisputed #1 feature across both gradient-boosted models, contributing 40.87% of total gain in LightGBM and 31.45% in XGBoost. Department sales from the exact corresponding week of the prior year establish the core demand envelope. Short-term momentum features (Lag_1 and Rolling_Mean_4) provide the second layer of predictive signal, contributing a combined 39.78% in LightGBM and 37.58% in XGBoost by capturing local customer foot traffic trends and recent macroeconomic adjustments. Explicit holiday indicators (Is_Thanksgiving, Is_Christmas, and Pre_Christmas_Peak) account for nearly 10% of total gain in XGBoost, providing the crucial non-linear upward step required to capture high-velocity holiday surges."
)

add_heading_2(doc, "4.5 Supply Chain Inventory Optimization and Cost Reduction")
add_p(doc, 
    "Figure 8 translates statistical accuracy gains directly into supply chain financial metrics. Panel A demonstrates the dramatic contraction in holiday error achieved by LightGBM ($2,421.19) compared to Baseline Ridge ($10,108.52). In Panel B, applying the inventory mismatch cost formulation (Equation 6) across the 145,237 validation department-weeks reveals that deploying machine learning cuts total network inventory mismatch costs from $80.3M down to $48.6M. This yields an estimated annualized cost savings of $31.7M—a 39.5% operational cost reduction across all 45 stores. Broken down by store format: Type A Supercenters save $17.1M (-36.7%), Type B Discount Stores save $12.8M (-43.0%), and Type C Neighborhood Markets save $1.8M (-43.5%)."
)

add_figure_with_caption(doc, "figures/fig8_supply_chain_impact.png", "Figure 8: Error Breakdown on Holiday vs. Regular Weeks and Supply Chain Mismatch Cost Savings Across Store Formats.", width_inches=6.2)

# ==============================================================================
# CHAPTER 5: CONCLUSION
# ==============================================================================
add_heading_1(doc, "Chapter 5: Conclusion")

add_p(doc, 
    "This study successfully designed, implemented, and validated an end-to-end predictive analytics regression pipeline for multi-store retail sales forecasting following the formal Knowledge Discovery in Databases (KDD) process. By integrating 421,570 historical transaction records across 45 stores and 81 departments with promotional markdown schedules, holiday calendars, and macroeconomic indicators, the system addressed the operational challenges of modern retail inventory planning. Robust preprocessing successfully resolved extensive promotional markdown missingness (64%–74%), handled customer accounting returns, and preserved genuine holiday demand spikes without statistical bias. Engineering 43 leak-free predictive features—spanning multi-horizon autoregressive lags, shifted rolling aggregations, and Fourier cyclical transforms—equipped tree-based ensembles with rich temporal context without introducing look-ahead leakage.",
    bold_prefix="5.1 Summary of Research Achievements: "
)

add_p(doc, 
    "Quantitative benchmarking established that LightGBM is the superior predictive architecture for retail sales forecasting, achieving a WMAE of $1,758.94 (a 60.0% error reduction relative to the Baseline Ridge model), an RMSE of $3,837.62, and an R² of 0.9725. Crucially, LightGBM reduced Holiday MAE by 76.0% ($2,421.19 vs. $10,108.52), directly mitigating the risk of catastrophic stockouts during Black Friday and Christmas. From an operational supply chain perspective, these accuracy gains translate into an estimated $31.7M (39.5%) reduction in inventory holding and stockout mismatch costs across the 45 Walmart stores.",
    bold_prefix="5.2 Operational Supply Chain Recommendations: "
)

add_p(doc, 
    "Based on the empirical findings, two actionable deployment policies are recommended for retail operations: (1) A Dual-Regime Deployment Policy: Deploy LightGBM for Q4 holiday pre-staging and distribution center safety stock allocation, where its superior handling of high-stakes holiday spikes (w = 5) prevents stockouts, while utilizing XGBoost for routine weekly replenishment, where it achieved the lowest regular-week MAE ($1,410.37); (2) Early Promotional Buffer Synchronization: Because MarkDown2 and MarkDown3 exhibit high concentration during Thanksgiving and pre-Christmas weeks, procurement teams should pre-allocate safety stock 3 to 4 weeks prior to Weeks 47 and 50.\n\n"
    "Future Research Directions: While the current system achieves excellent point-prediction accuracy, future work will extend the framework along two avenues: (1) Probabilistic Quantile Regression: Optimizing pinball loss functions (at τ = 0.50, 0.90, 0.95) and applying Conformal Prediction to generate distribution-free prediction intervals, enabling dynamic, service-level-driven safety stock calculation; (2) Deep Learning Architectures: Benchmarking multi-horizon Temporal Fusion Transformers (TFT) with self-attention against gradient-boosted trees, and applying Minimum Trace (MinT) hierarchical forecast reconciliation across national, store format, store, and department aggregations.",
    bold_prefix="5.3 Limitations and Future Scope: "
)

# ==============================================================================
# CHAPTER 6: REFERENCES
# ==============================================================================
add_heading_1(doc, "Chapter 6: References")

references_list = [
    "[1] U. Fayyad, G. Piatetsky-Shapiro, and P. Smyth, \"From Data Mining to Knowledge Discovery in Databases,\" AI Magazine, vol. 17, no. 3, pp. 37–54, 1996.",
    "[2] Walmart Recruiting, \"Walmart Recruiting — Store Sales Forecasting Competition Dataset,\" Kaggle Inc., 2014. [Online]. Available: https://www.kaggle.com/competitions/walmart-recruiting-store-sales-forecasting/data",
    "[3] T. Chen and C. Guestrin, \"XGBoost: A Scalable Tree Boosting System,\" in Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining (KDD '16), San Francisco, CA, USA, 2016, pp. 785–794.",
    "[4] G. Ke, Q. Meng, T. Finley, T. Wang, W. Chen, W. Ma, Q. Ye, and T.-Y. Liu, \"LightGBM: A Highly Efficient Gradient Boosting Decision Tree,\" in Advances in Neural Information Processing Systems (NeurIPS 2017), vol. 30, pp. 3146–3154, 2017.",
    "[5] L. Breiman, \"Random Forests,\" Machine Learning, vol. 45, no. 1, pp. 5–32, 2001.",
    "[6] S. Makridakis, E. Spiliotis, and V. Assimakopoulos, \"The M5 Accuracy Competition: Results, Findings, and Conclusions,\" International Journal of Forecasting, vol. 38, no. 4, pp. 1346–1364, 2022.",
    "[7] R. J. Hyndman and G. Athanasopoulos, Forecasting: Principles and Practice, 3rd ed. Melbourne, Australia: OTexts, 2021.",
    "[8] G. E. P. Box, G. M. Jenkins, G. C. Reinsel, and G. M. Ljung, Time Series Analysis: Forecasting and Control, 5th ed. Hoboken, NJ, USA: John Wiley & Sons, 2015.",
    "[9] D. K. Barrow and N. Kourentzes, \"Distributions of Forecasting Errors of Forecast Combinations: Implications for Inventory Management,\" International Journal of Production Economics, vol. 177, pp. 24–33, 2016.",
    "[10] R. Fildes, S. Ma, and S. Kolassa, \"Retail Forecasting: Research and Practice,\" International Journal of Forecasting, vol. 38, no. 4, pp. 1283–1318, 2022.",
    "[11] A. E. Hoerl and R. W. Kennard, \"Ridge Regression: Biased Estimation for Nonorthogonal Problems,\" Technometrics, vol. 12, no. 1, pp. 55–67, 1970.",
    "[12] S. Chopra and P. Meindl, Supply Chain Management: Strategy, Planning, and Operation, 7th ed. Boston, MA, USA: Pearson Education, 2019."
]

for ref in references_list:
    p_ref = doc.add_paragraph()
    set_para_format(p_ref, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=4, line_spacing=1.1)
    r_ref = p_ref.add_run(ref)
    r_ref.font.name = 'Times New Roman'
    r_ref.font.size = Pt(11)

target_filename = "24070521505_Dev_Dilip_Dhapodkar.docx"
doc.save(target_filename)
print(f"Successfully generated {target_filename}!")

# Also make duplicate copy with 24070521505_Dev_Dhapodkar.docx and update Walmart_Sales_Forecasting_Report.docx
import shutil
shutil.copyfile(target_filename, "24070521505_Dev_Dhapodkar.docx")
shutil.copyfile(target_filename, "Walmart_Sales_Forecasting_Report.docx")
print("Also created 24070521505_Dev_Dhapodkar.docx and updated Walmart_Sales_Forecasting_Report.docx!")
