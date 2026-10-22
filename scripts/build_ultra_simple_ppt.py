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

# High-contrast, clean colors
C_NAVY = RGBColor(15, 41, 66)       # Walmart deep navy
C_BLUE = RGBColor(0, 113, 206)      # Walmart blue
C_YELLOW = RGBColor(255, 194, 32)   # Spark yellow
C_GREEN = RGBColor(16, 185, 129)    # Emerald green
C_CORAL = RGBColor(225, 29, 72)
C_TEAL = RGBColor(13, 148, 136)     # Vivid red
C_DARK = RGBColor(30, 41, 59)       # Body text
C_SLATE = RGBColor(100, 116, 139)   # Subdued text
C_CARD_BG = RGBColor(248, 250, 252) # Light card fill
C_CARD_BORDER = RGBColor(226, 232, 240)
C_WHITE = RGBColor(255, 255, 255)

def add_header(slide, title, subtitle, slide_num, total_slides=7):
    # Base background
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = C_WHITE
    bg.line.fill.background()

    # Top Navy Banner
    banner = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.05))
    banner.fill.solid()
    banner.fill.fore_color.rgb = C_NAVY
    banner.line.fill.background()

    # Yellow Accent Line
    accent = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(1.05), Inches(13.333), Inches(0.06))
    accent.fill.solid()
    accent.fill.fore_color.rgb = C_YELLOW
    accent.line.fill.background()

    # Header Text
    tb = slide.shapes.add_textbox(Inches(0.65), Inches(0.12), Inches(11.0), Inches(0.85))
    tf = tb.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = title
    p1.font.name = 'Calibri'
    p1.font.size = Pt(23)
    p1.font.bold = True
    p1.font.color.rgb = C_WHITE

    p2 = tf.add_paragraph()
    p2.text = subtitle
    p2.font.name = 'Calibri'
    p2.font.size = Pt(12)
    p2.font.color.rgb = RGBColor(186, 230, 253)

    # Footer
    ft = slide.shapes.add_textbox(Inches(0.65), Inches(7.12), Inches(12.0), Inches(0.3))
    fp = ft.text_frame.paragraphs[0]
    fp.text = f"Dev Dilip Dhapodkar (PRN: 24070521505)  |  Predictive Analytics CA3: Sales Forecasting                                                  Slide {slide_num} of {total_slides}"
    fp.font.name = 'Calibri'
    fp.font.size = Pt(9.5)
    fp.font.color.rgb = C_SLATE

def add_notes(slide, text):
    notes = slide.notes_slide
    notes.notes_text_frame.text = text

def add_takeaway_card(slide, left, top, width, height, title, text_items, header_color=C_BLUE):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    card.adjustments[0] = 0.04
    card.fill.solid()
    card.fill.fore_color.rgb = C_CARD_BG
    card.line.color.rgb = C_CARD_BORDER
    card.line.width = Pt(1)

    # Header tab
    hdr = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(0.44))
    hdr.adjustments[0] = 0.08
    hdr.fill.solid()
    hdr.fill.fore_color.rgb = header_color
    hdr.line.fill.background()

    htb = slide.shapes.add_textbox(Inches(left + 0.15), Inches(top + 0.05), Inches(width - 0.3), Inches(0.35))
    hp = htb.text_frame.paragraphs[0]
    hp.text = title
    hp.font.name = 'Calibri'
    hp.font.size = Pt(13)
    hp.font.bold = True
    hp.font.color.rgb = C_WHITE

    btb = slide.shapes.add_textbox(Inches(left + 0.2), Inches(top + 0.52), Inches(width - 0.4), Inches(height - 0.6))
    btf = btb.text_frame
    btf.word_wrap = True
    for i, item in enumerate(text_items):
        p = btf.paragraphs[0] if i == 0 else btf.add_paragraph()
        p.text = item
        p.font.name = 'Calibri'
        p.font.size = Pt(12)
        p.font.color.rgb = C_DARK
        p.space_after = Pt(6)

# ==============================================================================
# SLIDE 1: ULTRA-CLEAN TITLE SLIDE
# ==============================================================================
s1 = prs.slides.add_slide(blank_layout)
bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
bg1.fill.solid()
bg1.fill.fore_color.rgb = C_NAVY
bg1.line.fill.background()

strip1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(0.4), Inches(7.5))
strip1.fill.solid()
strip1.fill.fore_color.rgb = C_YELLOW
strip1.line.fill.background()

tb1 = s1.shapes.add_textbox(Inches(1.1), Inches(1.1), Inches(11.2), Inches(3.4))
tf1 = tb1.text_frame
tf1.word_wrap = True

p = tf1.paragraphs[0]
p.text = "PREDICTIVE ANALYTICS — CA3 PRESENTATION"
p.font.name = 'Calibri'
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = C_YELLOW
p.space_after = Pt(12)

p = tf1.add_paragraph()
p.text = "Sales Forecasting"
p.font.name = 'Calibri'
p.font.size = Pt(44)
p.font.bold = True
p.font.color.rgb = C_WHITE
p.space_after = Pt(8)

p = tf1.add_paragraph()
p.text = "End-to-End Retail Store Sales Forecasting & Supply Chain Optimization"
p.font.name = 'Calibri'
p.font.size = Pt(19)
p.font.color.rgb = RGBColor(186, 230, 253)
p.space_after = Pt(20)

p = tf1.add_paragraph()
p.text = "Presented by: Dev Dilip Dhapodkar   |   PRN: 24070521505"
p.font.name = 'Calibri'
p.font.size = Pt(17)
p.font.bold = True
p.font.color.rgb = C_YELLOW

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
    p1.font.size = Pt(26)
    p1.font.bold = True
    p1.font.color.rgb = C_BLUE
    p2 = tf.add_paragraph()
    p2.text = label
    p2.alignment = PP_ALIGN.CENTER
    p2.font.name = 'Calibri'
    p2.font.size = Pt(12)
    p2.font.bold = True
    p2.font.color.rgb = C_NAVY
    p3 = tf.add_paragraph()
    p3.text = sub
    p3.alignment = PP_ALIGN.CENTER
    p3.font.name = 'Calibri'
    p3.font.size = Pt(10)
    p3.font.color.rgb = C_SLATE

add_stat_box(s1, 1.1, 4.85, 3.4, 1.6, "421,570", "Walmart Sales Records", "45 Stores × 81 Departments")
add_stat_box(s1, 5.0, 4.85, 3.4, 1.6, "-60.0%", "WMAE Error Reduction", "$1,759 vs $4,393 Baseline")
add_stat_box(s1, 8.9, 4.85, 3.4, 1.6, "R² = 0.9725", "Variance Explained", "$31.7M Supply Chain Savings")

add_notes(s1,
"""[Time: 0:00 - 0:35]
SPEAKER SCRIPT:
"Good morning, Professor. My name is Dev Dilip Dhapodkar, PRN 24070521505. Today, I am presenting my Predictive Analytics CA3 project on 'Sales Forecasting'.

Using the official Kaggle Walmart dataset of over 421,000 records across 45 stores, I developed an end-to-end machine learning pipeline that forecasts weekly sales, reduces forecast error by 60%, and achieves an R² of 0.9725 to optimize retail supply chain inventory."
""")

# ==============================================================================
# SLIDE 2: THE BUSINESS PROBLEM & HOLIDAY SURGES
# ==============================================================================
s2 = prs.slides.add_slide(blank_layout)
add_header(s2, "1. The Challenge: Massive Recurring Holiday Surges", "Why Retail Forecasting Is Critical for Supply Chain Inventory Planning", 2)

# Prominent Chart on Left
s2.shapes.add_picture("slide_charts/chart1_sales_spikes.png", Inches(0.65), Inches(1.35), width=Inches(7.8))

# Right Column: 2 Clear Cards
add_takeaway_card(s2, 8.7, 1.35, 4.0, 2.7, "The Supply Chain Dilemma", [
    "• Thanksgiving (+44%): Sales surge to $66.6M in a single week due to Black Friday demand.",
    "• Pre-Christmas (+40%): Surges to $80.9M, followed by an immediate sharp drop.",
    "• Asymmetric Risk: Stockouts during holidays lose customers forever. Over-stocking causes costly markdowns."
], C_CORAL)

add_takeaway_card(s2, 8.7, 4.25, 4.0, 2.65, "The Evaluation Metric (WMAE)", [
    "• Weighted Mean Absolute Error (WMAE):",
    "• Holiday Weeks have 5x weight (w = 5).",
    "• Regular Weeks have 1x weight (w = 1).",
    "• Models must prioritize holiday accuracy above all else to optimize inventory."
], C_NAVY)

add_notes(s2,
"""[Time: 0:35 - 1:25]
SPEAKER SCRIPT:
"Looking at Slide 2: Figure 1 plots total weekly sales across all 45 Walmart stores over nearly three years. 
Notice the two massive red and orange spikes every November and December:
- On Thanksgiving and Black Friday, weekly sales surge by +44% to over $66 million.
- During the pre-Christmas rush, sales spike by +40% to over $80 million, followed by an immediate collapse once stores close.

For supply chain managers, under-forecasting during holidays causes severe out-of-stock penalties. That is why our competition metric—Weighted Mean Absolute Error (WMAE)—weights holiday errors five times heavier than normal weeks."
""")

# ==============================================================================
# SLIDE 3: DATA PREPROCESSING & OUTLIER TREATMENT
# ==============================================================================
s3 = prs.slides.add_slide(blank_layout)
add_header(s3, "2. Data Preprocessing: MarkDowns & Outlier Treatment", "Handling Missing Promotional Records and Anomaly Returns Without Biasing Holiday Spikes", 3)

s3.shapes.add_picture("slide_charts/chart_preprocessing_simple.png", Inches(0.65), Inches(1.35), width=Inches(7.8))

add_takeaway_card(s3, 8.7, 1.35, 4.0, 2.7, "1. MarkDown Imputation", [
    "• 64%–74% Missing: MarkDown1–5 only started being tracked in November 2011.",
    "• Solution: Extracted binary 'Has_MarkDown' and count indicators before imputing 0.0.",
    "• Result: The model knows whether a promotion was active or inactive."
], C_BLUE)

add_takeaway_card(s3, 8.7, 4.25, 4.0, 2.65, "2. Returns & Outliers", [
    "• Negative Returns (1,285 rows): Customer returns caused negative sales. Floored at $0.00.",
    "• Preserving Holidays: Standard outlier removal would delete genuine Black Friday spikes. We capped non-holiday outliers at $183K while keeping holiday spikes intact."
], C_TEAL)

add_notes(s3,
"""[Time: 1:25 - 2:15]
SPEAKER SCRIPT:
"Next, in Data Preprocessing, we tackled two critical real-world issues shown on the chart:
First, promotional markdowns (MarkDown1 through 5) had 64% to 74% missing values. This is because markdowns were only introduced in late 2011. Instead of naive imputation, we created an active promotional flag and then imputed zeros, giving the model clear promo signals.

Second, 1,285 records showed negative sales due to customer returns, which we floored at zero. For outliers, we carefully winsorized only non-holiday anomalies at the 99.95th percentile, ensuring real holiday demand surges were never accidentally erased."
""")

# ==============================================================================
# SLIDE 4: FEATURE ENGINEERING (TOP PREDICTORS)
# ==============================================================================
s4 = prs.slides.add_slide(blank_layout)
add_header(s4, "3. Feature Engineering: The 43 Predictive Features", "How Autoregressive Lags and Calendar Signals Power Accurate Forecasts", 4)

s4.shapes.add_picture("slide_charts/chart2_top_features.png", Inches(0.65), Inches(1.35), width=Inches(7.8))

add_takeaway_card(s4, 8.7, 1.35, 4.0, 2.7, "Top Predictive Drivers", [
    "• #1: Sales 1 Year Ago (Lag 52): Contributes 40.9% of model gain! Department sales from the exact same week last year anchor seasonality.",
    "• #2 & #3: Recent Trends (Lag 1 & 4-Wk Avg): Combine for 40% of gain, capturing recent momentum and store traffic.",
    "• #4: Holiday Flags: Thanksgiving (+44%) and Christmas flags prevent holiday under-forecasting."
], C_NAVY)

add_takeaway_card(s4, 8.7, 4.25, 4.0, 2.65, "Zero Data Leakage", [
    "• Rolling Windows Shifted: All rolling statistics were computed on t-1 shifted data so no future sales leak into the model.",
    "• Strict Split: Historical store target baselines were calculated exclusively on the training set prior to November 2011."
], C_BLUE)

add_notes(s4,
"""[Time: 2:15 - 3:05]
SPEAKER SCRIPT:
"In Step 3, we engineered 43 domain-specific features. As the chart on the left illustrates:
1. The single most powerful feature is 'Lag 52'—sales from the exact same week one year ago—which accounts for 41% of total model gain! Retail demand is intensely seasonal, so last year's sales provide the baseline.
2. The next 40% of gain comes from short-term momentum: prior week sales (Lag 1) and the recent 4-week moving average.
3. Specific holiday flags like Thanksgiving provide the final non-linear boost during Q4.

Crucially, all rolling averages were strictly shifted by one week to eliminate any look-ahead bias or data leakage."
""")

# ==============================================================================
# SLIDE 5: MODEL BENCHMARKING (LIGHTGBM WINNER)
# ==============================================================================
s5 = prs.slides.add_slide(blank_layout)
add_header(s5, "4. Model Benchmarking: LightGBM Crushes Baseline", "Evaluating on 145,237 Out-of-Sample Validation Records (49 Full Weeks)", 5)

s5.shapes.add_picture("slide_charts/chart3_model_wmae.png", Inches(0.65), Inches(1.35), width=Inches(7.8))

add_takeaway_card(s5, 8.7, 1.35, 4.0, 2.7, "Performance Comparison", [
    "• Baseline (Ridge): WMAE $4,393 (Linear model overshoots heavily during holidays).",
    "• Random Forest: WMAE $1,792 (-59%).",
    "• XGBoost: WMAE $1,838 (-58%).",
    "• LightGBM: WMAE $1,759 (-60% Error Reduction, Winner!)."
], C_GREEN)

add_takeaway_card(s5, 8.7, 4.25, 4.0, 2.65, "Why LightGBM Won", [
    "• Holiday Error Slashed by 76%: Holiday MAE dropped from $10,108 down to $2,421.",
    "• Superior Fit: R² = 0.9725 (explains 97.25% of variance across 81 departments).",
    "• Lightning Fast: Trained 600 trees on 263,000 records in just 4.9 seconds!"
], C_NAVY)

add_notes(s5,
"""[Time: 3:05 - 4:00]
SPEAKER SCRIPT:
"Now looking at Model Benchmarking on Slide 5. We evaluated four algorithms on an unseen 49-week validation horizon containing 145,000 department-week records.

As the bar chart shows:
- The linear Baseline Ridge model struggled, with a WMAE of $4,393 and a catastrophic holiday error of over $10,000 per department. Linear models simply cannot handle non-linear holiday spikes.
- Tree ensembles dramatically improved accuracy:
- Random Forest achieved $1,792.
- XGBoost achieved $1,838.
- LightGBM was the overall winner, achieving the lowest WMAE of $1,759—a 60% error reduction—and an R² of 0.9725, while training in under 5 seconds!"
""")

# ==============================================================================
# SLIDE 6: ACTUAL VS PREDICTED FORECAST TRACKING
# ==============================================================================
s6 = prs.slides.add_slide(blank_layout)
add_header(s6, "5. Forecast Tracking: Predictions Hug Real Sales", "Out-of-Sample Tracking of Aggregate Weekly Revenue and Holiday Peaks", 6)

s6.shapes.add_picture("slide_charts/chart4_actual_vs_pred.png", Inches(0.65), Inches(1.35), width=Inches(7.8))

add_takeaway_card(s6, 8.7, 1.35, 4.0, 2.7, "Tight Peak Tracking", [
    "• Black Line = Actual Sales ($M).",
    "• Dashed Green Line = LightGBM Forecast.",
    "• Both lines overlap almost perfectly throughout the 49-week horizon, accurately capturing the $77M Black Friday peak."
], C_NAVY)

add_takeaway_card(s6, 8.7, 4.25, 4.0, 2.65, "Robust Generalization", [
    "• Handles Post-Holiday Drops: Unlike linear models that lag behind, LightGBM immediately adapts to January post-holiday sales drops.",
    "• Department-Level Precision: Generalizes reliably across small neighborhood stores and massive supercenters."
], C_BLUE)

add_notes(s6,
"""[Time: 4:00 - 4:50]
SPEAKER SCRIPT:
"Slide 6 shows the actual proof of model performance:
The black solid line is actual weekly sales across the 45 stores; the dashed green line is our LightGBM forecast.

Notice how the green forecast hugs the black line through every seasonal dip and rises smoothly to capture the massive 77-million-dollar holiday peak. More importantly, it immediately adjusts downwards right after the holidays, preventing overstocking in January."
""")

# ==============================================================================
# SLIDE 7: BUSINESS IMPACT & CONCLUSION
# ==============================================================================
s7 = prs.slides.add_slide(blank_layout)
add_header(s7, "6. Supply Chain Business Impact & Conclusion", "Translating 60% Forecast Error Reduction into $31.7M in Real Cost Savings", 7)

s7.shapes.add_picture("slide_charts/chart5_cost_savings.png", Inches(0.65), Inches(1.35), width=Inches(7.8))

add_takeaway_card(s7, 8.7, 1.35, 4.0, 2.7, "Quantified Savings ($31.7M)", [
    "• Total Cost Dropped by 39%: Under a standard 22% holding + stockout penalty factor, mismatch costs drop from $80.3M to $48.6M.",
    "• Supercenters (Type A): Save $17.1M (-37%).",
    "• Discount Stores (Type B): Save $12.8M (-43%).",
    "• Neighborhood Mkts (Type C): Save $1.8M (-44%)."
], C_GREEN)

add_takeaway_card(s7, 8.7, 4.25, 4.0, 2.65, "Key Takeaway", [
    "• LightGBM delivers production-grade sales forecasts (WMAE $1,759, R² = 0.9725).",
    "• Directly eliminates stockouts on high-margin Black Friday and Christmas holiday periods.",
    "• Ready for automated supply chain replenishment deployment."
], C_NAVY)

add_notes(s7,
"""[Time: 4:50 - 5:45]
SPEAKER SCRIPT:
"Finally, on Slide 7, we translate statistical accuracy into business dollars:
In retail supply chain management, forecast errors mean paying for excess safety stock or losing margins due to empty shelves. Applying an industry-standard 22% penalty factor:
- Total inventory mismatch cost is slashed from $80.3 million down to $48.6 million.
- That is a direct savings of $31.7 million—or 39%—across all 45 Walmart stores ($17M saved in Supercenters and $13M in Discount stores).

In conclusion:
Following the KDD process, we engineered 43 features and built a LightGBM model that cuts error by 60%, explains 97.25% of sales variance, and protects holiday revenue.

Thank you very much. I am now open to your questions."
""")

# Save both presentation files
prs.save("Walmart_Sales_Forecasting_Simple_Presentation.pptx")
prs.save("Walmart_Sales_Forecasting_Presentation.pptx")
print("Ultra-simple presentation saved successfully to both filenames!")
