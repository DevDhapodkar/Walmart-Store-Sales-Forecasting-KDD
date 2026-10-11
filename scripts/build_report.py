import os
import json
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image as RLImage,
    Table, TableStyle, PageBreak, KeepTogether
)

# ==============================================================================
# CONTENT DEFINITIONS FOR CHAPTERS 1 - 6
# ==============================================================================
TITLE = "End-to-End Retail Store Sales Forecasting and Supply Chain Inventory Optimization Using the KDD Process"
SUBTITLE = "Predictive Analytics Continuous Assessment 3 (CA3) — Project Report"

LIT_REVIEW_TABLE = [
    ["Author(s) & Year", "Methodology / Model", "Dataset / Domain", "Key Findings & Limitations"],
    ["Box & Jenkins (2015); Hyndman & Athanasopoulos (2021)", "ARIMA, SARIMAX & Exponential Smoothing (ETS)", "Univariate & Multi-seasonal Retail Time Series", "Captures linear autocorrelation well; struggles with abrupt non-linear promotional spikes and cross-store feature interactions."],
    ["Chen & Guestrin (2016)", "XGBoost (Regularized Gradient Boosted Trees)", "Large-scale Tabular & Time-Series Benchmarks", "Second-order Taylor expansion with L1/L2 tree regularization handles sparse promotional features and non-linear interactions effectively."],
    ["Ke et al. (2017)", "LightGBM (GOSS & EFB Histogram Boosting)", "High-dimensional Multi-Store Retail Datasets", "Leaf-wise tree growth reduces training time by >80% over depth-wise boosting while improving accuracy on skewed targets."],
    ["Makridakis et al. (2022)", "M5 Forecasting Accuracy Competition (LightGBM / Ensembles)", "Walmart Hierarchical Store-Item Sales (42,840 series)", "Gradient boosted trees with multi-horizon lag and rolling window features outperformed pure statistical and deep learning baselines."],
    ["Barrow & Kourentzes (2016)", "Safety Stock & Inventory Buffer Optimization under Forecast Error", "Retail Supply Chain Operations", "Demonstrated that reducing holiday peak forecast MAE directly lowers safety stock holding costs and stockout penalties."]
]

DATASET_TABLE = [
    ["Dataset File", "Records", "Columns", "Primary Key / Granularity", "Key Attributes & Description"],
    ["stores.csv", "45", "3", "Store (1–45)", "Store Format Type (A: 22 Supercenters, B: 17 Discount, C: 6 Neighborhood) and physical Size (34,875 to 219,622 sq. ft.)."],
    ["features.csv", "8,190", "12", "(Store, Date)", "Temperature, Fuel_Price, MarkDown1–MarkDown5 (promotional markdowns), CPI, Unemployment, and IsHoliday."],
    ["train.csv", "421,570", "5", "(Store, Dept, Date)", "Historical Weekly_Sales across 45 stores and 81 departments over 143 weeks (2010-02-05 to 2012-10-26)."],
    ["test.csv", "115,064", "4", "(Store, Dept, Date)", "Evaluation horizon spanning 39 weeks (2012-11-02 to 2013-07-26) for out-of-sample forecasting."]
]

MISSING_TABLE = [
    ["Attribute / Variable", "Missing Count (train merged)", "Missing % (train merged)", "Missing Count (features.csv)", "Imputation & Treatment Strategy"],
    ["MarkDown1 (General Promo)", "270,889", "64.26%", "4,158 (50.77%)", "Extract Has_MarkDown indicator; structural zero imputation (0.0); clip < 0"],
    ["MarkDown2 (Seasonal Promo)", "310,322", "73.61%", "5,269 (64.33%)", "Extract Active_MarkDown_Count; structural zero imputation (0.0)"],
    ["MarkDown3 (Holiday Promo)", "284,479", "67.48%", "4,577 (55.89%)", "Structural zero imputation (0.0); interaction term with IsHoliday"],
    ["MarkDown4 (Dept Promo)", "286,603", "67.98%", "4,726 (57.70%)", "Structural zero imputation (0.0); summed into Total_MarkDown"],
    ["MarkDown5 (Clearance)", "270,138", "64.08%", "4,140 (50.55%)", "Structural zero imputation (0.0); summed into Total_MarkDown"],
    ["CPI (Consumer Price Index)", "0", "0.00%", "585 (7.14%)", "Store-grouped chronological forward/backward fill (ffill / bfill)"],
    ["Unemployment Rate (%)", "0", "0.00%", "585 (7.14%)", "Store-grouped chronological forward/backward fill (ffill / bfill)"],
    ["Weekly_Sales (< 0 / Outliers)", "1,285 (< $0)", "0.30%", "N/A", "Floor negative accounting returns at $0.00; cap non-holiday >99.95th pct ($183,494)"]
]

RESULTS_TABLE = [
    ["Model Architecture", "WMAE ($ USD) ↓", "RMSE ($ USD) ↓", "MAE ($ USD) ↓", "R² Score ↑", "Holiday MAE (w=5) ↓", "Regular MAE (w=1) ↓", "Train Time"],
    ["Baseline (Ridge Regression)", "$4,393.17", "$6,616.57", "$2,514.98", "0.9183", "$10,108.52", "$1,835.29", "0.20 s"],
    ["Random Forest Regressor", "$1,791.54", "$4,413.86", "$1,520.75", "0.9637", "$2,615.57", "$1,422.75", "42.88 s"],
    ["XGBoost Regressor", "$1,837.57", "$4,306.19", "$1,523.89", "0.9654", "$2,792.11", "$1,410.37", "6.31 s"],
    ["LightGBM Regressor (Best)", "$1,758.94", "$3,837.62", "$1,541.31", "0.9725", "$2,421.19", "$1,462.55", "4.91 s"]
]

FEATURE_IMP_TABLE = [
    ["Rank", "Feature Name", "Feature Category", "XGBoost Gain (%)", "LightGBM Gain (%)", "Random Forest Imp. (%)"],
    ["1", "Lag_52", "Year-over-Year Seasonal Autoregression", "31.45%", "40.87%", "26.30%"],
    ["2", "Rolling_Mean_4", "4-Week Moving Average (t-1 shifted)", "24.61%", "17.19%", "29.15%"],
    ["3", "Lag_1", "Immediate Prior Week Sales (t-1)", "12.97%", "22.59%", "20.95%"],
    ["4", "Store_Dept_Mean", "Out-of-Sample Store-Dept Historical Baseline", "6.56%", "3.91%", "5.38%"],
    ["5", "Is_Thanksgiving", "Holiday Event Indicator (Week 47, w=5)", "4.36%", "2.32%", "0.79%"],
    ["6", "Lag_2", "Two-Week Prior Sales (t-2)", "4.35%", "4.96%", "7.91%"],
    ["7", "Is_Christmas", "Holiday Event Indicator (Week 52, w=5)", "2.69%", "0.36%", "0.10%"],
    ["8", "Pre_Christmas_Peak", "Pre-Holiday Shopping Surge (Weeks 49–51)", "2.34%", "0.34%", "0.23%"],
    ["9", "Store_Dept_Std", "Store-Dept Historical Volatility", "1.73%", "2.28%", "1.63%"],
    ["10", "Store_Dept_Median", "Store-Dept Robust Baseline", "1.57%", "0.35%", "2.99%"]
]

REFERENCES = [
    "[1] U. Fayyad, G. Piatetsky-Shapiro, and P. Smyth, \"From Data Mining to Knowledge Discovery in Databases,\" AI Magazine, vol. 17, no. 3, pp. 37–54, 1996.",
    "[2] Walmart Recruiting, \"Walmart Recruiting — Store Sales Forecasting Competition Dataset,\" Kaggle, 2014. Available: https://www.kaggle.com/competitions/walmart-recruiting-store-sales-forecasting/data",
    "[3] T. Chen and C. Guestrin, \"XGBoost: A Scalable Tree Boosting System,\" in Proc. 22nd ACM SIGKDD Int. Conf. Knowledge Discovery and Data Mining (KDD), San Francisco, CA, USA, 2016, pp. 785–794.",
    "[4] G. Ke, Q. Meng, T. Finley, T. Wang, W. Chen, W. Ma, Q. Ye, and T.-Y. Liu, \"LightGBM: A Highly Efficient Gradient Boosting Decision Tree,\" in Advances in Neural Information Processing Systems (NeurIPS), vol. 30, pp. 3146–3154, 2017.",
    "[5] L. Breiman, \"Random Forests,\" Machine Learning, vol. 45, no. 1, pp. 5–32, 2001.",
    "[6] S. Makridakis, E. Spiliotis, and V. Assimakopoulos, \"M5 Accuracy Competition: Results, Findings, and Conclusions,\" International Journal of Forecasting, vol. 38, no. 4, pp. 1346–1364, 2022.",
    "[7] R. J. Hyndman and G. Athanasopoulos, Forecasting: Principles and Practice, 3rd ed. Melbourne, Australia: OTexts, 2021.",
    "[8] G. E. P. Box, G. M. Jenkins, G. C. Reinsel, and G. M. Ljung, Time Series Analysis: Forecasting and Control, 5th ed. Hoboken, NJ, USA: John Wiley & Sons, 2015.",
    "[9] D. K. Barrow and N. Kourentzes, \"Distributions of Forecasting Errors of Forecast Combinations: Implications for Inventory Management,\" International Journal of Production Economics, vol. 177, pp. 24–33, 2016.",
    "[10] R. Fildes, S. Ma, and S. Kolassa, \"Retail Forecasting: Research and Practice,\" International Journal of Forecasting, vol. 38, no. 4, pp. 1283–1318, 2022.",
    "[11] A. E. Hoerl and R. W. Kennard, \"Ridge Regression: Biased Estimation for Nonorthogonal Problems,\" Technometrics, vol. 12, no. 1, pp. 55–67, 1970.",
    "[12] S. Chopra and P. Meindl, Supply Chain Management: Strategy, Planning, and Operation, 7th ed. Boston, MA, USA: Pearson, 2019."
]

# ==============================================================================
# 1. GENERATE WORD DOCUMENT (.docx)
# ==============================================================================
print("Building Walmart_Sales_Forecasting_Report.docx...")
doc = Document()

for section in doc.sections:
    section.top_margin = Inches(0.85)
    section.bottom_margin = Inches(0.85)
    section.left_margin = Inches(0.9)
    section.right_margin = Inches(0.9)

style_normal = doc.styles['Normal']
style_normal.font.name = 'Calibri'
style_normal.font.size = Pt(11)

def add_heading_styled(doc, text, level=1):
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        run.font.name = 'Calibri'
        run.font.bold = True
        if level == 1:
            run.font.size = Pt(16)
            run.font.color.rgb = RGBColor(15, 41, 66)
        elif level == 2:
            run.font.size = Pt(13)
            run.font.color.rgb = RGBColor(0, 113, 206)
        else:
            run.font.size = Pt(11.5)
            run.font.color.rgb = RGBColor(30, 58, 138)
    return h

def add_docx_table(doc, data_rows):
    tbl = doc.add_table(rows=len(data_rows), cols=len(data_rows[0]))
    tbl.style = 'Table Grid'
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, row in enumerate(data_rows):
        for j, val in enumerate(row):
            cell = tbl.cell(i, j)
            cell.text = str(val)
            for p in cell.paragraphs:
                p.paragraph_format.space_before = Pt(2)
                p.paragraph_format.space_after = Pt(2)
                for run in p.runs:
                    run.font.name = 'Calibri'
                    run.font.size = Pt(9.5)
                    if i == 0:
                        run.font.bold = True
                        run.font.color.rgb = RGBColor(255, 255, 255)
            if i == 0:
                shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="0F2942"/>')
                cell._tc.get_or_add_tcPr().append(shading)
            elif i % 2 == 1:
                shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F8FAFC"/>')
                cell._tc.get_or_add_tcPr().append(shading)
    doc.add_paragraph()

def add_docx_figure(doc, path, caption, width_in=6.4):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.add_picture(path, width=Inches(width_in))
    cap = doc.add_paragraph(caption)
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for r in cap.runs:
        r.font.size = Pt(9.5)
        r.font.italic = True
        r.font.color.rgb = RGBColor(71, 85, 105)

# Cover / Title Header
p_title = doc.add_paragraph()
p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
r_sub = p_title.add_run("PREDICTIVE ANALYTICS — CONTINUOUS ASSESSMENT 3 (CA3)\nEND-TO-END PREDICTIVE MODEL DEVELOPMENT REPORT\n\n")
r_sub.font.size = Pt(12)
r_sub.font.bold = True
r_sub.font.color.rgb = RGBColor(0, 113, 206)

r_main = p_title.add_run(TITLE + "\n\n")
r_main.font.size = Pt(20)
r_main.font.bold = True
r_main.font.color.rgb = RGBColor(15, 41, 66)

r_meta = p_title.add_run(
    "Dataset: Kaggle Walmart Recruiting — Store Sales Forecasting (421,570 Historical Sales Records)\n"
    "Methodology: Knowledge Discovery in Databases (KDD)\n"
    "Pipeline: Data Selection & Ingestion → Missing MarkDown Imputation & Outlier Treatment → Feature Engineering → EDA → Model Training → WMAE Evaluation → Supply Chain Interpretation"
)
r_meta.font.size = Pt(10.5)
r_meta.font.color.rgb = RGBColor(71, 85, 105)

doc.add_paragraph("_" * 78)

# Chapter 1: Introduction
add_heading_styled(doc, "Chapter 1: Introduction", level=1)
add_heading_styled(doc, "1.1 Background and Motivation", level=2)
doc.add_paragraph(
    "Modern big-box retail networks operate across thousands of store-department combinations subject to complex seasonal cycles, promotional price markdowns, holiday calendar spikes, and regional macroeconomic fluctuations. Walmart, the world's largest omnichannel retailer, manages inventory replenishment across diverse store formats ranging from massive Supercenters (Type A) to regional Discount Stores (Type B) and compact Neighborhood Markets (Type C). Accurate weekly department-level sales forecasting forms the quantitative backbone of retail supply chain management, directly governing procurement schedules, safety stock allocation, distribution center routing, and working capital utilization."
)
add_heading_styled(doc, "1.2 Problem Statement", level=2)
doc.add_paragraph(
    "The objective of this project is to develop an end-to-end predictive analytics regression model that forecasts weekly department-level sales across 45 Walmart stores and 81 departments using historical sales records, promotional markdown channels (MarkDown1–MarkDown5), holiday calendar events (Super Bowl, Labor Day, Thanksgiving, and Christmas), and macroeconomic indicators (Consumer Price Index, Fuel Price, Unemployment Rate, and Ambient Temperature). In retail supply chains, forecast errors manifest asymmetrically: under-forecasting during major holiday weeks causes immediate out-of-stock (OOS) occurrences and lost customer goodwill, whereas over-forecasting inflates warehouse holding costs and forces margin-dilutive clearance markdowns."
)
add_heading_styled(doc, "1.3 Project Objectives and Supply Chain Scope", level=2)
objectives = [
    "1. Relational Data Integration & KDD Structuring: Unify historical department sales (421,570 training records across 143 weeks) with store metadata and regional macroeconomic/markdown time series.",
    "2. Robust Preprocessing & Outlier Treatment: Address structural missingness in promotional markdowns (64%–74% missing prior to November 2011), propagate regional CPI/Unemployment series, floor negative accounting returns (1,285 records), and winsorize extreme non-holiday outliers.",
    "3. Leak-Free Temporal Feature Engineering: Construct 43 domain-specific features capturing multi-horizon lags (Lag_1, Lag_2, Lag_4, Lag_52), shifted rolling averages (4-week and 12-week), Fourier cyclical seasonality, and holiday-markdown interactions.",
    "4. Multi-Model Benchmarking under WMAE: Train and compare a linear Baseline (Ridge Regression), Random Forest Regressor, XGBoost Regressor, and LightGBM Regressor under the official Kaggle Weighted Mean Absolute Error (WMAE) metric where holiday weeks carry 5x weight (w = 5).",
    "5. Supply Chain Inventory Optimization: Translate forecast accuracy improvements into concrete reductions in safety stock holding costs and stockout penalty exposure across Store Types A, B, and C."
]
for obj in objectives:
    doc.add_paragraph(obj)

# Chapter 2: Literature Review
add_heading_styled(doc, "Chapter 2: Literature Review", level=1)
add_heading_styled(doc, "2.1 Evolution of Retail Demand Forecasting", level=2)
doc.add_paragraph(
    "Classical retail forecasting relied predominantly on univariate autoregressive integrated moving average (ARIMA) and exponential smoothing (ETS) state-space models [7], [8]. While effective for stationary, aggregate store-level series, classical parametric approaches require training thousands of independent local models across store-department pairs and struggle to incorporate exogenous promotional markdowns, discontinuous holiday calendar shifts, and cross-sectional store format hierarchies [10]."
)
add_heading_styled(doc, "2.2 Tree-Based Ensembles and Gradient Boosting in Retail", level=2)
doc.add_paragraph(
    "The paradigm shifted decisively following the Kaggle Walmart Recruiting Competition [2] and the M5 Forecasting Accuracy Competition [6], where global tree-based ensembles—specifically Random Forests [5], XGBoost [3], and LightGBM [4]—consistently outperformed both classical econometric models and pure recurrent neural networks. By pooling cross-sectional observations across all 45 stores and 81 departments into a unified global tabular representation enriched with autoregressive lags and rolling statistics, gradient boosted decision trees learn complex non-linear interactions between store size, promotional markdown depth, and holiday timing."
)
add_heading_styled(doc, "2.3 Comparative Literature Summary & Research Gap", level=2)
add_docx_table(doc, LIT_REVIEW_TABLE)
doc.add_paragraph(
    "Research Gap Addressed: Existing studies frequently evaluate models solely using unweighted RMSE or MAE, ignoring the asymmetric cost of holiday stockouts, or introduce subtle temporal data leakage when computing rolling window statistics. This study implements a strictly leak-free KDD pipeline with explicit holiday sample weighting (w = 5) and quantifies the downstream financial impact on supply chain holding and stockout costs."
)

# Chapter 3: Workflow & Methodology
add_heading_styled(doc, "Chapter 3: Workflow and Methodology", level=1)
add_heading_styled(doc, "3.1 End-to-End KDD Pipeline Architecture", level=2)
doc.add_paragraph(
    "Following Fayyad et al.'s Knowledge Discovery in Databases (KDD) framework [1], our implementation proceeds sequentially through seven stages: (1) Data Selection & Ingestion (Walmart Dataset) → (2) Preprocessing (Missing MarkDown Imputation & Outlier Treatment) → (3) Feature Engineering (Lags, Rolling Averages, Holiday & Promo Indicators) → (4) Exploratory Data Analysis (EDA) → (5) Model Training (Baseline Ridge, Random Forest, XGBoost, LightGBM) → (6) Model Evaluation (WMAE, RMSE, MAE, R²) → (7) Feature Importance & Supply Chain Interpretation."
)
add_heading_styled(doc, "3.2 Data Selection & Relational Schema", level=2)
add_docx_table(doc, DATASET_TABLE)

add_heading_styled(doc, "3.3 Data Preprocessing: Missing MarkDown Imputation & Outlier Treatment", level=2)
doc.add_paragraph(
    "A rigorous diagnostic of the merged dataset revealed three critical data quality challenges requiring domain-aligned preprocessing:"
)
add_docx_table(doc, MISSING_TABLE)

add_heading_styled(doc, "3.4 Feature Engineering Pipeline (43 Predictors)", level=2)
doc.add_paragraph(
    "To equip regression models with rich temporal context without introducing look-ahead bias, we engineered 43 features across five families:\n"
    "• Autoregressive Lag Features: Grouped by (Store, Dept) and sorted by Date, we extract Lag_1 (t-1 week), Lag_2 (t-2 weeks), Lag_4 (t-4 weeks / 1-month prior), and Lag_52 (t-52 weeks / exact year-over-year seasonal anchor).\n"
    "• Leak-Free Rolling Window Statistics: Using strictly shifted series s.shift(1), we compute Rolling_Mean_4 (4-week moving average), Rolling_Std_4 (4-week demand volatility), Rolling_Mean_12 (quarterly baseline), and short-term velocity Momentum_1_4 = Lag_1 - Rolling_Mean_4.\n"
    "• Holiday & Promotional Indicators: Explicit binary indicators for Super Bowl (Feb), Labor Day (Sep), Thanksgiving (Nov), Christmas (Dec), Pre_Christmas_Peak (Weeks 49–51), Active_MarkDown_Count, Total_MarkDown, and Promo_Holiday_Interaction.\n"
    "• Cyclical Fourier Encodings: Continuous sine and cosine transforms of ISO Week (Week_Sin, Week_Cos) and Month (Month_Sin, Month_Cos) to preserve circular calendar continuity between Week 52 and Week 1.\n"
    "• Out-of-Sample Target Encodings: Store_Dept_Mean, Store_Dept_Median, and Store_Dept_Std computed exclusively on the training split (prior to 2011-11-25) and mapped onto validation records."
)

add_heading_styled(doc, "3.5 Mathematical Formulation of Models and Evaluation Metrics", level=2)
doc.add_paragraph(
    "1. Weighted Mean Absolute Error (WMAE): The primary competition metric weights holiday weeks five times higher than normal weeks: WMAE = [ Σ w_i · |y_i - ŷ_i| ] / [ Σ w_i ], where w_i = 5 if IsHoliday_i is True and w_i = 1 otherwise.\n"
    "2. Baseline Ridge Regression: Minimizes L2-penalized squared residuals: L(β) = ||y - Xβ||₂² + α||β||₂² with α = 100.0 on standardized predictors.\n"
    "3. Random Forest Regressor: Constructs B = 100 decorrelated regression trees (max_depth = 16, max_features = 0.6) trained via bootstrap aggregation with holiday sample weights.\n"
    "4. XGBoost & LightGBM Regressors: Additive tree ensembles ŷ_i = Σ f_k(x_i) optimizing a second-order Taylor expansion of the sample-weighted objective with L1/L2 regularization (XGBoost depth-wise max_depth = 8; LightGBM leaf-wise num_leaves = 63)."
)

# Chapter 4: Results & Discussion
add_heading_styled(doc, "Chapter 4: Experimental Results and Discussion", level=1)
add_heading_styled(doc, "4.1 Exploratory Data Analysis (EDA) Findings", level=2)
doc.add_paragraph(
    "Exploratory visual analysis across the 421,570 historical records uncovered fundamental structural drivers of retail demand. Aggregate weekly sales across all 45 stores fluctuate around $47.1M during regular weeks but surge to $66.6M during Thanksgiving (+44.0% store average lift) and nearly $80M during the pre-Christmas shopping peak (Weeks 49–51, +40.2% lift), followed by a sharp drop on Christmas week (-6.0%) as stores close early. Store physical square footage exhibits a strong positive linear correlation (r = 0.81) with average weekly sales across Type A Supercenters ($1.45M/week), Type B Discount Stores ($0.79M/week), and Type C Neighborhood Markets ($0.46M/week)."
)
add_docx_figure(doc, "figures/fig1_eda_sales_overview.png", "Figure 1: Aggregate Weekly Retail Sales Trend (2010–2012), Format Distribution, and Store Size Elasticity.")
add_docx_figure(doc, "figures/fig2_outlier_and_markdown_analysis.png", "Figure 2: Pre-Imputation Missingness Profile, Outlier Thresholds, and Promotional Markdown Depth by Channel.")
add_docx_figure(doc, "figures/fig3_holiday_and_macro_effects.png", "Figure 3: Holiday Event Sales Lift and Standardized Macroeconomic Indicator Trajectories (2010–2012).")
add_docx_figure(doc, "figures/fig4_correlation_matrix.png", "Figure 4: Pearson Correlation Matrix Across Autoregressive Lags, Store Size, Markdowns, and Macroeconomics.")

add_heading_styled(doc, "4.2 Quantitative Model Evaluation (WMAE, RMSE, MAE, R²)", level=2)
doc.add_paragraph(
    "To evaluate out-of-sample generalization without temporal leakage, the dataset was partitioned chronologically at 2011-11-25 into 263,199 training records and 145,237 validation records (49 weeks encompassing Thanksgiving 2011, Christmas 2011, Super Bowl 2012, and Labor Day 2012). Table 4.1 summarizes model performance across all evaluation metrics."
)
add_docx_table(doc, RESULTS_TABLE)
doc.add_paragraph(
    "Key Comparative Insights:\n"
    "• LightGBM Regressor achieved the best overall WMAE of $1,758.94 (a 60.0% reduction compared to the Baseline Ridge WMAE of $4,393.17), the lowest RMSE of $3,837.62 (-42.0% vs. Baseline), and the highest coefficient of determination R² = 0.9725 while training in just 4.91 seconds.\n"
    "• Holiday Peak Accuracy: Baseline Ridge Regression suffered a Holiday MAE of $10,108.52 because linear combinations of recent lags cannot capture abrupt non-linear Thanksgiving and Christmas spikes. LightGBM reduced Holiday MAE by 76.0% to $2,421.19.\n"
    "• Regular Week Accuracy: XGBoost achieved the lowest Non-Holiday MAE of $1,410.37 (followed closely by Random Forest at $1,422.75 and LightGBM at $1,462.55), demonstrating exceptional week-to-week replenishment precision."
)
add_docx_figure(doc, "figures/fig5_model_comparison.png", "Figure 5: Multi-Metric Validation Set Performance Comparison Across WMAE, RMSE, MAE, and R².")
add_docx_figure(doc, "figures/fig6_actual_vs_predicted.png", "Figure 6: Chronological Validation Forecast Tracking (Nov 2011 – Oct 2012) and Actual vs. Predicted Parity.")

add_heading_styled(doc, "4.3 Feature Importance & Gain Attribution", level=2)
doc.add_paragraph(
    "Table 4.2 and Figure 7 present the relative split gain attribution for XGBoost and LightGBM alongside Random Forest impurity importance. Year-over-year seasonal lag (Lag_52) is the single most influential predictor (31.45% in XGBoost, 40.87% in LightGBM), followed by recent 4-week rolling demand (Rolling_Mean_4: 24.61% in XGBoost) and immediate prior-week sales (Lag_1: 22.59% in LightGBM). Explicit holiday indicators (Is_Thanksgiving, Is_Christmas, Pre_Christmas_Peak) contribute 9.39% of total gain in XGBoost, enabling rapid upward adjustment during Q4 holiday peaks."
)
add_docx_table(doc, FEATURE_IMP_TABLE)
add_docx_figure(doc, "figures/fig7_feature_importance.png", "Figure 7: Top 15 Predictive Features by Normalized Split Gain (%) for XGBoost and LightGBM.")

add_heading_styled(doc, "4.4 Supply Chain Inventory Optimization & Business Impact", level=2)
doc.add_paragraph(
    "In retail supply chain operations, absolute forecast errors translate directly into excess safety stock holding costs (when ŷ > y) and stockout margin penalties (when ŷ < y). Applying an industry-standard 22% annualized inventory mismatch cost factor across the 145,237 validation department-weeks, deploying gradient boosted trees reduces total mismatch cost from $80.3M (Baseline Ridge) to $48.6M—delivering $31.7M (-39.5%) in supply chain cost savings ($17.1M saved across 22 Type A Supercenters, $12.8M saved across 17 Type B Discount Stores, and $1.8M saved across 6 Type C Neighborhood Markets)."
)
add_docx_figure(doc, "figures/fig8_supply_chain_impact.png", "Figure 8: Holiday vs. Regular Week Error Breakdown and Estimated Supply Chain Mismatch Cost Savings by Store Format.")

# Chapter 5: Conclusion & Future Scope
add_heading_styled(doc, "Chapter 5: Conclusion and Future Scope", level=1)
doc.add_paragraph(
    "This study successfully developed, validated, and interpreted an end-to-end predictive analytics regression pipeline for multi-store department-level sales forecasting following the KDD methodology. By integrating 421,570 historical sales records with promotional markdowns, holiday indicators, and macroeconomic signals, and engineering 43 leak-free autoregressive and seasonal predictors, our gradient-boosted models achieved R² = 0.9725 and reduced WMAE by 60.0% ($1,758.94 vs. $4,393.17).\n\n"
    "Actionable Supply Chain Recommendations:\n"
    "1. Dual-Regime Replenishment Policy: Deploy LightGBM (WMAE = $1,758.94, Holiday MAE = $2,421.19) for Q4 holiday inventory pre-staging and XGBoost (Non-Holiday MAE = $1,410.37) for routine weekly automated replenishment.\n"
    "2. Pre-Holiday Promotional Synchronization: Since MarkDown2 and MarkDown3 exhibit massive amplification during holiday weeks, distribution centers should increase safety stock buffers 3 weeks prior to Weeks 47 and 50.\n"
    "3. Future Scope: Extend point predictions to probabilistic quantile forecasting (Pinball Loss / Conformal Prediction) and explore Temporal Fusion Transformers (TFT) and hierarchical reconciliation across store-department trees."
)

# Chapter 6: References
add_heading_styled(doc, "Chapter 6: References", level=1)
for ref in REFERENCES:
    p_ref = doc.add_paragraph(ref)
    p_ref.paragraph_format.space_after = Pt(4)

doc.save("Walmart_Sales_Forecasting_Report.docx")
print("Saved Walmart_Sales_Forecasting_Report.docx successfully!")

# ==============================================================================
# 2. GENERATE PDF DOCUMENT (.pdf) VIA REPORTLAB
# ==============================================================================
print("Building Walmart_Sales_Forecasting_Report.pdf...")

pdf_doc = SimpleDocTemplate(
    "Walmart_Sales_Forecasting_Report.pdf",
    pagesize=A4,
    leftMargin=0.65 * inch,
    rightMargin=0.65 * inch,
    topMargin=0.62 * inch,
    bottomMargin=0.65 * inch
)

styles = getSampleStyleSheet()
st_title = ParagraphStyle('DocTitle', parent=styles['Title'], fontName='Helvetica-Bold', fontSize=17, leading=22, textColor=colors.HexColor('#0F2942'), alignment=TA_CENTER, spaceAfter=8)
st_sub = ParagraphStyle('DocSub', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10.5, leading=14, textColor=colors.HexColor('#0071CE'), alignment=TA_CENTER, spaceAfter=4.5)
st_meta = ParagraphStyle('DocMeta', parent=styles['Normal'], fontName='Helvetica', fontSize=9.2, leading=13, textColor=colors.HexColor('#475569'), alignment=TA_CENTER, spaceAfter=14)
st_h1 = ParagraphStyle('ChapH1', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=14, leading=18, textColor=colors.HexColor('#0F2942'), spaceBefore=14, spaceAfter=4.5)
st_h2 = ParagraphStyle('ChapH2', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=11.2, leading=15, textColor=colors.HexColor('#0071CE'), spaceBefore=10, spaceAfter=4)
st_body = ParagraphStyle('BodyJust', parent=styles['Normal'], fontName='Helvetica', fontSize=9.6, leading=13.8, textColor=colors.HexColor('#1E293B'), alignment=TA_JUSTIFY, spaceAfter=4.5)
st_cap = ParagraphStyle('FigCap', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=8.6, leading=11.5, textColor=colors.HexColor('#475569'), alignment=TA_CENTER, spaceBefore=3, spaceAfter=10)
st_th = ParagraphStyle('TblHdr', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.2, leading=10.5, textColor=colors.white, alignment=TA_CENTER)
st_td = ParagraphStyle('TblCell', parent=styles['Normal'], fontName='Helvetica', fontSize=8.0, leading=10.5, textColor=colors.HexColor('#1E293B'), alignment=TA_LEFT)


def clean_pdf_str(s):
    return (str(s)
        .replace('↓', '')
        .replace('↑', '')
        .replace('→', '->')
        .replace('Σ', 'Sum')
        .replace('ŷ', 'y_hat')
        .replace('•', '-')
    )

def rl_table(data_rows, col_widths):
    wrapped = []
    for i, r in enumerate(data_rows):
        row_cells = []
        for c in r:
            row_cells.append(Paragraph(clean_pdf_str(c), st_th if i == 0 else st_td))
        wrapped.append(row_cells)
    t = Table(wrapped, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F2942')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    return t

def rl_fig(path, caption, w_in=6.7, h_in=2.7):
    img = RLImage(path, width=w_in * inch, height=h_in * inch, kind='proportional')
    return KeepTogether([Spacer(1, 4), img, Paragraph(caption, st_cap)])

story = []

# Title Block
story.append(Paragraph("PREDICTIVE ANALYTICS — CONTINUOUS ASSESSMENT 3 (CA3)", st_sub))
story.append(Paragraph(TITLE, st_title))
story.append(Paragraph(
    "<b>Submitted By:</b> Dev Dilip Dhapodkar &nbsp;&nbsp;|&nbsp;&nbsp; <b>PRN:</b> 24070521505<br/>"
    "<b>Dataset:</b> Kaggle Walmart Recruiting — Store Sales Forecasting (421,570 Records, 45 Stores, 81 Departments) &nbsp;|&nbsp; "
    "<b>Methodology:</b> Knowledge Discovery in Databases (KDD)", st_meta
))

# Chapter 1
story.append(Paragraph("Chapter 1: Introduction", st_h1))
story.append(Paragraph("1.1 Background and Motivation", st_h2))
story.append(Paragraph(
    "Modern big-box retail networks operate across thousands of store-department combinations subject to complex seasonal cycles, promotional price markdowns, holiday calendar spikes, and regional macroeconomic fluctuations. Walmart manages inventory replenishment across diverse store formats ranging from Supercenters (Type A) to Discount Stores (Type B) and Neighborhood Markets (Type C). Accurate weekly department-level sales forecasting forms the quantitative backbone of retail supply chain management, directly governing procurement schedules, safety stock allocation, distribution center routing, and working capital utilization.", st_body
))
story.append(Paragraph("1.2 Problem Statement & Supply Chain Objectives", st_h2))
story.append(Paragraph(
    "The objective of this project is to develop an end-to-end predictive analytics regression model that forecasts weekly department-level sales across 45 Walmart stores and 81 departments using historical sales records, promotional markdown channels (MarkDown1–MarkDown5), holiday calendar events (Super Bowl, Labor Day, Thanksgiving, and Christmas), and macroeconomic indicators (CPI, Fuel Price, Unemployment, Temperature). Under-forecasting during high-velocity holiday weeks causes immediate out-of-stock (OOS) occurrences and lost customer goodwill (weighted 5x in WMAE), whereas over-forecasting inflates warehouse holding costs. Our KDD pipeline addresses both failure modes simultaneously.", st_body
))
for obj in objectives:
    story.append(Paragraph(obj, st_body))

# Chapter 2
story.append(Paragraph("Chapter 2: Literature Review", st_h1))
story.append(Paragraph(
    "Classical retail forecasting relied predominantly on univariate ARIMA and exponential smoothing (ETS) models [7], [8], which struggle to incorporate exogenous promotional markdowns, discontinuous holiday shifts, and cross-sectional store format hierarchies. Following the Kaggle Walmart Recruiting Competition [2] and the M5 Forecasting Competition [6], global tree-based ensembles—Random Forests [5], XGBoost [3], and LightGBM [4]—demonstrated superior capability by pooling cross-store observations with multi-horizon autoregressive lags and rolling statistics.", st_body
))
story.append(rl_table(LIT_REVIEW_TABLE, [1.35*inch, 1.45*inch, 1.45*inch, 2.65*inch]))
story.append(Spacer(1, 6))
story.append(Paragraph(
    "<b>Research Gap Addressed:</b> Existing baselines often evaluate models solely using unweighted RMSE or introduce subtle temporal data leakage in rolling windows. This project implements a strictly leak-free KDD pipeline with explicit holiday sample weighting (w = 5) and quantifies downstream supply chain holding and stockout cost savings.", st_body
))

# Chapter 3
story.append(Paragraph("Chapter 3: Workflow and Methodology (KDD Process)", st_h1))
story.append(Paragraph("3.1 KDD Pipeline & Relational Data Selection", st_h2))
story.append(Paragraph(
    "Our workflow follows seven KDD stages: (1) Data Selection & Ingestion -> (2) Missing MarkDown Imputation & Outlier Treatment -> (3) Feature Engineering (Lags, Rolling Averages, Holiday & Promo Indicators) -> (4) Exploratory Data Analysis -> (5) Model Training (Baseline Ridge, Random Forest, XGBoost, LightGBM) -> (6) Model Evaluation (WMAE, RMSE, MAE, R²) -> (7) Feature Importance & Supply Chain Interpretation.", st_body
))
story.append(rl_table(DATASET_TABLE, [0.95*inch, 0.75*inch, 0.65*inch, 1.35*inch, 3.2*inch]))
story.append(Paragraph("3.2 Preprocessing: Missing MarkDown Imputation & Outlier Treatment", st_h2))
story.append(rl_table(MISSING_TABLE, [1.45*inch, 1.0*inch, 0.9*inch, 1.1*inch, 2.45*inch]))
story.append(Paragraph("3.3 Leak-Free Feature Engineering & Mathematical Formulation", st_h2))
story.append(Paragraph(
    "We engineer 43 features across five groups: (1) Autoregressive Lags (Lag_1, Lag_2, Lag_4, Lag_52 grouped by Store and Dept); (2) Shifted Rolling Statistics (Rolling_Mean_4, Rolling_Std_4, Rolling_Mean_12, and Momentum_1_4 computed on t-1 shifted series to prevent data leakage); (3) Explicit Holiday & Promo Indicators (Is_SuperBowl, Is_LaborDay, Is_Thanksgiving, Is_Christmas, Pre_Christmas_Peak, Total_MarkDown, Active_MarkDown_Count, Promo_Holiday_Interaction); (4) Fourier Cyclical Encodings (Week_Sin, Week_Cos, Month_Sin, Month_Cos); and (5) Out-of-Sample Target Encodings (Store_Dept_Mean, Store_Dept_Median, Store_Dept_Std computed strictly on the training split prior to 2011-11-25). Models are evaluated via the official Kaggle Weighted Mean Absolute Error: WMAE = [ Sum w_i |y_i - y_hat_i| ] / [ Sum w_i ], where w_i = 5 for holiday weeks and 1 for regular weeks.", st_body
))

# Chapter 4
story.append(Paragraph("Chapter 4: Experimental Results and Discussion", st_h1))
story.append(Paragraph("4.1 Exploratory Data Analysis (EDA) Insights", st_h2))
story.append(Paragraph(
    "Aggregate weekly sales average $47.1M across the 45 stores during regular weeks and surge to $66.6M during Thanksgiving (+44.0% store lift) and nearly $80M during the pre-Christmas peak (Weeks 49–51, +40.2% lift). Store square footage correlates strongly (r = 0.81) with weekly store revenue across Type A Supercenters ($1.45M/wk), Type B Discount Stores ($0.79M/wk), and Type C Neighborhood Markets ($0.46M/wk).", st_body
))
story.append(rl_fig("figures/fig1_eda_sales_overview.png", "Figure 1: Aggregate Weekly Retail Sales Trend (2010–2012), Format Distribution, and Store Size Elasticity.", 6.7, 4.1))
story.append(rl_fig("figures/fig2_outlier_and_markdown_analysis.png", "Figure 2: Pre-Imputation Missingness Profile, Outlier Thresholds, and Promotional Markdown Depth by Channel.", 6.7, 2.2))
story.append(rl_fig("figures/fig3_holiday_and_macro_effects.png", "Figure 3: Holiday Event Sales Lift and Standardized Macroeconomic Indicator Trajectories (2010–2012).", 6.7, 2.4))
story.append(rl_fig("figures/fig4_correlation_matrix.png", "Figure 4: Pearson Correlation Matrix Across Autoregressive Lags, Store Size, Markdowns, and Macroeconomics.", 6.2, 4.8))

story.append(Paragraph("4.2 Quantitative Model Evaluation (145,237 Validation Dept-Weeks)", st_h2))
story.append(rl_table(RESULTS_TABLE, [1.55*inch, 0.85*inch, 0.85*inch, 0.8*inch, 0.65*inch, 0.85*inch, 0.8*inch, 0.55*inch]))
story.append(Spacer(1, 5))
story.append(Paragraph(
    "LightGBM achieved the lowest overall WMAE of $1,758.94 (-60.0% vs. Baseline Ridge at $4,393.17), lowest RMSE of $3,837.62 (-42.0%), lowest Holiday MAE of $2,421.19 (-76.0%), and highest R² = 0.9725 in 4.91 seconds. XGBoost achieved the lowest Non-Holiday MAE of $1,410.37.", st_body
))
story.append(rl_fig("figures/fig5_model_comparison.png", "Figure 5: Multi-Metric Validation Set Performance Comparison Across WMAE, RMSE, MAE, and R².", 6.7, 2.0))
story.append(rl_fig("figures/fig6_actual_vs_predicted.png", "Figure 6: Chronological Validation Forecast Tracking (Nov 2011 – Oct 2012) and Actual vs. Predicted Parity.", 6.7, 2.6))

story.append(Paragraph("4.3 Feature Importance & Supply Chain Cost Optimization", st_h2))
story.append(rl_table(FEATURE_IMP_TABLE, [0.45*inch, 1.25*inch, 2.3*inch, 0.95*inch, 0.95*inch, 1.0*inch]))
story.append(rl_fig("figures/fig7_feature_importance.png", "Figure 7: Top 15 Predictive Features by Normalized Split Gain (%) for XGBoost and LightGBM.", 6.7, 2.7))
story.append(rl_fig("figures/fig8_supply_chain_impact.png", "Figure 8: Holiday vs. Regular Week Error Breakdown and Estimated Supply Chain Mismatch Cost Savings by Store Format.", 6.7, 2.3))

# Chapter 5 & 6
story.append(Paragraph("Chapter 5: Conclusion and Future Scope", st_h1))
story.append(Paragraph(
    "By executing the end-to-end KDD methodology on 421,570 Walmart store-department-week records and engineering 43 leak-free autoregressive, promotional, and holiday predictors, our gradient-boosted regression models achieved R² = 0.9725 and reduced WMAE by 60.0% ($1,758.94 vs. $4,393.17). Under an industry-standard 22% inventory mismatch penalty, deploying gradient boosted trees reduces cumulative validation-period holding and stockout costs from $80.3M to $48.6M—saving $31.7M (-39.5%) across the 45 stores. Future work will extend point forecasts to probabilistic quantile regression (Conformal Prediction) and Temporal Fusion Transformers (TFT).", st_body
))

story.append(Paragraph("Chapter 6: References", st_h1))
for ref in REFERENCES:
    story.append(Paragraph(ref, st_body))

def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 8.5)
    canvas.setFillColor(colors.HexColor('#64748B'))
    canvas.drawString(0.65 * inch, 0.45 * inch, "Dev Dilip Dhapodkar (PRN: 24070521505) — Predictive Analytics CA3 Project Report")
    canvas.drawRightString(A4[0] - 0.65 * inch, 0.45 * inch, f"Page {doc.page}")
    canvas.restoreState()

pdf_doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
print("Saved Walmart_Sales_Forecasting_Report.pdf successfully!")
