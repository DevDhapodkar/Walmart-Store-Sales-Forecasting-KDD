import os
import json
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image as RLImage,
    Table, TableStyle, PageBreak, KeepTogether
)

pdf_filename = "24070521505_Dev_Dilip_Dhapodkar.pdf"

pdf_doc = SimpleDocTemplate(
    pdf_filename,
    pagesize=A4,
    leftMargin=0.75 * inch,
    rightMargin=0.75 * inch,
    topMargin=0.85 * inch,
    bottomMargin=0.85 * inch
)

styles = getSampleStyleSheet()

# Strict formatting styles matching guidelines: Times-Roman, 12pt body, Justified, 6pt before-after
st_main_title = ParagraphStyle(
    'MainTitle',
    fontName='Times-Bold',
    fontSize=16,
    leading=21,
    textColor=colors.HexColor('#0F2942'),
    alignment=TA_CENTER,
    spaceBefore=6,
    spaceAfter=4
)

st_sub_title = ParagraphStyle(
    'SubTitle',
    fontName='Times-Bold',
    fontSize=12,
    leading=16,
    textColor=colors.HexColor('#0071CE'),
    alignment=TA_CENTER,
    spaceBefore=4,
    spaceAfter=4
)

st_meta = ParagraphStyle(
    'MetaBlock',
    fontName='Times-Roman',
    fontSize=10.5,
    leading=14,
    textColor=colors.HexColor('#475569'),
    alignment=TA_CENTER,
    spaceBefore=4,
    spaceAfter=12
)

st_h1 = ParagraphStyle(
    'Heading1',
    fontName='Times-Bold',
    fontSize=14.5,
    leading=19,
    textColor=colors.HexColor('#0F2942'),
    alignment=TA_LEFT,
    spaceBefore=14,
    spaceAfter=6
)

st_h2 = ParagraphStyle(
    'Heading2',
    fontName='Times-Bold',
    fontSize=12.5,
    leading=17,
    textColor=colors.HexColor('#0071CE'),
    alignment=TA_LEFT,
    spaceBefore=10,
    spaceAfter=5
)

st_body = ParagraphStyle(
    'BodyJustified',
    fontName='Times-Roman',
    fontSize=11.5,
    leading=16,
    textColor=colors.HexColor('#111827'),
    alignment=TA_JUSTIFY,
    spaceBefore=6,
    spaceAfter=6
)

st_tbl_cap = ParagraphStyle(
    'TableCaption',
    fontName='Times-Bold',
    fontSize=10.5,
    leading=14,
    textColor=colors.HexColor('#0F2942'),
    alignment=TA_LEFT,
    spaceBefore=8,
    spaceAfter=4
)

st_fig_cap = ParagraphStyle(
    'FigureCaption',
    fontName='Times-Italic',
    fontSize=10,
    leading=13.5,
    textColor=colors.HexColor('#475569'),
    alignment=TA_CENTER,
    spaceBefore=4,
    spaceAfter=8
)

st_th = ParagraphStyle(
    'TableHdr',
    fontName='Times-Bold',
    fontSize=9,
    leading=12,
    textColor=colors.white,
    alignment=TA_CENTER
)

st_td = ParagraphStyle(
    'TableCell',
    fontName='Times-Roman',
    fontSize=8.5,
    leading=11.5,
    textColor=colors.HexColor('#1E293B'),
    alignment=TA_LEFT
)

st_eq = ParagraphStyle(
    'EquationText',
    fontName='Times-Italic',
    fontSize=11,
    leading=14,
    textColor=colors.HexColor('#0F2942'),
    alignment=TA_CENTER
)

st_eq_num = ParagraphStyle(
    'EquationNum',
    fontName='Times-Bold',
    fontSize=11,
    leading=14,
    textColor=colors.HexColor('#0F2942'),
    alignment=TA_RIGHT
)

def make_rl_table(data_rows, col_widths):
    wrapped = []
    for i, r in enumerate(data_rows):
        row_cells = []
        for c in r:
            row_cells.append(Paragraph(str(c), st_th if i == 0 else st_td))
        wrapped.append(row_cells)
    t = Table(wrapped, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F2942')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    return t

def make_equation(eq_str, num_str):
    tbl = Table(
        [[Paragraph(eq_str, st_eq), Paragraph(f"({num_str})", st_eq_num)]],
        colWidths=[5.9 * inch, 0.85 * inch]
    )
    tbl.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    return tbl

story = []

# FIRST PAGE: EXACT PROFESSOR NOTIFICATION COVER PAGE
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
story.append(Spacer(1, 4))

# Chapter 1: Introduction
story.append(Paragraph("Chapter 1: Introduction", st_h1))
story.append(Paragraph("<b>1.1 Context and Problem Domain:</b> In large-scale retail commerce, accurate sales forecasting represents the cornerstone of effective multi-echelon supply chain management. Modern big-box retail operations, exemplified by multinational supermarket networks such as Walmart, encompass thousands of store-department intersections operating across heterogeneous geographical catchments. Each individual retail unit is simultaneously buffeted by long-term macroeconomic fluctuations, local purchasing power variations, weather perturbations, high-velocity promotional markdown events, and extreme calendar-driven holiday surges. Traditional inventory replenishment policies that rely on simple historical moving averages or localized univariate projections frequently exhibit catastrophic forecast mismatch. These planning failures precipitate two mutually destructive operational regimes: costly stockouts during high-velocity holiday peaks, which irreversibly erode revenue and consumer brand loyalty, and severe overstocking during regular replenishment cycles, which inflates working capital lock-up, warehouse handling overhead, and subsequent gross margin erosion through forced post-holiday clearance markdowns.", st_body))

story.append(Paragraph("<b>1.2 Research Objective and Scope:</b> The primary objective of this project is to develop, validate, and interpret an end-to-end predictive analytics regression pipeline that forecasts weekly department-level sales across multiple retail stores using historical sales transactions, promotional price markdown schedules, calendar holiday schedules, and regional macroeconomic indicators. Formulated as a multi-store hierarchical forecasting problem on the benchmark Kaggle Walmart Recruiting dataset, the analytical framework follows the rigorous Knowledge Discovery in Databases (KDD) process. Specifically, the model forecasts weekly revenue across 45 physical Walmart stores and 81 specialized departments spanning three distinct store format architectures (Type A Supercenters, Type B Discount Stores, and Type C Neighborhood Markets).", st_body))

story.append(Paragraph("<b>1.3 Asymmetric Supply Chain Cost Structure:</b> A fundamental characteristic of retail demand forecasting lies in the acute operational asymmetry of prediction error costs. In standard regression formulations, errors are evaluated using uniform symmetric penalties such as Ordinary Least Squares Mean Squared Error (MSE) or Mean Absolute Error (MAE). In practical supply chain operations, however, an under-forecast during a peak retail holiday such as Thanksgiving (Black Friday) or the pre-Christmas shopping week is drastically more damaging than an equivalent magnitude error during a routine non-holiday week in February. During major holiday events, consumer foot traffic peaks by upwards of 40% to 50%, supply chain lead times from distribution centers are saturated, and stockouts cannot be mitigated via emergency freight. Consequently, the operational loss function must heavily penalize holiday forecast discrepancies. This business reality is formalized via the official Kaggle Weighted Mean Absolute Error (WMAE) metric, which explicitly assigns a 5x weighting factor (w = 5) to holiday observation weeks relative to baseline weeks (w = 1). The predictive system developed herein is explicitly calibrated to optimize this asymmetric cost surface.", st_body))

# Chapter 2: Literature Review
story.append(Paragraph("Chapter 2: Literature Review", st_h1))
story.append(Paragraph("<b>2.1 Classical Econometric and Parametric Formulations:</b> The academic and industrial literature surrounding retail demand forecasting has undergone a profound paradigm shift over the past two decades. Early econometric approaches relied almost exclusively on univariate statistical formulations, most notably the classical Autoregressive Integrated Moving Average (ARIMA) and Seasonal ARIMA (SARIMA) models popularized by Box and Jenkins, alongside Holt-Winters Exponential Smoothing state-space models. While mathematically tractable and capable of capturing stationary autocorrelative cycles, univariate parametric formulations exhibit severe structural limitations in modern retail environments. First, they require the fitting and ongoing maintenance of thousands of independent local models across every individual store-department time series. Second, and more critically, univariate models possess limited capacity to ingest high-dimensional, cross-sectional exogenous features—such as simultaneous multi-channel promotional markdowns, regional fuel prices, and macroeconomic consumer indices—without suffering severe parameter instability and degrees-of-freedom depletion.", st_body))

story.append(Paragraph("<b>2.2 Global Machine Learning and Gradient Boosted Tree Ensembles:</b> To overcome the limitations of localized univariate modeling, contemporary predictive analytics leverages global machine learning architectures that pool cross-sectional observations across all store and department hierarchies into a unified high-capacity tabular space. Foundational work by Breiman on Random Forests established the efficacy of bagging randomized decision trees to suppress prediction variance and accommodate complex non-linear feature interactions without overfitting. Subsequently, the advent of extreme gradient boosting architectures—most prominently XGBoost introduced by Chen and Guestrin, and LightGBM developed by Ke et al.—revolutionized retail forecasting. These tree-based ensembles utilize second-order Taylor expansions of the objective loss function, incorporate L1/L2 leaf weight regularization, and histogram-based continuous feature binning. Landmark industrial competitions, notably the M5 Forecasting Accuracy Competition analyzed by Makridakis et al., decisively demonstrated that global gradient-boosted decision trees enriched with multi-horizon lag structures and shifted rolling statistical aggregations consistently outperform both classical statistical methods and deep recurrent neural networks on intermittent, highly promotional retail demand series.", st_body))

# Table 1 (Caption Above Table)
lit_headers = ["Author(s) & Year", "Methodology / Architecture", "Dataset / Domain", "Key Strengths & Identified Limitations"]
lit_data = [
    ["Box & Jenkins (2015); Hyndman (2021)", "ARIMA, SARIMAX & ETS State-Space", "Univariate Retail Series", "Strong linear autocorrelation capture; poor handling of non-linear promotional spikes and cross-store data pooling."],
    ["Breiman (2001)", "Random Forest Regressor (Bagging Ensemble)", "Tabular Machine Learning", "Robust to noisy outliers and non-linear interactions; high computational memory overhead and slower inference."],
    ["Chen & Guestrin (2016)", "XGBoost (Regularized Gradient Boosting)", "High-Dimensional Benchmarks", "Second-order Taylor optimization with L1/L2 leaf penalties; excellent handling of sparse features; depth-wise tree growth."],
    ["Ke et al. (2017)", "LightGBM (Leaf-Wise Histogram Boosting)", "Multi-Store Retail Benchmarks", "Leaf-wise best-first tree growth with histogram binning; >80% reduction in training latency with superior convergence on skewed targets."],
    ["Makridakis et al. (2022)", "M5 Forecasting Competition (Tree Ensembles)", "Walmart Hierarchical (42,840 series)", "Demonstrated that global GBDT ensembles with lag and rolling features decisively surpass classical and deep neural architectures."],
    ["Barrow & Kourentzes (2016)", "Safety Stock Optimization under Asymmetric Loss", "Supply Chain Operations", "Confirmed that targeted reduction in peak-period forecast variance yields disproportionate reductions in buffer stockholding costs."]
]
story.append(Paragraph("Table 1: Synthesis of Relevant Prior Literature in Predictive Retail Analytics and Machine Learning", st_tbl_cap))
story.append(make_rl_table(lit_data, [1.4 * inch, 1.5 * inch, 1.4 * inch, 2.45 * inch]))
story.append(Spacer(1, 4))

story.append(Paragraph("<b>2.3 Research Gap and Methodological Contribution:</b> Despite the extensive literature on gradient-boosted decision trees in retail, existing empirical implementations frequently suffer from two persistent methodological flaws. First, many published studies compute rolling statistical features across the entire chronological horizon without enforcing a strict t-1 backward shift, thereby inadvertently leaking current-period target variance into historical rolling aggregations. Second, standard models are commonly optimized against symmetric unweighted metrics (such as unweighted RMSE or MAE), ignoring the asymmetric 5x financial penalty of holiday stockout events. This study bridges this gap by engineering a leak-free feature pipeline, enforcing sample-weighted holiday optimization, and directly translating statistical error reductions into dollarized inventory holding and stockout cost mitigation.", st_body))

# Chapter 3: Workflow / Predictive Modelling Process
story.append(Paragraph("Chapter 3: Workflow / Predictive Modelling Process", st_h1))
story.append(Paragraph("<b>3.1 The KDD Methodological Architecture:</b> To ensure methodological rigor, reproducibility, and end-to-end traceability, this project operationalizes the classical Knowledge Discovery in Databases (KDD) framework originally formulated by Fayyad et al. The predictive modeling workflow proceeds through seven sequential and interdependent phases: (1) Relational Data Selection and Ingestion, (2) Target-Aligned Data Preprocessing and Outlier Treatment, (3) Multi-Scale Feature Engineering, (4) Exploratory Data Analysis (EDA), (5) Multi-Model Architecture Training, (6) Comprehensive Out-of-Sample Performance Evaluation under Asymmetric WMAE, and (7) Feature Gain Attribution and Supply Chain Business Interpretation.", st_body))

story.append(Paragraph("<b>3.2 Stage 1: Data Selection and Relational Ingestion:</b> The analytical dataset was sourced from the benchmark Walmart Recruiting — Store Sales Forecasting repository. The schema comprises four relational tables that were merged into a unified analytical matrix. Historical weekly sales records (train.csv) were merged with exogenous environmental and economic attributes (features.csv) on the composite primary key [Store, Date, IsHoliday], and subsequently merged with structural store metadata (stores.csv) on [Store]. The resulting merged training matrix comprises exactly 421,570 unique store-department-week observations spanning 143 consecutive weeks from February 5, 2010 to October 26, 2012. Table 2 details the structural properties and granularity of each constituent table.", st_body))

# Table 2 (Caption Above Table)
tab2_headers = ["File Name", "Record Count", "Attribute Count", "Primary Granularity", "Attribute Schema & Operational Role"]
tab2_data = [
    ["stores.csv", "45", "3", "Store (1–45)", "Store metadata: Store format Type (A: 22 Supercenters, B: 17 Discount Stores, C: 6 Neighborhood Markets) and physical Size (34,875 to 219,622 sq. ft.)."],
    ["features.csv", "8,190", "12", "(Store, Date)", "Contextual attributes: Temperature, Fuel_Price, MarkDown1–MarkDown5 promotional channels, CPI, Unemployment, and IsHoliday."],
    ["train.csv", "421,570", "5", "(Store, Dept, Date)", "Historical weekly sales: Weekly_Sales ($ USD) across 45 stores and 81 departments over 143 historical weeks."],
    ["test.csv", "115,064", "4", "(Store, Dept, Date)", "Future evaluation horizon spanning 39 weeks (November 2, 2012 to July 26, 2013) for out-of-sample deployment."]
]
story.append(Paragraph("Table 2: Relational Database Schema and Ingestion Properties of the Walmart Forecasting Corpus", st_tbl_cap))
story.append(make_rl_table(tab2_data, [1.05 * inch, 0.95 * inch, 0.95 * inch, 1.35 * inch, 2.45 * inch]))
story.append(Spacer(1, 4))

story.append(Paragraph("<b>3.3 Stage 2: Data Preprocessing, Imputation and Outlier Treatment:</b> A systematic diagnostic of the raw ingested dataset revealed three critical data quality anomalies requiring domain-informed preprocessing: promotional markdown missingness, macroeconomic temporal gaps, and accounting returns manifesting as negative sales values.", st_body))

# Table 3 (Caption Above Table)
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
story.append(Paragraph("Table 3: Comprehensive Diagnostic Profile of Missing Values, Anomalies, and Imputation Protocols", st_tbl_cap))
story.append(make_rl_table(tab3_data, [1.3 * inch, 1.05 * inch, 0.9 * inch, 1.65 * inch, 1.85 * inch]))
story.append(Spacer(1, 4))

story.append(Paragraph("<b>3.4 Stage 3: Multi-Scale Feature Engineering Pipeline:</b> To equip tree-based ensembles with multi-scale temporal context without look-ahead bias, 43 domain-specific predictive features were constructed across five structural families: (1) Autoregressive Lags (Lag_1, Lag_2, Lag_4, Lag_52); (2) Shifted Rolling Window Aggregations (Rolling_Mean_4, Rolling_Std_4, Rolling_Mean_12, Momentum_1_4 computed on t-1 shifted demand); (3) Explicit Holiday Calendar Indicators (Is_SuperBowl, Is_LaborDay, Is_Thanksgiving, Is_Christmas, Pre_Christmas_Peak); (4) Fourier Cyclical Seasonality Transforms enforcing circular calendar continuity; and (5) Out-of-Sample Historical Target Statistics (Store_Dept_Mean, Store_Dept_Median, Store_Dept_Std computed strictly on the training partition).", st_body))

# Equation (1)
story.append(make_equation("Week_Sin = sin(2pi * Week / 52),    Week_Cos = cos(2pi * Week / 52)", "1"))
story.append(Spacer(1, 4))

story.append(Paragraph("<b>3.5 Stage 5 & 6: Predictive Model Formulation and Evaluation Metric:</b> Four distinct model families were benchmarked across the dataset:", st_body))
story.append(Paragraph("1. Baseline Ridge Regression: Minimizing the L2-regularized squared error objective:", st_body))
# Equation (2)
story.append(make_equation("min_beta { ||y - X beta||_2^2 + alpha ||beta||_2^2 },    alpha = 100.0", "2"))
story.append(Spacer(1, 3))

story.append(Paragraph("2. Random Forest Regressor: An ensemble of B = 100 decorrelated decision trees constructed via bootstrap aggregation with randomized feature subspaces:", st_body))
# Equation (3)
story.append(make_equation("y_hat_RF(x) = (1 / B) * Sum_{b=1}^{B} T_b(x)", "3"))
story.append(Spacer(1, 3))

story.append(Paragraph("3. XGBoost and LightGBM Regressors: Gradient-boosted decision trees minimizing a second-order Taylor expansion of the weighted regularized objective at iteration t:", st_body))
# Equation (4)
story.append(make_equation("L^(t) approx Sum_{i=1}^{N} w_i [ g_i f_t(x_i) + (1/2) h_i f_t^2(x_i) ] + Omega(f_t)", "4"))
story.append(Spacer(1, 3))

story.append(Paragraph("4. Official Evaluation Metric — Weighted Mean Absolute Error (WMAE): Assigns weight 5 to holiday weeks and weight 1 to regular weeks to penalize peak stockouts:", st_body))
# Equation (5)
story.append(make_equation("WMAE = [ Sum_{i=1}^{N} w_i * |y_i - y_hat_i| ] / [ Sum_{i=1}^{N} w_i ],    w_i = 5 if IsHoliday_i else 1", "5"))
story.append(Spacer(1, 3))

story.append(Paragraph("5. Supply Chain Inventory Mismatch Cost Formulation: Translates forecast errors into total dollarized holding and stockout penalties under cost coefficient gamma = 0.22:", st_body))
# Equation (6)
story.append(make_equation("C_mismatch = gamma * Sum_{i=1}^{N} |y_i - y_hat_i|,    gamma = 0.22", "6"))
story.append(Spacer(1, 4))

# Chapter 4: Results and Discussion
story.append(Paragraph("Chapter 4: Results and Discussion", st_h1))
story.append(Paragraph("<b>4.1 Exploratory Data Analysis Insights:</b> Figure 1 illustrates aggregate weekly retail sales across the 45 Walmart stores from February 2010 to October 2012. Regular sales average $47.1M/week but spike dramatically to $66.6M on Thanksgiving (+44.0% lift) and nearly $80.0M during Pre-Christmas Weeks 49–51 (+40.2% lift). Store size strongly correlates with sales (Pearson r = 0.81) across Supercenters ($1.45M/week), Discount Stores ($0.79M/week), and Neighborhood Markets ($0.46M/week).", st_body))

# Figure 1 (Caption Below Figure)
story.append(KeepTogether([
    RLImage("figures/fig1_eda_sales_overview.png", width=6.6 * inch, height=4.0 * inch, kind='proportional'),
    Paragraph("Figure 1: Aggregate Weekly Retail Sales Trajectory (2010–2012), Format Type Distribution, and Store Area Size Elasticity.", st_fig_cap)
]))
story.append(Spacer(1, 4))

story.append(Paragraph("Figure 2 illustrates the pre-imputation missingness profile across promotional channels (Panel A), the right-skewed sales distribution with outlier fences (Panel B), and promotional markdown depth during holiday weeks (Panel C), where MarkDown3 surges to over $14,000 per store during Thanksgiving.", st_body))

# Figure 2 (Caption Below Figure)
story.append(KeepTogether([
    RLImage("figures/fig2_outlier_and_markdown_analysis.png", width=6.6 * inch, height=2.2 * inch, kind='proportional'),
    Paragraph("Figure 2: Missingness Profile Across Variables, Department Sales Distribution with Outlier Fences, and Promotional Markdown Depth.", st_fig_cap)
]))
story.append(Spacer(1, 4))

story.append(Paragraph("Figure 3 details holiday revenue lift across events alongside macroeconomic indicator trajectories, while Figure 4 presents the Pearson correlation heatmap.", st_body))

# Figures 3 and 4 (Captions Below Figures)
story.append(KeepTogether([
    RLImage("figures/fig3_holiday_and_macro_effects.png", width=6.6 * inch, height=2.3 * inch, kind='proportional'),
    Paragraph("Figure 3: Empirical Weekly Revenue Lift by Holiday Calendar Event and Standardized Trajectories of Macroeconomic Indicators.", st_fig_cap)
]))
story.append(Spacer(1, 4))

story.append(KeepTogether([
    RLImage("figures/fig4_correlation_matrix.png", width=6.0 * inch, height=4.6 * inch, kind='proportional'),
    Paragraph("Figure 4: Pearson Correlation Matrix Across Autoregressive Lags, Rolling Averages, Store Size, and Macroeconomic Attributes.", st_fig_cap)
]))
story.append(Spacer(1, 4))

story.append(Paragraph("<b>4.2 Quantitative Model Benchmark Comparison:</b> Table 4 presents performance metrics evaluated across the 145,237 records of the chronological validation set (November 25, 2011 to October 26, 2012, spanning 49 weeks and all four holiday events).", st_body))

# Table 4 (Caption Above Table)
tab4_headers = ["Model Architecture", "WMAE ($ USD)", "RMSE ($ USD)", "MAE ($ USD)", "R2 Score", "Holiday MAE (w=5)", "Regular MAE (w=1)", "Train Time"]
tab4_data = [
    ["Baseline (Ridge Regression)", "$4,393.17", "$6,616.57", "$2,514.98", "0.9183", "$10,108.52", "$1,835.29", "0.20 s"],
    ["Random Forest Regressor", "$1,791.54", "$4,413.86", "$1,520.75", "0.9637", "$2,615.57", "$1,422.75", "42.88 s"],
    ["XGBoost Regressor", "$1,837.57", "$4,306.19", "$1,523.89", "0.9654", "$2,792.11", "$1,410.37", "6.31 s"],
    ["LightGBM Regressor (Winner)", "$1,758.94", "$3,837.62", "$1,541.31", "0.9725", "$2,421.19", "$1,462.55", "4.91 s"]
]
story.append(Paragraph("Table 4: Comprehensive Model Evaluation Across 145,237 Out-of-Sample Store-Department-Week Validation Observations", st_tbl_cap))
story.append(make_rl_table(tab4_data, [1.6 * inch, 0.85 * inch, 0.85 * inch, 0.8 * inch, 0.65 * inch, 1.05 * inch, 1.05 * inch, 0.55 * inch]))
story.append(Spacer(1, 4))

# Figure 5 (Caption Below Figure)
story.append(KeepTogether([
    RLImage("figures/fig5_model_comparison.png", width=6.6 * inch, height=2.0 * inch, kind='proportional'),
    Paragraph("Figure 5: Comparative Evaluation of Predictive Architectures Across WMAE, RMSE, MAE, and R2 Goodness-of-Fit.", st_fig_cap)
]))
story.append(Spacer(1, 4))

story.append(Paragraph("<b>4.3 Forecast Tracking and Parity Analysis:</b> Figure 6 benchmarks weekly forecast tracking across the 49-week validation horizon. LightGBM and XGBoost track holiday peaks accurately with R2 = 0.9725, whereas Baseline Ridge overshoots severely.", st_body))

# Figure 6 (Caption Below Figure)
story.append(KeepTogether([
    RLImage("figures/fig6_actual_vs_predicted.png", width=6.6 * inch, height=2.5 * inch, kind='proportional'),
    Paragraph("Figure 6: Chronological Validation Set Forecast Tracking (Nov 2011 – Oct 2012) and Actual versus Predicted 45-Degree Parity Scatter.", st_fig_cap)
]))
story.append(Spacer(1, 4))

story.append(Paragraph("<b>4.4 Feature Gain Attribution and Interpretation:</b> Table 5 and Figure 7 detail normalized split gain contribution across XGBoost and LightGBM.", st_body))

# Table 5 (Caption Above Table)
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
story.append(Paragraph("Table 5: Feature Importance Hierarchy Across Tree Ensembles Derived via Normalized Split Gain Attribution", st_tbl_cap))
story.append(make_rl_table(tab5_data, [0.5 * inch, 1.35 * inch, 2.3 * inch, 0.9 * inch, 0.9 * inch, 0.9 * inch]))
story.append(Spacer(1, 4))

# Figure 7 (Caption Below Figure)
story.append(KeepTogether([
    RLImage("figures/fig7_feature_importance.png", width=6.6 * inch, height=2.6 * inch, kind='proportional'),
    Paragraph("Figure 7: Top 15 Predictive Features Ranked by Relative Split Gain Contribution for XGBoost and LightGBM.", st_fig_cap)
]))
story.append(Spacer(1, 4))

story.append(Paragraph("<b>4.5 Supply Chain Inventory Optimization and Cost Reduction:</b> Figure 8 translates accuracy gains into dollarized inventory holding and stockout cost savings. Deploying LightGBM slashes mismatch penalties from $80.3M to $48.6M—saving $31.7M (-39.5%) across all 45 stores.", st_body))

# Figure 8 (Caption Below Figure)
story.append(KeepTogether([
    RLImage("figures/fig8_supply_chain_impact.png", width=6.6 * inch, height=2.3 * inch, kind='proportional'),
    Paragraph("Figure 8: Error Breakdown on Holiday vs. Regular Weeks and Supply Chain Mismatch Cost Savings Across Store Formats.", st_fig_cap)
]))
story.append(Spacer(1, 4))

# Chapter 5: Conclusion
story.append(Paragraph("Chapter 5: Conclusion", st_h1))
story.append(Paragraph("<b>5.1 Summary of Research Achievements:</b> This study successfully designed, implemented, and validated an end-to-end predictive analytics regression pipeline for multi-store retail sales forecasting following the formal Knowledge Discovery in Databases (KDD) process. By integrating 421,570 historical transaction records across 45 stores and 81 departments with promotional markdown schedules, holiday calendars, and macroeconomic indicators, the system addressed the operational challenges of modern retail inventory planning. Robust preprocessing successfully resolved extensive promotional markdown missingness (64%–74%), handled customer accounting returns, and preserved genuine holiday demand spikes without statistical bias. Engineering 43 leak-free predictive features equipped tree-based ensembles with rich temporal context without introducing look-ahead leakage.", st_body))

story.append(Paragraph("<b>5.2 Operational Supply Chain Recommendations:</b> Quantitative benchmarking established that LightGBM is the superior predictive architecture for retail sales forecasting, achieving a WMAE of $1,758.94 (a 60.0% error reduction relative to the Baseline Ridge model), an RMSE of $3,837.62, and an R2 of 0.9725. Crucially, LightGBM reduced Holiday MAE by 76.0% ($2,421.19 vs. $10,108.52), directly mitigating the risk of catastrophic stockouts during Black Friday and Christmas. From an operational supply chain perspective, these accuracy gains translate into an estimated $31.7M (39.5%) reduction in inventory holding and stockout mismatch costs across the 45 Walmart stores.", st_body))

story.append(Paragraph("<b>5.3 Limitations and Future Scope:</b> Based on the empirical findings, two actionable deployment policies are recommended for retail operations: (1) A Dual-Regime Deployment Policy: Deploy LightGBM for Q4 holiday pre-staging and distribution center safety stock allocation, where its superior handling of high-stakes holiday spikes (w = 5) prevents stockouts, while utilizing XGBoost for routine weekly replenishment, where it achieved the lowest regular-week MAE ($1,410.37); (2) Early Promotional Buffer Synchronization: Because MarkDown2 and MarkDown3 exhibit high concentration during Thanksgiving and pre-Christmas weeks, procurement teams should pre-allocate safety stock 3 to 4 weeks prior to Weeks 47 and 50. Future work will extend point forecasts to probabilistic quantile regression (Conformal Prediction) and Temporal Fusion Transformers (TFT).", st_body))

# Chapter 6: References
story.append(Paragraph("Chapter 6: References", st_h1))
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
    story.append(Paragraph(ref, ParagraphStyle('RefStyle', fontName='Times-Roman', fontSize=10, leading=14, textColor=colors.HexColor('#1E293B'), alignment=TA_JUSTIFY, spaceBefore=3, spaceAfter=3)))

def add_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('Times-Roman', 9.5)
    canvas.setFillColor(colors.HexColor('#64748B'))
    canvas.drawString(0.75 * inch, 0.45 * inch, "Dev Dilip Dhapodkar (PRN: 24070521505) — Predictive Analytics CA3 Project Report")
    canvas.drawRightString(A4[0] - 0.75 * inch, 0.45 * inch, f"Page {doc.page}")
    canvas.restoreState()

pdf_doc.build(story, onFirstPage=add_footer, onLaterPages=add_footer)
print(f"Successfully generated {pdf_filename}!")

import shutil
shutil.copyfile(pdf_filename, "24070521505_Dev_Dhapodkar.pdf")
shutil.copyfile(pdf_filename, "Walmart_Sales_Forecasting_Report.pdf")
print("Also created 24070521505_Dev_Dhapodkar.pdf and updated Walmart_Sales_Forecasting_Report.pdf!")
