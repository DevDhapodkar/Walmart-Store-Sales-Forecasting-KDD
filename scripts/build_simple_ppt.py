import sys
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

# Theme Colors
C_NAVY = RGBColor(15, 41, 66)       # Primary dark navy
C_BLUE = RGBColor(0, 113, 206)      # Walmart blue
C_YELLOW = RGBColor(255, 194, 32)   # Walmart yellow accent
C_TEAL = RGBColor(13, 148, 136)     # Teal
C_CORAL = RGBColor(225, 29, 72)     # Coral red
C_DARK = RGBColor(30, 41, 59)       # Body text
C_SLATE = RGBColor(100, 116, 139)   # Subdued text
C_LIGHT_BG = RGBColor(248, 250, 252)# Card bg
C_BORDER = RGBColor(226, 232, 240)  # Border
C_WHITE = RGBColor(255, 255, 255)

def add_header(slide, title, subtitle, slide_num, total_slides=7):
    # Base background
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = C_WHITE
    bg.line.fill.background()

    # Top Navy Banner
    banner = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.0))
    banner.fill.solid()
    banner.fill.fore_color.rgb = C_NAVY
    banner.line.fill.background()

    # Yellow Accent Line
    accent = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(1.0), Inches(13.333), Inches(0.05))
    accent.fill.solid()
    accent.fill.fore_color.rgb = C_YELLOW
    accent.line.fill.background()

    # Header Text
    tb = slide.shapes.add_textbox(Inches(0.6), Inches(0.1), Inches(10.5), Inches(0.85))
    tf = tb.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = title
    p1.font.name = 'Calibri'
    p1.font.size = Pt(22)
    p1.font.bold = True
    p1.font.color.rgb = C_WHITE

    p2 = tf.add_paragraph()
    p2.text = subtitle
    p2.font.name = 'Calibri'
    p2.font.size = Pt(11.5)
    p2.font.color.rgb = RGBColor(186, 230, 253)

    # Footer
    ft = slide.shapes.add_textbox(Inches(0.6), Inches(7.12), Inches(12.133), Inches(0.3))
    fp = ft.text_frame.paragraphs[0]
    fp.text = f"Dev Dilip Dhapodkar (PRN: 24070521505)  |  Predictive Analytics CA3: Sales Forecasting                                                  Slide {slide_num} of {total_slides}"
    fp.font.name = 'Calibri'
    fp.font.size = Pt(9.5)
    fp.font.color.rgb = C_SLATE

def add_notes(slide, text):
    notes = slide.notes_slide
    notes.notes_text_frame.text = text

def add_card(slide, left, top, width, height, title, bullets, accent_color=C_BLUE):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    card.adjustments[0] = 0.03
    card.fill.solid()
    card.fill.fore_color.rgb = C_LIGHT_BG
    card.line.color.rgb = C_BORDER
    card.line.width = Pt(1)

    # Header strip
    hdr = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(0.42))
    hdr.adjustments[0] = 0.08
    hdr.fill.solid()
    hdr.fill.fore_color.rgb = accent_color
    hdr.line.fill.background()

    htb = slide.shapes.add_textbox(Inches(left + 0.15), Inches(top + 0.04), Inches(width - 0.3), Inches(0.35))
    hp = htb.text_frame.paragraphs[0]
    hp.text = title
    hp.font.name = 'Calibri'
    hp.font.size = Pt(12)
    hp.font.bold = True
    hp.font.color.rgb = C_WHITE

    btb = slide.shapes.add_textbox(Inches(left + 0.15), Inches(top + 0.48), Inches(width - 0.3), Inches(height - 0.55))
    btf = btb.text_frame
    btf.word_wrap = True
    for i, b in enumerate(bullets):
        bp = btf.paragraphs[0] if i == 0 else btf.add_paragraph()
        bp.text = b
        bp.font.name = 'Calibri'
        bp.font.size = Pt(11)
        bp.font.color.rgb = C_DARK
        bp.space_after = Pt(4)

# ==============================================================================
# SLIDE 1: TITLE SLIDE (30-40 seconds)
# ==============================================================================
s1 = prs.slides.add_slide(blank_layout)
bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
bg1.fill.solid()
bg1.fill.fore_color.rgb = C_NAVY
bg1.line.fill.background()

strip1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(0.35), Inches(7.5))
strip1.fill.solid()
strip1.fill.fore_color.rgb = C_YELLOW
strip1.line.fill.background()

tb1 = s1.shapes.add_textbox(Inches(1.0), Inches(1.1), Inches(11.5), Inches(3.2))
tf1 = tb1.text_frame
tf1.word_wrap = True

p = tf1.paragraphs[0]
p.text = "PREDICTIVE ANALYTICS — CA3 PROJECT PRESENTATION"
p.font.name = 'Calibri'
p.font.size = Pt(14)
p.font.bold = True
p.font.color.rgb = C_YELLOW
p.space_after = Pt(10)

p = tf1.add_paragraph()
p.text = "Sales Forecasting"
p.font.name = 'Calibri'
p.font.size = Pt(40)
p.font.bold = True
p.font.color.rgb = C_WHITE
p.space_after = Pt(6)

p = tf1.add_paragraph()
p.text = "End-to-End Retail Store Sales Forecasting & Supply Chain Optimization"
p.font.name = 'Calibri'
p.font.size = Pt(18)
p.font.color.rgb = RGBColor(186, 230, 253)
p.space_after = Pt(18)

p = tf1.add_paragraph()
p.text = "Presented by: Dev Dilip Dhapodkar   |   PRN: 24070521505"
p.font.name = 'Calibri'
p.font.size = Pt(16)
p.font.bold = True
p.font.color.rgb = C_YELLOW

# 3 Quick Stat Cards
def add_stat_box(slide, left, top, width, height, val, label, sub):
    b = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    b.adjustments[0] = 0.05
    b.fill.solid()
    b.fill.fore_color.rgb = C_WHITE
    b.line.fill.background()
    tb = slide.shapes.add_textbox(Inches(left), Inches(top + 0.15), Inches(width), Inches(height - 0.3))
    tf = tb.text_frame
    p1 = tf.paragraphs[0]
    p1.text = val
    p1.alignment = PP_ALIGN.CENTER
    p1.font.name = 'Calibri'
    p1.font.size = Pt(24)
    p1.font.bold = True
    p1.font.color.rgb = C_BLUE
    p2 = tf.add_paragraph()
    p2.text = label
    p2.alignment = PP_ALIGN.CENTER
    p2.font.name = 'Calibri'
    p2.font.size = Pt(11)
    p2.font.bold = True
    p2.font.color.rgb = C_NAVY
    p3 = tf.add_paragraph()
    p3.text = sub
    p3.alignment = PP_ALIGN.CENTER
    p3.font.name = 'Calibri'
    p3.font.size = Pt(9.5)
    p3.font.color.rgb = C_SLATE

add_stat_box(s1, 1.0, 4.8, 3.4, 1.5, "421,570", "Historical Sales Records", "45 Stores × 81 Depts (143 Weeks)")
add_stat_box(s1, 4.9, 4.8, 3.4, 1.5, "60.0%", "WMAE Error Reduction", "$1,758.94 vs $4,393 Baseline")
add_stat_box(s1, 8.8, 4.8, 3.4, 1.5, "0.9725", "Coefficient of Determination", "R² Score on Unseen 49-Week Test")

add_notes(s1, 
"""[Target Time: 0:00 - 0:40]
SPEAKER SCRIPT:
"Good morning everyone and respected professor. My name is Dev Dilip Dhapodkar, PRN 24070521505. Today I am presenting my Predictive Analytics CA3 project on 'Sales Forecasting'.

In this project, I developed an end-to-end predictive machine learning model to forecast weekly department-level sales across 45 Walmart stores using historical sales, promotional markdowns, holiday calendar events, and macroeconomic indicators. 

Following the Knowledge Discovery in Databases (KDD) process, my final model achieved a 60% reduction in Weighted Mean Absolute Error and an R² of 0.9725. Let me walk you through the problem, the workflow, the models, and the key results."
""")

# ==============================================================================
# SLIDE 2: PROBLEM STATEMENT & KDD WORKFLOW (50 seconds)
# ==============================================================================
s2 = prs.slides.add_slide(blank_layout)
add_header(s2, "1. Problem Statement & KDD Workflow", "Addressing Asymmetric Supply Chain Costs Through Systematic Data Mining", 2)

# Left Column: The Problem & Asymmetric Risk
add_card(s2, 0.6, 1.25, 4.4, 2.7, "The Business Problem", [
    "• Scale: 45 Walmart stores, 81 departments (over 3,600 time series).",
    "• Volatility: Extreme sales surges during holidays (Thanksgiving, Christmas) and promotional markdown campaigns.",
    "• Goal: Accurately predict Weekly_Sales to optimize inventory replenishment."
], C_NAVY)

add_card(s2, 0.6, 4.15, 4.4, 2.75, "Asymmetric Supply Chain Cost", [
    "• Stockout Risk (Under-forecasting): Running out of stock during holiday peaks causes direct revenue loss and customer dissatisfaction. This is why the competition metric (WMAE) weights holiday errors 5x higher (w = 5).",
    "• Holding Cost (Over-forecasting): Overstocking incurs warehouse storage fees and forces post-season clearance markdowns."
], C_CORAL)

# Right Column: The 7 KDD Stages
add_card(s2, 5.3, 1.25, 7.4, 5.65, "End-to-End KDD Implementation Workflow", [
    "1. Data Ingestion: Merged 4 relational tables (train.csv, features.csv, stores.csv, test.csv) into 421,570 unified rows.",
    "2. Preprocessing: Structural zero-imputation for MarkDown1–5; store-grouped fill for CPI & Unemployment; floored 1,285 negative sales & treated outliers.",
    "3. Feature Engineering: Created 43 leak-free features (Lags 1–52, Rolling Means, Holiday flags, Fourier cyclical encodings).",
    "4. Exploratory Data Analysis: Quantified store size elasticity (r = 0.81), format hierarchy (Types A, B, C), and holiday revenue lifts.",
    "5. Model Training: Strict chronological split (2011-11-25); trained Baseline Ridge, Random Forest, XGBoost, and LightGBM with w=5 sample weights.",
    "6. Model Evaluation: Assessed out-of-sample performance via WMAE ($w=5$), RMSE, MAE, and R².",
    "7. Business Interpretation: Analyzed feature gain attribution and translated error reduction into $31.7M in inventory cost savings."
], C_BLUE)

add_notes(s2,
"""[Target Time: 0:40 - 1:30]
SPEAKER SCRIPT:
"In retail supply chains, forecast errors are asymmetric. If you under-forecast during a holiday like Thanksgiving, you face stockouts and lost revenue. If you over-forecast, you get hit with holding costs and clearance losses. That is why the evaluation metric for this competition—Weighted Mean Absolute Error (WMAE)—assigns five times more weight to holiday weeks.

To solve this, I structured the project around the systematic KDD process across seven stages: from ingesting 421,000 records, to cleaning markdowns and negative returns, engineering 43 leak-free predictive features, and benchmarking four distinct machine learning algorithms."
""")

# ==============================================================================
# SLIDE 3: DATA PREPROCESSING & OUTLIERS (50 seconds)
# ==============================================================================
s3 = prs.slides.add_slide(blank_layout)
add_header(s3, "2. Data Preprocessing: Missing MarkDowns & Outliers", "Cleaning 421,570 Records While Preserving Authentic Holiday Demand Spikes", 3)

# Place Figure 2 on the Left (width 8.2 inches)
s3.shapes.add_picture("figures/fig2_outlier_and_markdown_analysis.png", Inches(0.6), Inches(1.3), width=Inches(8.0))

# Right Column Takeaway Cards
add_card(s3, 8.8, 1.3, 3.9, 2.65, "MarkDown Imputation Strategy", [
    "• Pre-Nov 2011 Missingness: MarkDown1–5 have 64% to 74% missing values because Walmart only started tracking them in Nov 2011.",
    "• Treatment: Extracted binary Has_MarkDown and Active_MarkDown_Count flags, then imputed 0.0 (structural absence of promo).",
    "• CPI & Unemployment: Missing in late test weeks; imputed using store-level forward/backward fill."
], C_BLUE)

add_card(s3, 8.8, 4.15, 3.9, 2.8, "Negative Sales & Outlier Treatment", [
    "• Negative Returns (1,285 rows): 0.3% of sales were negative due to customer returns and accounting credits. Floored at $0.00.",
    "• Preserving Holiday Spikes: Standard IQR filtering would incorrectly delete genuine Black Friday surges. Instead, we winsorized non-holiday upper-tail records (>99.95th percentile, $183K) while keeping holiday records intact."
], C_TEAL)

add_notes(s3,
"""[Target Time: 1:30 - 2:20]
SPEAKER SCRIPT:
"Moving to Data Preprocessing. We faced two major data challenges shown in Figure 2:
First, promotional markdowns (MarkDown1 through 5) had 64% to 74% missing values. This wasn't random missing data—Walmart only introduced tracking in late 2011, and markdowns only occur during promotions. Before imputing with zero, we created indicator features like 'Has_MarkDown' and 'Active_MarkDown_Count' so the model knows when a promotion was active.

Second, 1,285 records had negative sales due to customer returns, which we floored at zero. For outliers, we carefully distinguished between anomalous errors and real holiday spikes. We capped non-holiday outliers at the 99.95th percentile while preserving authentic holiday sales peaks."
""")

# ==============================================================================
# SLIDE 4: FEATURE ENGINEERING & EDA (50 seconds)
# ==============================================================================
s4 = prs.slides.add_slide(blank_layout)
add_header(s4, "3. Feature Engineering: 43 Leak-Free Predictors", "Multi-Horizon Autoregression, Rolling Trends, Holiday Flags & Cyclical Fourier Transforms", 4)

# Place Figure 4 (Correlation Matrix) on the Left
s4.shapes.add_picture("figures/fig4_correlation_matrix.png", Inches(0.6), Inches(1.25), width=Inches(5.7))

# Right Column: Feature Families Breakdown
add_card(s4, 6.5, 1.25, 6.2, 2.7, "Feature Families Constructed", [
    "1. Autoregressive Lags: Lag_1 (t-1 wk, r = 0.95), Lag_2 (bi-weekly), Lag_4 (monthly, r = 0.94), and Lag_52 (year-over-year seasonal anchor, r = 0.97).",
    "2. Leak-Free Rolling Windows: Shifted by t-1 to prevent target leakage: Rolling_Mean_4, Rolling_Std_4, Rolling_Mean_12, and Momentum_1_4.",
    "3. Specific Holiday Events: Binary flags for Super Bowl (W6), Labor Day (W36), Thanksgiving (W47, +44% sales lift), Christmas (W52), and Pre-Christmas Peak (W49–51, +40% sales lift).",
    "4. Fourier Cyclical Encodings: sin/cos transforms of Week and Month to capture continuous seasonal cycles."
], C_NAVY)

add_card(s4, 6.5, 4.15, 6.2, 2.75, "Correlation Insights (Figure at Left)", [
    "• Strongest Drivers: Lag_52 (r = 0.97), Rolling_Mean_4 (r = 0.96), and Lag_1 (r = 0.95) have the highest linear correlation with Weekly_Sales.",
    "• Store Structure: Store physical size strongly correlates with sales (r = 0.81) across Type A Supercenters ($1.45M/wk), Type B Discount ($0.79M/wk), and Type C Neighborhood ($0.46M/wk).",
    "• No Look-Ahead Bias: Historical store-dept target statistics were computed strictly on the training partition."
], C_BLUE)

add_notes(s4,
"""[Target Time: 2:20 - 3:10]
SPEAKER SCRIPT:
"In Step 3, feature engineering is where predictive power is won or lost. We engineered 43 domain-specific features across four categories:
1. Autoregressive lags: Lag 1, 2, 4, and most importantly Lag 52, which captures exact year-over-year seasonality.
2. Leak-free rolling statistics: 4-week and 12-week moving averages, strictly shifted by one week so no future data leaks into the model.
3. Explicit holiday flags: Not just a generic 'is holiday' flag, but specific indicators for Thanksgiving (which delivers a +44% revenue surge), Pre-Christmas peak, Super Bowl, and Labor Day.
4. Cyclical Fourier sine and cosine features to handle circular calendar seasonality.

As shown in the correlation matrix on the left, Lag 52 (r = 0.97) and Rolling Mean 4 (r = 0.96) show the highest correlation with sales."
""")

# ==============================================================================
# SLIDE 5: MODEL TRAINING & EVALUATION (1 minute)
# ==============================================================================
s5 = prs.slides.add_slide(blank_layout)
add_header(s5, "4. Model Benchmarking & Evaluation (WMAE, RMSE, R²)", "Evaluating on 145,237 Unseen Dept-Weeks Across All 4 Holiday Events", 5)

# Place Figure 5 on Top
s5.shapes.add_picture("figures/fig5_model_comparison.png", Inches(0.6), Inches(1.2), width=Inches(12.133))

# Compact Results Table on Bottom
table_data = [
    ["Model Architecture", "WMAE (USD) ↓", "RMSE (USD) ↓", "MAE (USD) ↓", "R² Score ↑", "Holiday MAE (w=5) ↓", "Regular MAE (w=1) ↓", "Train Time"],
    ["Baseline (Ridge Regression)", "$4,393.17", "$6,616.57", "$2,514.98", "0.9183", "$10,108.52", "$1,835.29", "0.20 s"],
    ["Random Forest Regressor", "$1,791.54", "$4,413.86", "$1,520.75", "0.9637", "$2,615.57", "$1,422.75", "42.88 s"],
    ["XGBoost Regressor", "$1,837.57", "$4,306.19", "$1,523.89", "0.9654", "$2,792.11", "$1,410.37", "6.31 s"],
    ["LightGBM Regressor (Winner)", "$1,758.94", "$3,837.62", "$1,541.31", "0.9725", "$2,421.19", "$1,462.55", "4.91 s"]
]

# Create table
R = len(table_data)
C = len(table_data[0])
tbl_shape = s5.shapes.add_table(R, C, Inches(0.6), Inches(4.55), Inches(12.133), Inches(2.3))
tbl = tbl_shape.table
col_w = [2.4, 1.4, 1.4, 1.3, 1.1, 1.7, 1.6, 1.233]
for idx, w in enumerate(col_w):
    tbl.columns[idx].width = Inches(w)

for r in range(R):
    for c in range(C):
        cell = tbl.cell(r, c)
        cell.text = str(table_data[r][c])
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        cell.fill.solid()
        if r == 0:
            cell.fill.fore_color.rgb = C_NAVY
        elif r == 4:  # Highlight winner
            cell.fill.fore_color.rgb = RGBColor(236, 253, 245)
        elif r % 2 == 1:
            cell.fill.fore_color.rgb = RGBColor(248, 250, 252)
        else:
            cell.fill.fore_color.rgb = C_WHITE
        for p in cell.text_frame.paragraphs:
            p.alignment = PP_ALIGN.CENTER if c > 0 else PP_ALIGN.LEFT
            p.font.name = 'Calibri'
            p.font.size = Pt(10.5 if r > 0 else 11)
            p.font.bold = (r == 0 or r == 4 or c == 0)
            p.font.color.rgb = C_WHITE if r == 0 else (C_TEAL if r == 4 else C_DARK)

add_notes(s5,
"""[Target Time: 3:10 - 4:15]
SPEAKER SCRIPT:
"Now looking at Model Training and Evaluation. We partitioned the data chronologically at November 25, 2011. This gave us 263,000 training records and an out-of-sample validation set of 145,000 records spanning 49 weeks and covering all four major holidays.

We trained four models with sample weights of w = 5 on holiday weeks:
1. Baseline Ridge Regression
2. Random Forest Regressor
3. XGBoost Regressor
4. LightGBM Regressor

Here are the key takeaways:
- LightGBM was the clear winner: It achieved the lowest WMAE of $1,758.94—a 60% error reduction over the baseline—the lowest RMSE of $3,837, and the highest R² of 0.9725, training in just 4.9 seconds!
- Look at the Holiday MAE column: Ridge regression failed completely during holidays, with an error of over $10,000 per department-week. LightGBM cut holiday error by 76% down to $2,421.
- For regular non-holiday weeks, XGBoost was slightly better at $1,410 MAE, making both gradient-boosted models exceptionally strong."
""")

# ==============================================================================
# SLIDE 6: ACTUAL VS PREDICTED FORECAST TRACKING (45 seconds)
# ==============================================================================
s6 = prs.slides.add_slide(blank_layout)
add_header(s6, "5. Validation Forecast Tracking & Parity Analysis", "Visual Proof: Tracking the 49-Week Validation Horizon and Holiday Surges", 6)

# Place Figure 6 (Actual vs Predicted)
s6.shapes.add_picture("figures/fig6_actual_vs_predicted.png", Inches(0.6), Inches(1.25), width=Inches(12.133))

add_card(s6, 0.6, 5.3, 12.133, 1.65, "What the Forecast Tracking Proves", [
    "• Holiday Peak Tracking (Panel A): Black line is actual sales; dashed red is XGBoost and blue is LightGBM. Both track the $77M Thanksgiving and Christmas surges tightly, whereas the grey dotted Baseline overshoots dramatically.",
    "• Tight Parity Line (Panel B): Out of 145,237 predictions, points hug the 45-degree ideal parity line (y = x) with R² = 0.965 to 0.972, proving robust generalization across all 45 stores."
], C_NAVY)

add_notes(s6,
"""[Target Time: 4:15 - 5:00]
SPEAKER SCRIPT:
"Figure 6 provides visual confirmation of our validation results.
In Panel A on the left, the black line represents actual aggregate weekly sales across the 49-week validation horizon. The yellow circles mark holiday weeks. 
Notice how the grey dotted line—the linear baseline—completely overshoots immediately after Thanksgiving and Christmas. In contrast, LightGBM (blue) and XGBoost (red) track the peaks and post-holiday dips with high precision.

In Panel B on the right, you can see the predicted vs actual scatter plot on 8,000 sampled validation points. The points align tightly along the red 45-degree parity line, confirming consistent accuracy across both low-volume and high-volume departments."
""")

# ==============================================================================
# SLIDE 7: FEATURE IMPORTANCE, BUSINESS SAVINGS & CONCLUSION (1 minute)
# ==============================================================================
s7 = prs.slides.add_slide(blank_layout)
add_header(s7, "6. Feature Importance, Supply Chain Impact & Conclusion", "Translating Model Accuracy into $31.7M in Inventory Cost Savings Across 45 Stores", 7)

# Place Figure 8 (Supply Chain Impact) on the Left
s7.shapes.add_picture("figures/fig8_supply_chain_impact.png", Inches(0.6), Inches(1.25), width=Inches(6.8))

# Right Column: Top Features & Business Takeaways
add_card(s7, 7.6, 1.25, 5.1, 2.7, "Top Predictive Drivers (Gain %)", [
    "• Lag_52 (Annual Seasonality): #1 feature in both LightGBM (40.9%) and XGBoost (31.5%). Sales exactly 1 year ago anchor demand.",
    "• Rolling_Mean_4 & Lag_1: Combine for 38% to 40% gain, adapting forecasts to short-term store traffic.",
    "• Holiday Flags: Is_Thanksgiving & Pre_Christmas_Peak provide 9.4% gain in XGBoost, preventing holiday stockouts."
], C_NAVY)

add_card(s7, 7.6, 4.15, 5.1, 2.75, "Supply Chain ROI & Conclusion", [
    "• 76% Holiday Error Reduction: Cuts peak stockouts during Black Friday & Christmas when stockouts hurt most.",
    "• $31.7M Cost Savings (-39.5%): Under an industry 22% mismatch penalty, forecast improvements save $17.1M in Supercenters (Type A), $12.8M in Discount (Type B), and $1.8M in Neighborhood Mkts (Type C).",
    "• Conclusion: LightGBM is recommended for Q4 holiday pre-staging and XGBoost for routine weekly replenishment."
], C_TEAL)

add_notes(s7,
"""[Target Time: 5:00 - 6:00]
SPEAKER SCRIPT:
"Finally, let's connect model accuracy to business impact:
1. Feature Importance: The single most important feature was Lag 52 (sales from the same week last year), accounting for 41% of LightGBM's gain. Short-term rolling means and explicit holiday flags accounted for the rest.
2. Supply Chain Impact: As shown in Figure 8 Panel B, applying a standard 22% inventory holding and stockout penalty factor across the 49-week horizon, moving from the baseline to gradient boosting reduces inventory mismatch costs from $80.3M down to $48.6M. That is an estimated savings of $31.7 million dollars—or a 39.5% cost reduction across all 45 stores.

To conclude:
We implemented an end-to-end KDD pipeline for Sales Forecasting. Our gradient-boosted models cut WMAE by 60% and explained 97.25% of sales variance. For deployment, we recommend LightGBM for high-stakes holiday pre-staging and XGBoost for routine weekly automated replenishment.

Thank you for your time, and I am happy to answer any questions."
""")

# Save simple deck
output_path = "Walmart_Sales_Forecasting_Simple_Presentation.pptx"
prs.save(output_path)
print(f"Successfully generated {output_path} (7 slides)!")

# Also overwrite Walmart_Sales_Forecasting_Presentation.pptx so the main repo deck is immediately the 7-slide simple version!
prs.save("Walmart_Sales_Forecasting_Presentation.pptx")
print("Also updated Walmart_Sales_Forecasting_Presentation.pptx to the simple 7-slide deck!")
