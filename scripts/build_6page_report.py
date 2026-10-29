import os
import shutil
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image as RLImage,
    Table, TableStyle, PageBreak, KeepTogether
)
import pypdf

# ==============================================================================
# 1. BUILD WORD DOCUMENT (.docx)
# ==============================================================================
doc = Document()

# Set Page size to A4: 210mm x 297mm (8.27 in x 11.69 in)
for section in doc.sections:
    section.page_width = Inches(8.27)
    section.page_height = Inches(11.69)
    section.top_margin = Inches(0.85)
    section.bottom_margin = Inches(0.85)
    section.left_margin = Inches(0.85)
    section.right_margin = Inches(0.85)

style_normal = doc.styles['Normal']
style_normal.font.name = 'Times New Roman'
style_normal.font.size = Pt(12)
style_normal.font.color.rgb = RGBColor(0, 0, 0)

def set_p(p, align=WD_ALIGN_PARAGRAPH.JUSTIFY, sb=6, sa=6, ls=1.12):
    p.alignment = align
    p.paragraph_format.space_before = Pt(sb)
    p.paragraph_format.space_after = Pt(sa)
    p.paragraph_format.line_spacing = ls

def p_body(doc, text, bold_pre=None):
    p = doc.add_paragraph()
    set_p(p, WD_ALIGN_PARAGRAPH.JUSTIFY, sb=6, sa=6)
    if bold_pre:
        r_pre = p.add_run(bold_pre)
        r_pre.font.name = 'Times New Roman'
        r_pre.font.size = Pt(12)
        r_pre.font.bold = True
    r = p.add_run(text)
    r.font.name = 'Times New Roman'
    r.font.size = Pt(12)
    return p

def p_h1(doc, text):
    p = doc.add_paragraph()
    set_p(p, WD_ALIGN_PARAGRAPH.LEFT, sb=12, sa=5)
    r = p.add_run(text)
    r.font.name = 'Times New Roman'
    r.font.size = Pt(15)
    r.font.bold = True
    r.font.color.rgb = RGBColor(15, 41, 66)
    return p

def p_h2(doc, text):
    p = doc.add_paragraph()
    set_p(p, WD_ALIGN_PARAGRAPH.LEFT, sb=9, sa=4)
    r = p.add_run(text)
    r.font.name = 'Times New Roman'
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0, 113, 206)
    return p

def docx_table(doc, cap_text, headers, rows_data, col_widths=None):
    # Caption ABOVE table
    p_c = doc.add_paragraph()
    set_p(p_c, WD_ALIGN_PARAGRAPH.LEFT, sb=8, sa=3)
    r = p_c.add_run(cap_text)
    r.font.name = 'Times New Roman'
    r.font.size = Pt(11)
    r.font.bold = True
    r.font.color.rgb = RGBColor(15, 41, 66)

    tbl = doc.add_table(rows=len(rows_data) + 1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False

    # Header
    for i, h in enumerate(headers):
        cell = tbl.cell(0, i)
        cell.text = str(h)
        if col_widths: cell.width = Inches(col_widths[i])
        cell.vertical_anchor = WD_ALIGN_VERTICAL.CENTER
        shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="0F2942"/>')
        cell._tc.get_or_add_tcPr().append(shading)
        p = cell.paragraphs[0]
        set_p(p, WD_ALIGN_PARAGRAPH.CENTER, sb=3, sa=3, ls=1.0)
        for run in p.runs:
            run.font.name = 'Times New Roman'
            run.font.size = Pt(9.5)
            run.font.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)

    # Rows
    for r_i, row in enumerate(rows_data):
        bg = "F8FAFC" if r_i % 2 == 1 else "FFFFFF"
        for c_i, val in enumerate(row):
            cell = tbl.cell(r_i + 1, c_i)
            cell.text = str(val)
            if col_widths: cell.width = Inches(col_widths[c_i])
            cell.vertical_anchor = WD_ALIGN_VERTICAL.CENTER
            shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{bg}"/>')
            cell._tc.get_or_add_tcPr().append(shading)
            p = cell.paragraphs[0]
            al = WD_ALIGN_PARAGRAPH.LEFT if c_i == 0 or len(str(val)) > 20 else WD_ALIGN_PARAGRAPH.CENTER
            set_p(p, al, sb=2.5, sa=2.5, ls=1.02)
            for run in p.runs:
                run.font.name = 'Times New Roman'
                run.font.size = Pt(9.0)
                run.font.color.rgb = RGBColor(30, 41, 59)

def docx_fig(doc, path, cap_text, width_in=5.8):
    p_img = doc.add_paragraph()
    set_p(p_img, WD_ALIGN_PARAGRAPH.CENTER, sb=6, sa=2)
    p_img.add_run().add_picture(path, width=Inches(width_in))

    # Caption BELOW figure
    p_c = doc.add_paragraph()
    set_p(p_c, WD_ALIGN_PARAGRAPH.CENTER, sb=2, sa=6)
    r = p_c.add_run(cap_text)
    r.font.name = 'Times New Roman'
    r.font.size = Pt(10)
    r.font.italic = True
    r.font.color.rgb = RGBColor(71, 85, 105)

def docx_eq(doc, formula_str, eq_num):
    tbl = doc.add_table(rows=1, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    c_l = tbl.cell(0, 0)
    c_r = tbl.cell(0, 1)
    c_l.width = Inches(5.6)
    c_r.width = Inches(0.9)
    for c in [c_l, c_r]:
        tcPr = c._tc.get_or_add_tcPr()
        tcBorders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:top w:val="none"/><w:left w:val="none"/><w:bottom w:val="none"/><w:right w:val="none"/></w:tcBorders>')
        tcPr.append(tcBorders)

    p_l = c_l.paragraphs[0]
    set_p(p_l, WD_ALIGN_PARAGRAPH.CENTER, sb=3, sa=3, ls=1.05)
    r_l = p_l.add_run(formula_str)
    r_l.font.name = 'Times New Roman'
    r_l.font.size = Pt(11)
    r_l.font.italic = True

    p_r = c_r.paragraphs[0]
    set_p(p_r, WD_ALIGN_PARAGRAPH.RIGHT, sb=3, sa=3, ls=1.05)
    r_r = p_r.add_run(f"({eq_num})")
    r_r.font.name = 'Times New Roman'
    r_r.font.size = Pt(11)
    r_r.font.bold = True

# --- HEADER BLOCK ---
p_hdr = doc.add_paragraph()
set_p(p_hdr, WD_ALIGN_PARAGRAPH.CENTER, sb=6, sa=2)
r1 = p_hdr.add_run("PREDICTIVE ANALYTICS — CONTINUOUS ASSESSMENT 3 (CA3)\n")
r1.font.name = 'Times New Roman'
r1.font.size = Pt(12)
r1.font.bold = True
r1.font.color.rgb = RGBColor(0, 113, 206)

r2 = p_hdr.add_run("Sales Forecasting: End-to-End Predictive Analytics Model Development and Supply Chain Inventory Optimization Using the KDD Process\n")
r2.font.name = 'Times New Roman'
r2.font.size = Pt(16)
r2.font.bold = True
r2.font.color.rgb = RGBColor(15, 41, 66)

r3 = p_hdr.add_run("Submitted By: Dev Dilip Dhapodkar   |   PRN: 24070521505   |   Symbiosis International University")
r3.font.name = 'Times New Roman'
r3.font.size = Pt(11)
r3.font.color.rgb = RGBColor(71, 85, 105)

# CHAPTER 1
p_h1(doc, "Chapter 1: Introduction")
p_body(doc, 
    "In large-scale retail commerce, accurate sales forecasting constitutes the operational foundation of multi-echelon supply chain coordination. Retail enterprises such as Walmart manage complex fulfillment networks encompassing thousands of store-department intersections across heterogeneous geographical markets. Each store location is subject to long-term macroeconomic trends, localized disposable income variations, ambient weather conditions, multi-channel promotional markdowns, and abrupt calendar holiday surges. Conventional replenishment models relying on historical moving averages or unadjusted exponential smoothing repeatedly fail to handle these multi-frequency patterns. Inaccurate forecasts create two severe operational risks: catastrophic out-of-stock (OOS) conditions during high-volume holiday periods that permanently erode market share and customer goodwill, and excessive inventory accumulation during routine trading cycles that inflates holding overhead and triggers forced margin-dilutive post-holiday clearance markdowns.",
    bold_pre="1.1 Context and Problem Domain: "
)
p_body(doc, 
    "This investigation develops, validates, and interprets an end-to-end predictive analytics regression pipeline that forecasts weekly department-level sales across multiple retail stores using historical transaction records, promotional price markdown schedules, holiday calendars, and macroeconomic indicators. Implemented on the benchmark Kaggle Walmart Recruiting dataset, the analytical framework adheres strictly to the formal Knowledge Discovery in Databases (KDD) process. Specifically, the model forecasts weekly revenue across 45 physical stores and 81 departments across three distinct retail formats: Type A Supercenters, Type B Discount Stores, and Type C Neighborhood Markets.",
    bold_pre="1.2 Research Objectives and Scope: "
)
p_body(doc, 
    "In retail supply chains, forecast error costs exhibit acute operational asymmetry. During routine mid-year weeks, moderate prediction errors can be absorbed through standard safety stock buffers and scheduled replenishment. Conversely, during major retail holidays such as Thanksgiving (Black Friday) and the pre-Christmas shopping peak, consumer foot traffic spikes by 40% to 50%, lead times from regional distribution centers are saturated, and stockouts cannot be alleviated through emergency deliveries. To formalize this business reality, the evaluation protocol employs the official Weighted Mean Absolute Error (WMAE) metric, which assigns a five-fold penalty (w = 5) to holiday weeks relative to regular baseline weeks (w = 1). The predictive system developed herein is explicitly calibrated to optimize this asymmetric cost surface.",
    bold_pre="1.3 Asymmetric Supply Chain Cost Structure: "
)

# CHAPTER 2
p_h1(doc, "Chapter 2: Literature Review")
p_body(doc, 
    "Retail demand forecasting methodologies have evolved substantially over the past two decades. Early parametric approaches relied on univariate statistical formulations, primarily Autoregressive Integrated Moving Average (ARIMA), Seasonal ARIMA (SARIMA), and Holt-Winters Exponential Smoothing state-space models. While effective for isolated stationary series, univariate parametric models require fitting and maintaining thousands of independent local models across every store-department pair and struggle to incorporate high-dimensional exogenous drivers—such as multi-channel promotional markdowns and regional economic indices—without parameter instability.",
    bold_pre="2.1 Classical Econometric Formulations: "
)
p_body(doc, 
    "To overcome these limitations, modern predictive analytics utilizes global machine learning architectures that pool observations across all store and department hierarchies into a unified tabular feature space. Breiman's Random Forest established the power of bootstrap aggregation to reduce predictive variance and model non-linear interactions. More recently, extreme gradient boosting architectures—notably XGBoost (Chen and Guestrin) and LightGBM (Ke et al.)—have become the premier standard in retail analytics. These architectures leverage second-order Taylor approximations, tree regularization penalties, and histogram-based binning. The M5 Forecasting Competition (Makridakis et al.) conclusively proved that global tree ensembles enriched with multi-horizon autoregressive lags and shifted rolling statistics outperform classical models and deep recurrent networks on promotional retail demand series.",
    bold_pre="2.2 Global Gradient-Boosted Decision Trees: "
)

lit_headers = ["Author(s) & Year", "Methodology / Model", "Dataset / Domain", "Key Strengths & Identified Limitations"]
lit_data = [
    ["Box & Jenkins (2015); Hyndman (2021)", "ARIMA, SARIMAX & ETS State-Space", "Univariate Retail Series", "Captures linear autocorrelation; fails on abrupt promotional spikes and cross-store data pooling."],
    ["Breiman (2001)", "Random Forest Regressor (Bagging)", "Tabular Machine Learning", "Robust against noisy outliers; high computational memory overhead and slower inference speed."],
    ["Chen & Guestrin (2016)", "XGBoost (Regularized GBDT)", "High-Dimensional Data", "Second-order Taylor optimization with L1/L2 leaf regularization; depth-wise tree growth."],
    ["Ke et al. (2017)", "LightGBM (Leaf-Wise Histogram Boosting)", "Multi-Store Retail Data", "Leaf-wise splitting with histogram binning; >80% faster training with superior convergence."],
    ["Makridakis et al. (2022)", "M5 Accuracy Competition (Tree Ensembles)", "Walmart Hierarchical (42,840 series)", "Proved global GBDT ensembles with lag and rolling features decisively outperform neural architectures."],
    ["Barrow & Kourentzes (2016)", "Inventory Safety Stock Optimization", "Supply Chain Operations", "Demonstrated that reducing peak-period forecast variance yields substantial buffer stockholding savings."]
]
docx_table(doc, "Table 1: Synthesis of Relevant Prior Literature in Predictive Retail Analytics and Machine Learning", lit_headers, lit_data, [1.4, 1.6, 1.4, 2.1])

p_body(doc, 
    "Existing empirical implementations often suffer from two methodological weaknesses: inadvertent look-ahead leakage in rolling window statistics, and model optimization against symmetric metrics that ignore the 5x stockout penalty of holiday peaks. This study addresses both issues through leak-free feature engineering and sample-weighted optimization.",
    bold_pre="2.3 Research Gap Addressed: "
)

# CHAPTER 3
p_h1(doc, "Chapter 3: Workflow / Predictive Modelling Process")
p_body(doc, 
    "The analytical workflow operationalizes the classical Knowledge Discovery in Databases (KDD) process through seven structured phases: Data Selection, Preprocessing, Feature Engineering, Exploratory Data Analysis, Model Training, Evaluation, and Supply Chain Interpretation.",
    bold_pre="3.1 The KDD Methodological Architecture: "
)
p_body(doc, 
    "The dataset integrates four relational files from the Walmart Recruiting repository: historical department transactions (train.csv), environmental and economic attributes (features.csv), store metadata (stores.csv), and holdout structures (test.csv). Merged on [Store, Date, IsHoliday] and [Store], the analytical training matrix contains 421,570 records spanning 143 consecutive weeks (February 2010 to October 2012) across 45 stores and 81 departments.",
    bold_pre="3.2 Stage 1: Data Selection and Relational Ingestion: "
)

tab2_headers = ["File Name", "Records", "Columns", "Primary Key", "Attribute Role in Predictive Pipeline"]
tab2_data = [
    ["stores.csv", "45", "3", "Store", "Store format Type (A: 22 Supercenters, B: 17 Discount, C: 6 Neighborhood) and physical Size (sq. ft.)."],
    ["features.csv", "8,190", "12", "(Store, Date)", "Contextual series: Temperature, Fuel_Price, MarkDown1–MarkDown5, CPI, Unemployment, and IsHoliday."],
    ["train.csv", "421,570", "5", "(Store, Dept, Date)", "Historical weekly sales: Weekly_Sales across 45 stores and 81 departments over 143 weeks."],
    ["test.csv", "115,064", "4", "(Store, Dept, Date)", "Evaluation horizon spanning 39 weeks (November 2012 to July 2013) for out-of-sample deployment."]
]
docx_table(doc, "Table 2: Relational Database Schema and Ingestion Properties of the Walmart Corpus", tab2_headers, tab2_data, [1.1, 0.9, 0.9, 1.2, 2.4])

p_body(doc, 
    "Data diagnostics identified three primary anomalies: promotional markdown missingness, macroeconomic indicator lags, and accounting merchandise returns manifesting as negative sales values.",
    bold_pre="3.3 Stage 2: Data Preprocessing, Imputation and Outlier Treatment: "
)

tab3_headers = ["Attribute / Column", "Missing Count", "Missing %", "Root Operational Cause", "Engineered Treatment Protocol"]
tab3_data = [
    ["MarkDown1–MarkDown5", "270K–310K", "64.1%–73.6%", "Tracking began Nov 2011; NA denotes inactive promo.", "Extracted Has_MarkDown indicator; structural 0.0 fill; clipped < 0."],
    ["CPI & Unemployment", "585 (features)", "7.14%", "Macroeconomic indices lagged in final test weeks.", "Store-grouped chronological forward/backward fill (ffill / bfill)."],
    ["Weekly_Sales (< $0)", "1,285 records", "0.30%", "Post-holiday customer returns & accounting credits.", "Floored at $0.00 to guarantee valid physical demand target."],
    ["Extreme Outliers", "422 records", "0.10%", "Bulk institutional sales vs. real Black Friday spikes.", "Winsorized non-holiday records at 99.95th pct ($183.5K); preserved Holidays."]
]
docx_table(doc, "Table 3: Comprehensive Diagnostic Profile of Missing Values, Anomalies, and Imputation Protocols", tab3_headers, tab3_data, [1.4, 1.1, 0.9, 1.5, 1.6])

p_body(doc, 
    "To equip regression models with rich temporal signals without look-ahead bias, 43 domain predictors were constructed across five classes: (1) Autoregressive Lags (Lag_1, Lag_2, Lag_4, Lag_52); (2) Leak-Free Shifted Rolling Windows computed on t-1 shifted demand (Rolling_Mean_4, Rolling_Std_4, Rolling_Mean_12, Momentum_1_4); (3) Explicit Holiday Calendar Indicators (Is_SuperBowl, Is_LaborDay, Is_Thanksgiving, Is_Christmas, Pre_Christmas_Peak); (4) Fourier Cyclical Seasonality Transforms enforcing circular calendar continuity; and (5) Out-of-Sample Historical Target Statistics (Store_Dept_Mean, Store_Dept_Median, Store_Dept_Std computed strictly on the training partition).",
    bold_pre="3.4 Stage 3: Multi-Scale Feature Engineering Pipeline: "
)

docx_eq(doc, "Week_Sin = sin(2pi * Week / 52),    Week_Cos = cos(2pi * Week / 52)", "1")

p_body(doc, 
    "Four distinct model families were benchmarked: Baseline Ridge Regression optimizing L2-regularized squared loss (Equation 2), Random Forest Regressor averaging B = 100 decorrelated trees (Equation 3), and XGBoost and LightGBM optimizing second-order regularized gradient boosting (Equation 4). Models were evaluated under asymmetric Weighted Mean Absolute Error (Equation 5) and inventory mismatch penalty cost (Equation 6) over a chronological split at November 25, 2011 (263,199 train / 145,237 validation records covering 49 weeks and all 4 holidays).",
    bold_pre="3.5 Stage 5 & 6: Predictive Model Formulation and Evaluation Metric: "
)

docx_eq(doc, "min_beta { ||y - X beta||_2^2 + alpha ||beta||_2^2 },    alpha = 100.0", "2")
docx_eq(doc, "y_hat_RF(x) = (1 / B) * Sum_{b=1}^{B} T_b(x)", "3")
docx_eq(doc, "L^(t) approx Sum_{i=1}^{N} w_i [ g_i f_t(x_i) + (1/2) h_i f_t^2(x_i) ] + Omega(f_t)", "4")
docx_eq(doc, "WMAE = [ Sum_{i=1}^{N} w_i * |y_i - y_hat_i| ] / [ Sum_{i=1}^{N} w_i ],    w_i = 5 if IsHoliday_i else 1", "5")
docx_eq(doc, "C_mismatch = gamma * Sum_{i=1}^{N} |y_i - y_hat_i|,    gamma = 0.22", "6")

# CHAPTER 4
p_h1(doc, "Chapter 4: Results and Discussion")
p_body(doc, 
    "Exploratory Data Analysis revealed key demand dynamics across the network. Average store revenue fluctuates around $47.1M/week during baseline periods but spikes to $66.6M on Thanksgiving (+44.0% lift) and $80.0M during Pre-Christmas Weeks 49–51 (+40.2% lift). Physical store area exhibits a strong linear correlation (r = 0.81) with sales across Supercenters ($1.45M/wk), Discount Stores ($0.79M/wk), and Neighborhood Markets ($0.46M/wk). Promotional MarkDown3 spikes to over $14,000/store during Thanksgiving, confirming the need for holiday-promo interaction terms.",
    bold_pre="4.1 Exploratory Data Analysis Insights: "
)

docx_fig(doc, "figures/fig1_eda_sales_overview.png", "Figure 1: Aggregate Weekly Retail Sales Trajectory (2010–2012), Format Type Distribution, and Store Area Size Elasticity.", width_in=5.6)
docx_fig(doc, "figures/fig3_holiday_and_macro_effects.png", "Figure 2: Empirical Weekly Revenue Lift by Holiday Calendar Event and Standardized Trajectories of Macroeconomic Indicators.", width_in=5.6)

p_body(doc, 
    "Table 4 and Figure 3 present out-of-sample benchmark performance across the 145,237 validation observations. LightGBM emerged as the champion model, achieving the lowest WMAE ($1,758.94, a 60.0% error reduction vs. Baseline Ridge at $4,393.17), lowest RMSE ($3,837.62), and highest goodness-of-fit (R² = 0.9725) in only 4.91 seconds. Crucially, LightGBM slashed Holiday MAE by 76.0% ($2,421.19 vs. $10,108.52), protecting against Black Friday and Christmas stockouts. XGBoost achieved the best non-holiday accuracy ($1,410.37 MAE).",
    bold_pre="4.2 Quantitative Model Benchmark Comparison: "
)

tab4_headers = ["Model Architecture", "WMAE ($ USD) ↓", "RMSE ($ USD) ↓", "MAE ($ USD) ↓", "R² Score ↑", "Holiday MAE (w=5) ↓", "Regular MAE (w=1) ↓", "Training Time"]
tab4_data = [
    ["Baseline (Ridge Regression)", "$4,393.17", "$6,616.57", "$2,514.98", "0.9183", "$10,108.52", "$1,835.29", "0.20 s"],
    ["Random Forest Regressor", "$1,791.54", "$4,413.86", "$1,520.75", "0.9637", "$2,615.57", "$1,422.75", "42.88 s"],
    ["XGBoost Regressor", "$1,837.57", "$4,306.19", "$1,523.89", "0.9654", "$2,792.11", "$1,410.37", "6.31 s"],
    ["LightGBM Regressor (Winner)", "$1,758.94", "$3,837.62", "$1,541.31", "0.9725", "$2,421.19", "$1,462.55", "4.91 s"]
]
docx_table(doc, "Table 4: Comprehensive Model Evaluation Across 145,237 Out-of-Sample Store-Department-Week Validation Observations", tab4_headers, tab4_data, [1.6, 0.8, 0.8, 0.75, 0.65, 1.0, 1.0, 0.55])

docx_fig(doc, "figures/fig5_model_comparison.png", "Figure 3: Comparative Evaluation of Predictive Architectures Across WMAE, RMSE, MAE, and R² Goodness-of-Fit.", width_in=5.6)
docx_fig(doc, "figures/fig6_actual_vs_predicted.png", "Figure 4: Chronological Validation Set Forecast Tracking (Nov 2011 – Oct 2012) and Actual versus Predicted 45-Degree Parity Scatter.", width_in=5.6)

p_body(doc, 
    "Normalized split gain attribution (Table 5) confirms that retail demand is anchored primarily by year-over-year seasonality: Lag_52 is the #1 feature in both LightGBM (40.87%) and XGBoost (31.45%). Short-term momentum (Lag_1 and Rolling_Mean_4) provides the second layer of predictive signal (38% to 40% combined gain), while holiday indicators account for nearly 10% of gain in XGBoost.",
    bold_pre="4.3 Feature Gain Attribution and Interpretation: "
)

tab5_headers = ["Rank", "Engineered Feature Name", "Functional Feature Class", "XGBoost Gain (%)", "LightGBM Gain (%)", "Random Forest Imp. (%)"]
tab5_data = [
    ["1", "Lag_52", "Annual Seasonal Autoregression (t-52)", "31.45%", "40.87%", "26.30%"],
    ["2", "Rolling_Mean_4", "Short-Term Moving Average (t-1 shifted)", "24.61%", "17.19%", "29.15%"],
    ["3", "Lag_1", "Immediate Prior Week Demand (t-1)", "12.97%", "22.59%", "20.95%"],
    ["4", "Store_Dept_Mean", "Out-of-Sample Historical Target Mean", "6.56%", "3.91%", "5.38%"],
    ["5", "Is_Thanksgiving", "Holiday Calendar Flag (Week 47, w=5)", "4.36%", "2.32%", "0.79%"],
    ["6", "Lag_2", "Bi-Weekly Paycheck Lag (t-2)", "4.35%", "4.96%", "7.91%"]
]
docx_table(doc, "Table 5: Feature Importance Hierarchy Across Tree Ensembles Derived via Normalized Split Gain Attribution", tab5_headers, tab5_data, [0.6, 1.4, 2.2, 0.9, 0.9, 0.9])

p_body(doc, 
    "Applying the inventory mismatch cost formulation (Equation 6) across validation records demonstrates that machine learning deployment reduces mismatch costs from $80.3M (Baseline) to $48.6M—saving $31.7M (-39.5%) across all 45 stores ($17.1M saved in Supercenters, $12.8M in Discount Stores, $1.8M in Neighborhood Markets).",
    bold_pre="4.4 Supply Chain Inventory Optimization: "
)

docx_fig(doc, "figures/fig8_supply_chain_impact.png", "Figure 5: Error Breakdown on Holiday vs. Regular Weeks and Supply Chain Mismatch Cost Savings Across Store Formats.", width_in=5.6)

# CHAPTER 5
p_h1(doc, "Chapter 5: Conclusion")
p_body(doc, 
    "This research successfully established an end-to-end predictive analytics regression pipeline for multi-store retail sales forecasting adhering to the KDD process. Integrating 421,570 transaction records across 45 stores and 81 departments with promotional markdowns and macroeconomic context, the system resolved promotional data sparsity, handled return transactions, and preserved genuine holiday spikes without look-ahead bias.",
    bold_pre="5.1 Summary of Research Achievements: "
)
p_body(doc, 
    "LightGBM achieved superior predictive accuracy (WMAE $1,758.94, RMSE $3,837.62, R² = 0.9725) and slashed holiday error by 76.0% ($2,421.19 vs. $10,108.52). We recommend a dual-regime operational deployment: LightGBM for Q4 holiday inventory pre-staging and distribution center buffer allocation, and XGBoost for routine weekly store replenishment. Procurement teams should pre-stage inventory 3 to 4 weeks prior to Weeks 47 and 50 to synchronize with scheduled promotional markdown spikes.",
    bold_pre="5.2 Operational Recommendations: "
)
p_body(doc, 
    "Future investigations will extend point predictions to probabilistic quantile forecasting (Conformal Prediction) to generate dynamic safety stock reorder levels, and benchmark Temporal Fusion Transformers (TFT) with MinT hierarchical forecast reconciliation.",
    bold_pre="5.3 Limitations and Future Scope: "
)

# CHAPTER 6
p_h1(doc, "Chapter 6: References")
refs = [
    "[1] U. Fayyad, G. Piatetsky-Shapiro, and P. Smyth, \"From Data Mining to Knowledge Discovery in Databases,\" AI Magazine, vol. 17, no. 3, pp. 37–54, 1996.",
    "[2] Walmart Recruiting, \"Walmart Recruiting — Store Sales Forecasting Competition Dataset,\" Kaggle Inc., 2014. [Online]. Available: https://www.kaggle.com/competitions/walmart-recruiting-store-sales-forecasting/data",
    "[3] T. Chen and C. Guestrin, \"XGBoost: A Scalable Tree Boosting System,\" in Proc. 22nd ACM SIGKDD Int. Conf. Knowledge Discovery and Data Mining (KDD '16), San Francisco, CA, USA, 2016, pp. 785–794.",
    "[4] G. Ke, Q. Meng, T. Finley, T. Wang, W. Chen, W. Ma, Q. Ye, and T.-Y. Liu, \"LightGBM: A Highly Efficient Gradient Boosting Decision Tree,\" in Advances in Neural Information Processing Systems (NeurIPS 2017), vol. 30, pp. 3146–3154, 2017.",
    "[5] L. Breiman, \"Random Forests,\" Machine Learning, vol. 45, no. 1, pp. 5–32, 2001.",
    "[6] S. Makridakis, E. Spiliotis, and V. Assimakopoulos, \"The M5 Accuracy Competition: Results, Findings, and Conclusions,\" Int. J. Forecast., vol. 38, no. 4, pp. 1346–1364, 2022.",
    "[7] R. J. Hyndman and G. Athanasopoulos, Forecasting: Principles and Practice, 3rd ed. Melbourne, Australia: OTexts, 2021.",
    "[8] G. E. P. Box, G. M. Jenkins, G. C. Reinsel, and G. M. Ljung, Time Series Analysis: Forecasting and Control, 5th ed. Hoboken, NJ, USA: John Wiley & Sons, 2015.",
    "[9] D. K. Barrow and N. Kourentzes, \"Distributions of Forecasting Errors of Forecast Combinations: Implications for Inventory Management,\" Int. J. Prod. Econ., vol. 177, pp. 24–33, 2016.",
    "[10] R. Fildes, S. Ma, and S. Kolassa, \"Retail Forecasting: Research and Practice,\" Int. J. Forecast., vol. 38, no. 4, pp. 1283–1318, 2022.",
    "[11] A. E. Hoerl and R. W. Kennard, \"Ridge Regression: Biased Estimation for Nonorthogonal Problems,\" Technometrics, vol. 12, no. 1, pp. 55–67, 1970.",
    "[12] S. Chopra and P. Meindl, Supply Chain Management: Strategy, Planning, and Operation, 7th ed. Boston, MA, USA: Pearson, 2019."
]

for ref in refs:
    p_r = doc.add_paragraph()
    set_p(p_r, WD_ALIGN_PARAGRAPH.JUSTIFY, sb=3, sa=3)
    r = p_r.add_run(ref)
    r.font.name = 'Times New Roman'
    r.font.size = Pt(10.5)

# Save Word files
doc_name_full = "24070521505_Dev_Dilip_Dhapodkar.docx"
doc_name_short = "24070521505_Dev_Dhapodkar.docx"
doc.save(doc_name_full)
shutil.copyfile(doc_name_full, doc_name_short)
shutil.copyfile(doc_name_full, "Walmart_Sales_Forecasting_Report.docx")
print(f"Saved Word documents: {doc_name_full} and {doc_name_short}")

# Count words
total_w = sum(len(p.text.split()) for p in doc.paragraphs)
for t in doc.tables:
    for row in t.rows:
        for cell in row.cells:
            total_w += sum(len(p.text.split()) for p in cell.paragraphs)
print(f"Total word count in 6-page docx: {total_w}")

# ==============================================================================
# 2. BUILD EXACT 6-PAGE PDF VIA REPORTLAB
# ==============================================================================
pdf_name_full = "24070521505_Dev_Dilip_Dhapodkar.pdf"
pdf_name_short = "24070521505_Dev_Dhapodkar.pdf"

pdf_doc = SimpleDocTemplate(
    pdf_name_full,
    pagesize=A4,
    leftMargin=0.75 * inch,
    rightMargin=0.75 * inch,
    topMargin=0.65 * inch,
    bottomMargin=0.65 * inch
)

styles = getSampleStyleSheet()

p_title_style = ParagraphStyle('T1', fontName='Times-Bold', fontSize=14.5, leading=18.5, textColor=colors.HexColor('#0F2942'), alignment=TA_CENTER, spaceBefore=4, spaceAfter=2)
p_sub_style = ParagraphStyle('T2', fontName='Times-Bold', fontSize=11, leading=14, textColor=colors.HexColor('#0071CE'), alignment=TA_CENTER, spaceBefore=2, spaceAfter=2)
p_meta_style = ParagraphStyle('T3', fontName='Times-Roman', fontSize=9.5, leading=12.5, textColor=colors.HexColor('#475569'), alignment=TA_CENTER, spaceBefore=2, spaceAfter=6)

p_h1_style = ParagraphStyle('H1', fontName='Times-Bold', fontSize=13, leading=16.5, textColor=colors.HexColor('#0F2942'), spaceBefore=8, spaceAfter=3)
p_body_style = ParagraphStyle('B1', fontName='Times-Roman', fontSize=10, leading=13.6, textColor=colors.HexColor('#111827'), alignment=TA_JUSTIFY, spaceBefore=4, spaceAfter=4)
p_tcap_style = ParagraphStyle('TC', fontName='Times-Bold', fontSize=9, leading=11.5, textColor=colors.HexColor('#0F2942'), spaceBefore=5, spaceAfter=2)
p_fcap_style = ParagraphStyle('FC', fontName='Times-Italic', fontSize=8.5, leading=11, textColor=colors.HexColor('#475569'), alignment=TA_CENTER, spaceBefore=2, spaceAfter=5)
p_th_style = ParagraphStyle('TH', fontName='Times-Bold', fontSize=8, leading=10, textColor=colors.white, alignment=TA_CENTER)
p_td_style = ParagraphStyle('TD', fontName='Times-Roman', fontSize=7.6, leading=9.8, textColor=colors.HexColor('#1E293B'))
p_eq_style = ParagraphStyle('EQ', fontName='Times-Italic', fontSize=9.5, leading=12, textColor=colors.HexColor('#0F2942'), alignment=TA_CENTER)
p_eqn_style = ParagraphStyle('EQN', fontName='Times-Bold', fontSize=9.5, leading=12, textColor=colors.HexColor('#0F2942'), alignment=TA_RIGHT)

def rl_tbl(rows, widths):
    w = []
    for i, r in enumerate(rows):
        cells = [Paragraph(str(c), p_th_style if i == 0 else p_td_style) for c in r]
        w.append(cells)
    t = Table(w, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F2942')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
    ]))
    return t

def rl_eq(formula, num):
    t = Table([[Paragraph(formula, p_eq_style), Paragraph(f"({num})", p_eqn_style)]], colWidths=[5.9 * inch, 0.85 * inch])
    t.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('TOPPADDING', (0,0), (-1,-1), 1.5), ('BOTTOMPADDING', (0,0), (-1,-1), 1.5)]))
    return t

story = []

# PAGE 1: Header + Chapter 1
story.append(Paragraph("PREDICTIVE ANALYTICS — CONTINUOUS ASSESSMENT 3 (CA3)", p_sub_style))
story.append(Paragraph("Sales Forecasting: End-to-End Predictive Analytics Model Development and Supply Chain Inventory Optimization Using the KDD Process", p_title_style))
story.append(Paragraph("<b>Submitted By:</b> Dev Dilip Dhapodkar &nbsp;&nbsp;|&nbsp;&nbsp; <b>PRN:</b> 24070521505 &nbsp;&nbsp;|&nbsp;&nbsp; <b>Symbiosis International University</b>", p_meta_style))

story.append(Paragraph("Chapter 1: Introduction", p_h1_style))
story.append(Paragraph("<b>1.1 Context and Problem Domain:</b> In large-scale retail commerce, accurate sales forecasting constitutes the operational foundation of multi-echelon supply chain coordination. Retail enterprises such as Walmart manage complex fulfillment networks encompassing thousands of store-department intersections across heterogeneous geographical markets. Each store location is subject to long-term macroeconomic trends, localized disposable income variations, ambient weather conditions, multi-channel promotional markdowns, and abrupt calendar holiday surges. Conventional replenishment models relying on historical moving averages or unadjusted exponential smoothing repeatedly fail to handle these multi-frequency patterns. Inaccurate forecasts create two severe operational risks: catastrophic out-of-stock (OOS) conditions during high-volume holiday periods that permanently erode market share and customer goodwill, and excessive inventory accumulation during routine trading cycles that inflates holding overhead and triggers forced margin-dilutive post-holiday clearance markdowns.", p_body_style))
story.append(Paragraph("<b>1.2 Research Objectives and Scope:</b> This investigation develops, validates, and interprets an end-to-end predictive analytics regression pipeline that forecasts weekly department-level sales across multiple retail stores using historical transaction records, promotional price markdown schedules, holiday calendars, and macroeconomic indicators. Implemented on the benchmark Kaggle Walmart Recruiting dataset, the analytical framework adheres strictly to the formal Knowledge Discovery in Databases (KDD) process. Specifically, the model forecasts weekly revenue across 45 physical stores and 81 departments across three distinct retail formats: Type A Supercenters, Type B Discount Stores, and Type C Neighborhood Markets.", p_body_style))
story.append(Paragraph("<b>1.3 Asymmetric Supply Chain Cost Structure:</b> In retail supply chains, forecast error costs exhibit acute operational asymmetry. During routine mid-year weeks, moderate prediction errors can be absorbed through standard safety stock buffers and scheduled replenishment. Conversely, during major retail holidays such as Thanksgiving (Black Friday) and the pre-Christmas shopping peak, consumer foot traffic spikes by 40% to 50%, lead times from regional distribution centers are saturated, and stockouts cannot be alleviated through emergency deliveries. To formalize this business reality, the evaluation protocol employs the official Weighted Mean Absolute Error (WMAE) metric, which assigns a five-fold penalty (w = 5) to holiday weeks relative to regular baseline weeks (w = 1). The predictive system developed herein is explicitly calibrated to optimize this asymmetric cost surface.", p_body_style))
story.append(PageBreak()) # End of Page 1

# PAGE 2: Chapter 2: Literature Review
story.append(Paragraph("Chapter 2: Literature Review", p_h1_style))
story.append(Paragraph("<b>2.1 Classical Econometric Formulations:</b> Retail demand forecasting methodologies have evolved substantially over the past two decades. Early parametric approaches relied on univariate statistical formulations, primarily Autoregressive Integrated Moving Average (ARIMA), Seasonal ARIMA (SARIMA), and Holt-Winters Exponential Smoothing state-space models. While effective for isolated stationary series, univariate parametric models require fitting and maintaining thousands of independent local models across every store-department pair and struggle to incorporate high-dimensional exogenous drivers—such as multi-channel promotional markdowns and regional economic indices—without parameter instability.", p_body_style))
story.append(Paragraph("<b>2.2 Global Gradient-Boosted Decision Trees:</b> To overcome these limitations, modern predictive analytics utilizes global machine learning architectures that pool observations across all store and department hierarchies into a unified tabular feature space. Breiman's Random Forest established the power of bootstrap aggregation to reduce predictive variance and model non-linear interactions. More recently, extreme gradient boosting architectures—notably XGBoost (Chen and Guestrin) and LightGBM (Ke et al.)—have become the premier standard in retail analytics. These architectures leverage second-order Taylor approximations, tree regularization penalties, and histogram-based binning. The M5 Forecasting Competition (Makridakis et al.) conclusively proved that global tree ensembles enriched with multi-horizon autoregressive lags and shifted rolling statistics outperform classical models and deep recurrent networks on promotional retail demand series.", p_body_style))

story.append(Paragraph("Table 1: Synthesis of Relevant Prior Literature in Predictive Retail Analytics and Machine Learning", p_tcap_style))
story.append(rl_tbl([lit_headers] + lit_data, [1.35 * inch, 1.45 * inch, 1.35 * inch, 2.6 * inch]))
story.append(Spacer(1, 3))
story.append(Paragraph("<b>2.3 Research Gap Addressed:</b> Existing empirical implementations often suffer from two methodological weaknesses: inadvertent look-ahead leakage in rolling window statistics, and model optimization against symmetric metrics that ignore the 5x stockout penalty of holiday peaks. This study addresses both issues through leak-free feature engineering and sample-weighted optimization.", p_body_style))
story.append(PageBreak()) # End of Page 2

# PAGE 3: Chapter 3: Workflow Stages 1 & 2
story.append(Paragraph("Chapter 3: Workflow / Predictive Modelling Process", p_h1_style))
story.append(Paragraph("<b>3.1 The KDD Methodological Architecture:</b> The analytical workflow operationalizes the classical Knowledge Discovery in Databases (KDD) process through seven structured phases: Data Selection, Preprocessing, Feature Engineering, Exploratory Data Analysis, Model Training, Evaluation, and Supply Chain Interpretation.", p_body_style))
story.append(Paragraph("<b>3.2 Stage 1: Data Selection and Relational Ingestion:</b> The dataset integrates four relational files from the Walmart Recruiting repository: historical department transactions (train.csv), environmental and economic attributes (features.csv), store metadata (stores.csv), and holdout structures (test.csv). Merged on [Store, Date, IsHoliday] and [Store], the analytical training matrix contains 421,570 records spanning 143 consecutive weeks (February 2010 to October 2012) across 45 stores and 81 departments.", p_body_style))

story.append(Paragraph("Table 2: Relational Database Schema and Ingestion Properties of the Walmart Corpus", p_tcap_style))
story.append(rl_tbl([tab2_headers] + tab2_data, [1.0 * inch, 0.9 * inch, 0.9 * inch, 1.3 * inch, 2.65 * inch]))
story.append(Spacer(1, 3))

story.append(Paragraph("<b>3.3 Stage 2: Data Preprocessing, Imputation and Outlier Treatment:</b> Data diagnostics identified three primary anomalies: promotional markdown missingness, macroeconomic indicator lags, and accounting merchandise returns manifesting as negative sales values.", p_body_style))

story.append(Paragraph("Table 3: Comprehensive Diagnostic Profile of Missing Values, Anomalies, and Imputation Protocols", p_tcap_style))
story.append(rl_tbl([tab3_headers] + tab3_data, [1.3 * inch, 0.95 * inch, 0.9 * inch, 1.7 * inch, 1.9 * inch]))
story.append(Spacer(1, 3))
story.append(Paragraph("Promotional markdowns (MarkDown1–5) were structurally zero-imputed after extracting binary activity indicators (Has_MarkDown). Negative accounting return values were floored at zero, and non-holiday outliers were capped at the 99.95th percentile ($183.5K) while strictly preserving authentic holiday spikes.", p_body_style))
story.append(PageBreak()) # End of Page 3

# PAGE 4: Chapter 3: Feature Engineering & Model Formulations
story.append(Paragraph("<b>3.4 Stage 3: Multi-Scale Feature Engineering Pipeline:</b> To equip regression models with rich temporal signals without look-ahead bias, 43 domain predictors were constructed across five classes: (1) Autoregressive Lags (Lag_1, Lag_2, Lag_4, Lag_52); (2) Leak-Free Shifted Rolling Windows computed on t-1 shifted demand (Rolling_Mean_4, Rolling_Std_4, Rolling_Mean_12, Momentum_1_4); (3) Explicit Holiday Calendar Indicators (Is_SuperBowl, Is_LaborDay, Is_Thanksgiving, Is_Christmas, Pre_Christmas_Peak); (4) Fourier Cyclical Seasonality Transforms enforcing circular calendar continuity; and (5) Out-of-Sample Historical Target Statistics (Store_Dept_Mean, Store_Dept_Median, Store_Dept_Std computed strictly on the training partition).", p_body_style))

story.append(rl_eq("Week_Sin = sin(2pi * Week / 52),    Week_Cos = cos(2pi * Week / 52)", "1"))
story.append(Spacer(1, 3))

story.append(Paragraph("<b>3.5 Stage 5 & 6: Predictive Model Formulation and Evaluation Metric:</b> Four distinct model families were benchmarked: Baseline Ridge Regression optimizing L2-regularized squared loss (Equation 2), Random Forest Regressor averaging B = 100 decorrelated trees (Equation 3), and XGBoost and LightGBM optimizing second-order regularized gradient boosting (Equation 4). Models were evaluated under asymmetric Weighted Mean Absolute Error (Equation 5) and inventory mismatch penalty cost (Equation 6) over a chronological split at November 25, 2011 (263,199 train / 145,237 validation records covering 49 weeks and all 4 holidays).", p_body_style))

story.append(rl_eq("min_beta { ||y - X beta||_2^2 + alpha ||beta||_2^2 },    alpha = 100.0", "2"))
story.append(rl_eq("y_hat_RF(x) = (1 / B) * Sum_{b=1}^{B} T_b(x)", "3"))
story.append(rl_eq("L^(t) approx Sum_{i=1}^{N} w_i [ g_i f_t(x_i) + (1/2) h_i f_t^2(x_i) ] + Omega(f_t)", "4"))
story.append(rl_eq("WMAE = [ Sum_{i=1}^{N} w_i * |y_i - y_hat_i| ] / [ Sum_{i=1}^{N} w_i ],    w_i = 5 if IsHoliday_i else 1", "5"))
story.append(rl_eq("C_mismatch = gamma * Sum_{i=1}^{N} |y_i - y_hat_i|,    gamma = 0.22", "6"))
story.append(Spacer(1, 3))

story.append(Paragraph("<b>3.6 Chronological Validation Design:</b> Partitioning the dataset at November 25, 2011 guarantees that the model is evaluated on a full 49-week forward horizon encompassing Thanksgiving, Christmas, Super Bowl, and Labor Day, testing out-of-sample holiday generalization without leakage.", p_body_style))
story.append(PageBreak()) # End of Page 4

# PAGE 5: Chapter 4: Results & Discussion
story.append(Paragraph("Chapter 4: Results and Discussion", p_h1_style))
story.append(Paragraph("<b>4.1 Exploratory Data Analysis & Benchmark Evaluation:</b> Average weekly sales across all 45 stores fluctuate near $47.1M during baseline periods, but spike to $66.6M on Thanksgiving (+44.0% lift) and $80.0M during Pre-Christmas Weeks 49–51 (+40.2% lift). Physical store area exhibits a strong linear correlation (r = 0.81) with sales across Supercenters ($1.45M/wk), Discount Stores ($0.79M/wk), and Neighborhood Markets ($0.46M/wk).", p_body_style))

story.append(KeepTogether([
    RLImage("figures/fig1_eda_sales_overview.png", width=6.2 * inch, height=2.45 * inch, kind='proportional'),
    Paragraph("Figure 1: Aggregate Weekly Retail Sales Trajectory (2010–2012), Format Type Distribution, and Store Area Size Elasticity.", p_fcap_style)
]))

story.append(Paragraph("Table 4: Comprehensive Model Evaluation Across 145,237 Out-of-Sample Store-Department-Week Validation Observations", p_tcap_style))
story.append(rl_tbl([tab4_headers] + tab4_data, [1.6 * inch, 0.85 * inch, 0.85 * inch, 0.8 * inch, 0.65 * inch, 1.0 * inch, 1.0 * inch, 0.55 * inch]))
story.append(Spacer(1, 3))

story.append(Paragraph("<b>4.2 Quantitative Findings:</b> LightGBM achieved the best overall performance with WMAE = $1,758.94 (a 60.0% error reduction vs. Baseline Ridge at $4,393.17), lowest RMSE ($3,837.62), and R² = 0.9725 in 4.91 seconds. Crucially, LightGBM slashed Holiday MAE by 76.0% ($2,421.19 vs. $10,108.52), protecting against peak stockouts. XGBoost achieved the lowest regular-week MAE ($1,410.37).", p_body_style))

story.append(KeepTogether([
    RLImage("figures/fig6_actual_vs_predicted.png", width=6.2 * inch, height=2.3 * inch, kind='proportional'),
    Paragraph("Figure 2: Chronological Validation Set Forecast Tracking (Nov 2011 – Oct 2012) and Actual versus Predicted 45-Degree Parity Scatter.", p_fcap_style)
]))
story.append(PageBreak()) # End of Page 5

# PAGE 6: Feature Importance, Supply Chain Impact, Conclusion & References
story.append(Paragraph("Table 5: Feature Importance Hierarchy Across Tree Ensembles Derived via Normalized Split Gain Attribution", p_tcap_style))
story.append(rl_tbl([tab5_headers] + tab5_data, [0.5 * inch, 1.35 * inch, 2.3 * inch, 0.9 * inch, 0.9 * inch, 0.8 * inch]))
story.append(Spacer(1, 2))

story.append(Paragraph("<b>4.3 Feature Gain & Supply Chain Impact:</b> Gain attribution confirms annual seasonality (Lag_52) is the #1 driver (40.87% in LightGBM, 31.45% in XGBoost), followed by 4-week rolling momentum (17%–25%) and Thanksgiving flags (2.3%–4.4%). Under Equation 6 (gamma = 0.22), deploying LightGBM cuts network mismatch costs from $80.3M to $48.6M—saving $31.7M (-39.5%) across all 45 stores ($17.1M saved in Supercenters, $12.8M in Discount Stores, $1.8M in Neighborhood Markets).", p_body_style))

story.append(KeepTogether([
    RLImage("figures/fig8_supply_chain_impact.png", width=6.2 * inch, height=2.0 * inch, kind='proportional'),
    Paragraph("Figure 3: Error Breakdown on Holiday vs. Regular Weeks and Supply Chain Mismatch Cost Savings Across Store Formats.", p_fcap_style)
]))

story.append(Paragraph("Chapter 5: Conclusion", p_h1_style))
story.append(Paragraph("<b>5.1 Summary & Recommendations:</b> This study demonstrated the efficacy of the KDD pipeline for multi-store retail forecasting, achieving R² = 0.9725 and reducing WMAE by 60.0% ($1,758.94 vs. $4,393.17). We recommend a dual-regime deployment policy: LightGBM for Q4 holiday safety stock allocation and XGBoost for routine replenishment, pre-staging inventory 3 to 4 weeks prior to Thanksgiving and Christmas promotional spikes. Future work will explore Conformal Prediction intervals and Temporal Fusion Transformers.", p_body_style))

story.append(Paragraph("Chapter 6: References", p_h1_style))
for ref in refs:
    story.append(Paragraph(ref, ParagraphStyle('R1', fontName='Times-Roman', fontSize=7.8, leading=10.2, textColor=colors.HexColor('#1E293B'), alignment=TA_JUSTIFY, spaceBefore=1.5, spaceAfter=1.5)))

def add_pdf_footer(canvas, d):
    canvas.saveState()
    canvas.setFont('Times-Roman', 9)
    canvas.setFillColor(colors.HexColor('#64748B'))
    canvas.drawString(0.75 * inch, 0.45 * inch, "Dev Dilip Dhapodkar (PRN: 24070521505) — Predictive Analytics CA3 Project Report")
    canvas.drawRightString(A4[0] - 0.75 * inch, 0.45 * inch, f"Page {d.page} of 6")
    canvas.restoreState()

pdf_doc.build(story, onFirstPage=add_pdf_footer, onLaterPages=add_pdf_footer)
shutil.copyfile(pdf_name_full, pdf_name_short)
shutil.copyfile(pdf_name_full, "Walmart_Sales_Forecasting_Report.pdf")

reader = pypdf.PdfReader(pdf_name_full)
print(f"Verified PDF page count: {len(reader.pages)} pages!")
for i, page in enumerate(reader.pages):
    print(f"Page {i+1} character count: {len(page.extract_text())}")
