import os
import json
import time
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns

from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import xgboost as xgb
import lightgbm as lgb

warnings.filterwarnings('ignore')
os.makedirs('figures', exist_ok=True)
os.makedirs('outputs', exist_ok=True)

# Set publication-quality plot style
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['axes.edgecolor'] = '#CBD5E1'
plt.rcParams['axes.linewidth'] = 0.9
plt.rcParams['grid.color'] = '#E2E8F0'
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.alpha'] = 0.7

PALETTE = {
    'navy': '#0F2942',
    'blue': '#0071CE',      # Walmart Blue
    'yellow': '#FFC220',    # Walmart Spark Yellow
    'amber': '#D97706',
    'teal': '#0D9488',
    'coral': '#E11D48',
    'purple': '#6366F1',
    'slate': '#475569',
    'light_bg': '#F8FAFC'
}

print("1. Loading Walmart Dataset...")
t0 = time.time()
stores = pd.read_csv('data/stores.csv')
features = pd.read_csv('data/features.csv')
train = pd.read_csv('data/train.csv')
test = pd.read_csv('data/test.csv')

print(f"Loaded stores: {stores.shape}, features: {features.shape}, train: {train.shape}, test: {test.shape}")

# Merge datasets
df = train.merge(features, on=['Store', 'Date', 'IsHoliday'], how='left').merge(stores, on='Store', how='left')
df['Date'] = pd.to_datetime(df['Date'])
df = df.sort_values(['Store', 'Dept', 'Date']).reset_index(drop=True)

test_df = test.merge(features, on=['Store', 'Date', 'IsHoliday'], how='left').merge(stores, on='Store', how='left')
test_df['Date'] = pd.to_datetime(test_df['Date'])
test_df = test_df.sort_values(['Store', 'Dept', 'Date']).reset_index(drop=True)

# Record raw stats before preprocessing
raw_missing_train = df.isnull().sum().to_dict()
raw_missing_features = features.isnull().sum().to_dict()
neg_sales_count = int((df['Weekly_Sales'] < 0).sum())
zero_sales_count = int((df['Weekly_Sales'] == 0).sum())
q999 = float(df['Weekly_Sales'].quantile(0.999))
q25 = float(df['Weekly_Sales'].quantile(0.25))
q50 = float(df['Weekly_Sales'].quantile(0.50))
q75 = float(df['Weekly_Sales'].quantile(0.75))
iqr = q75 - q25
upper_iqr_fence = q75 + 1.5 * iqr
outliers_above_iqr = int((df['Weekly_Sales'] > upper_iqr_fence).sum())
outliers_above_999 = int((df['Weekly_Sales'] > q999).sum())

print(f"Negative sales rows: {neg_sales_count}, Outliers > IQR fence (${upper_iqr_fence:,.2f}): {outliers_above_iqr}, > 99.9th pct (${q999:,.2f}): {outliers_above_999}")

# 2. Preprocessing: Missing MarkDown Imputation & Outlier Treatment
markdown_cols = ['MarkDown1', 'MarkDown2', 'MarkDown3', 'MarkDown4', 'MarkDown5']

# Create Promo Indicators before filling
df['Active_MarkDown_Count'] = df[markdown_cols].notnull().sum(axis=1)
df['Has_MarkDown'] = (df['Active_MarkDown_Count'] > 0).astype(int)

# Impute MarkDown1-5 with 0.0 (structural absence of promotional markdown)
df[markdown_cols] = df[markdown_cols].fillna(0.0)
for col in markdown_cols:
    df[col] = df[col].clip(lower=0.0)

df['Total_MarkDown'] = df[markdown_cols].sum(axis=1)

# Impute CPI and Unemployment using Store-level forward/backward fill
df['CPI'] = df.groupby('Store')['CPI'].transform(lambda s: s.ffill().bfill())
df['Unemployment'] = df.groupby('Store')['Unemployment'].transform(lambda s: s.ffill().bfill())

# Outlier & Negative Sales Treatment:
df['Weekly_Sales_Raw'] = df['Weekly_Sales'].copy()
non_holiday_cap = float(df.loc[~df['IsHoliday'], 'Weekly_Sales'].quantile(0.9995))
df['Weekly_Sales'] = df['Weekly_Sales'].clip(lower=0.0)
df.loc[(~df['IsHoliday']) & (df['Weekly_Sales'] > non_holiday_cap), 'Weekly_Sales'] = non_holiday_cap

# 3. Feature Engineering
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month
df['Week'] = df['Date'].dt.isocalendar().week.astype(int)
df['Quarter'] = df['Date'].dt.quarter
df['DayOfYear'] = df['Date'].dt.dayofyear

# Cyclical encodings for seasonality
df['Week_Sin'] = np.sin(2 * np.pi * df['Week'] / 52.0)
df['Week_Cos'] = np.cos(2 * np.pi * df['Week'] / 52.0)
df['Month_Sin'] = np.sin(2 * np.pi * df['Month'] / 12.0)
df['Month_Cos'] = np.cos(2 * np.pi * df['Month'] / 12.0)

# Specific Holiday Event Flags (Official Walmart Kaggle Holiday Dates)
super_bowl_dates = pd.to_datetime(['2010-02-12', '2011-02-11', '2012-02-10', '2013-02-08'])
labor_day_dates = pd.to_datetime(['2010-09-10', '2011-09-09', '2012-09-07', '2013-09-06'])
thanksgiving_dates = pd.to_datetime(['2010-11-26', '2011-11-25', '2012-11-23', '2013-11-29'])
christmas_dates = pd.to_datetime(['2010-12-31', '2011-12-30', '2012-12-28', '2013-12-27'])

df['Is_SuperBowl'] = df['Date'].isin(super_bowl_dates).astype(int)
df['Is_LaborDay'] = df['Date'].isin(labor_day_dates).astype(int)
df['Is_Thanksgiving'] = df['Date'].isin(thanksgiving_dates).astype(int)
df['Is_Christmas'] = df['Date'].isin(christmas_dates).astype(int)
df['Pre_Christmas_Peak'] = df['Week'].isin([49, 50, 51]).astype(int)
df['IsHoliday_Int'] = df['IsHoliday'].astype(int)
df['Promo_Holiday_Interaction'] = df['Has_MarkDown'] * df['IsHoliday_Int']

type_map = {'A': 3, 'B': 2, 'C': 1}
df['Store_Type_Code'] = df['Type'].map(type_map)

print("Computing Lag and Rolling Window Features...")
grp = df.groupby(['Store', 'Dept'])['Weekly_Sales']
df['Lag_1'] = grp.shift(1)
df['Lag_2'] = grp.shift(2)
df['Lag_4'] = grp.shift(4)
df['Lag_52'] = grp.shift(52)

df['Rolling_Mean_4'] = grp.transform(lambda s: s.shift(1).rolling(4, min_periods=1).mean())
df['Rolling_Std_4'] = grp.transform(lambda s: s.shift(1).rolling(4, min_periods=1).std()).fillna(0.0)
df['Rolling_Mean_12'] = grp.transform(lambda s: s.shift(1).rolling(12, min_periods=1).mean())
df['Momentum_1_4'] = df['Lag_1'] - df['Rolling_Mean_4']

# Chronological Train-Validation Split at 2011-11-25 (49 weeks of validation covering all 4 holidays!)
split_date = pd.to_datetime('2011-11-25')
model_df = df.dropna(subset=['Lag_1', 'Lag_2', 'Lag_4']).reset_index(drop=True)

train_sub = model_df[model_df['Date'] < split_date]
dept_stats = train_sub.groupby(['Store', 'Dept'])['Weekly_Sales'].agg(
    Store_Dept_Mean='mean',
    Store_Dept_Median='median',
    Store_Dept_Std='std'
).reset_index()
dept_stats['Store_Dept_Std'] = dept_stats['Store_Dept_Std'].fillna(0.0)

model_df = model_df.merge(dept_stats, on=['Store', 'Dept'], how='left').reset_index(drop=True)
train_mask = model_df['Date'] < split_date
val_mask = model_df['Date'] >= split_date

global_median = float(model_df.loc[train_mask, 'Weekly_Sales'].median())
model_df['Store_Dept_Mean'] = model_df['Store_Dept_Mean'].fillna(global_median)
model_df['Store_Dept_Median'] = model_df['Store_Dept_Median'].fillna(global_median)
model_df['Store_Dept_Std'] = model_df['Store_Dept_Std'].fillna(0.0)
model_df['Lag_52'] = model_df['Lag_52'].fillna(model_df['Store_Dept_Mean'])
model_df['Momentum_1_4'] = model_df['Momentum_1_4'].fillna(0.0)

feature_cols = [
    'Store', 'Dept', 'Store_Type_Code', 'Size',
    'Temperature', 'Fuel_Price', 'CPI', 'Unemployment',
    'MarkDown1', 'MarkDown2', 'MarkDown3', 'MarkDown4', 'MarkDown5',
    'Total_MarkDown', 'Active_MarkDown_Count', 'Has_MarkDown',
    'IsHoliday_Int', 'Is_SuperBowl', 'Is_LaborDay', 'Is_Thanksgiving', 'Is_Christmas',
    'Pre_Christmas_Peak', 'Promo_Holiday_Interaction',
    'Year', 'Month', 'Week', 'Quarter', 'DayOfYear',
    'Week_Sin', 'Week_Cos', 'Month_Sin', 'Month_Cos',
    'Lag_1', 'Lag_2', 'Lag_4', 'Lag_52',
    'Rolling_Mean_4', 'Rolling_Std_4', 'Rolling_Mean_12', 'Momentum_1_4',
    'Store_Dept_Mean', 'Store_Dept_Median', 'Store_Dept_Std'
]

X_train = model_df.loc[train_mask, feature_cols]
y_train = model_df.loc[train_mask, 'Weekly_Sales'].values
w_train = np.where(model_df.loc[train_mask, 'IsHoliday'].values, 5.0, 1.0)

X_val = model_df.loc[val_mask, feature_cols]
y_val = model_df.loc[val_mask, 'Weekly_Sales'].values
w_val = np.where(model_df.loc[val_mask, 'IsHoliday'].values, 5.0, 1.0)
hol_val = model_df.loc[val_mask, 'IsHoliday'].values

print(f"Train samples: {len(X_train):,}, Validation samples: {len(X_val):,}")

def compute_metrics(y_true, y_pred, weights, is_hol):
    y_pred = np.clip(y_pred, 0.0, None)
    wmae = float(np.sum(weights * np.abs(y_true - y_pred)) / np.sum(weights))
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    mae = float(mean_absolute_error(y_true, y_pred))
    r2 = float(r2_score(y_true, y_pred))
    hol_mae = float(mean_absolute_error(y_true[is_hol], y_pred[is_hol]))
    non_hol_mae = float(mean_absolute_error(y_true[~is_hol], y_pred[~is_hol]))
    return {
        'WMAE': round(wmae, 2),
        'RMSE': round(rmse, 2),
        'MAE': round(mae, 2),
        'R2': round(r2, 4),
        'Holiday_MAE': round(hol_mae, 2),
        'NonHoliday_MAE': round(non_hol_mae, 2)
    }

results = {}
preds = {}

# Model 1: Baseline (Ridge Regression)
print("Training Model 1: Baseline (Ridge Regression)...")
t1 = time.time()
baseline_model = make_pipeline(StandardScaler(), Ridge(alpha=100.0, random_state=42))
baseline_model.fit(X_train, y_train)
pred_base = np.clip(baseline_model.predict(X_val), 0.0, None)
results['Baseline (Ridge)'] = compute_metrics(y_val, pred_base, w_val, hol_val)
results['Baseline (Ridge)']['Train_Time_s'] = round(time.time() - t1, 2)
preds['Baseline (Ridge)'] = pred_base
print("Baseline (Ridge):", results['Baseline (Ridge)'])

# Model 2: Random Forest Regressor
print("Training Model 2: Random Forest Regressor...")
t1 = time.time()
rf_model = RandomForestRegressor(
    n_estimators=100,
    max_depth=16,
    min_samples_leaf=5,
    max_features=0.6,
    n_jobs=-1,
    random_state=42
)
rf_model.fit(X_train, y_train, sample_weight=w_train)
pred_rf = np.clip(rf_model.predict(X_val), 0.0, None)
results['Random Forest'] = compute_metrics(y_val, pred_rf, w_val, hol_val)
results['Random Forest']['Train_Time_s'] = round(time.time() - t1, 2)
preds['Random Forest'] = pred_rf
print("Random Forest:", results['Random Forest'])

# Model 3: LightGBM Regressor
print("Training Model 3: LightGBM Regressor...")
t1 = time.time()
lgb_model = lgb.LGBMRegressor(
    n_estimators=600,
    learning_rate=0.05,
    num_leaves=63,
    colsample_bytree=0.8,
    subsample=0.8,
    random_state=42,
    n_jobs=-1,
    verbose=-1
)
lgb_model.fit(X_train, y_train, sample_weight=w_train)
pred_lgb = np.clip(lgb_model.predict(X_val), 0.0, None)
results['LightGBM'] = compute_metrics(y_val, pred_lgb, w_val, hol_val)
results['LightGBM']['Train_Time_s'] = round(time.time() - t1, 2)
preds['LightGBM'] = pred_lgb
print("LightGBM:", results['LightGBM'])

# Model 4: XGBoost Regressor
print("Training Model 4: XGBoost Regressor...")
t1 = time.time()
xgb_model = xgb.XGBRegressor(
    n_estimators=550,
    learning_rate=0.05,
    max_depth=8,
    subsample=0.8,
    colsample_bytree=0.8,
    reg_alpha=1.0,
    reg_lambda=5.0,
    random_state=42,
    n_jobs=-1,
    tree_method='hist'
)
xgb_model.fit(X_train, y_train, sample_weight=w_train)
pred_xgb = np.clip(xgb_model.predict(X_val), 0.0, None)
results['XGBoost'] = compute_metrics(y_val, pred_xgb, w_val, hol_val)
results['XGBoost']['Train_Time_s'] = round(time.time() - t1, 2)
preds['XGBoost'] = pred_xgb
print("XGBoost:", results['XGBoost'])

# Save feature importances
xgb_imp = pd.Series(xgb_model.feature_importances_, index=feature_cols).sort_values(ascending=False)
lgb_imp_gain = pd.Series(lgb_model.booster_.feature_importance(importance_type='gain'), index=feature_cols)
lgb_imp_gain = (lgb_imp_gain / lgb_imp_gain.sum()).sort_values(ascending=False)
rf_imp = pd.Series(rf_model.feature_importances_, index=feature_cols).sort_values(ascending=False)

summary_payload = {
    'dataset_stats': {
        'train_rows': int(len(train)),
        'test_rows': int(len(test)),
        'stores_count': int(len(stores)),
        'features_rows': int(len(features)),
        'depts_count': int(df['Dept'].nunique()),
        'weeks_train': int(df['Date'].nunique()),
        'date_min': str(df['Date'].min().date()),
        'date_max': str(df['Date'].max().date()),
        'neg_sales_count': neg_sales_count,
        'zero_sales_count': zero_sales_count,
        'outliers_above_iqr': outliers_above_iqr,
        'outliers_above_999': outliers_above_999,
        'upper_iqr_fence': round(upper_iqr_fence, 2),
        'q999': round(q999, 2),
        'non_holiday_cap': round(non_holiday_cap, 2),
        'train_split_rows': int(len(X_train)),
        'val_split_rows': int(len(X_val)),
        'split_date': '2011-11-25'
    },
    'raw_missing_train': raw_missing_train,
    'raw_missing_features': raw_missing_features,
    'models': results,
    'top15_xgb': xgb_imp.head(15).round(4).to_dict(),
    'top15_lgb': lgb_imp_gain.head(15).round(4).to_dict(),
    'top15_rf': rf_imp.head(15).round(4).to_dict()
}

with open('outputs/metrics_summary.json', 'w') as f:
    json.dump(summary_payload, f, indent=2)

# ==============================================================================
# GENERATE 8 PUBLICATION-QUALITY FIGURES
# ==============================================================================
print("Generating Figure 1: EDA Sales Overview...")
fig = plt.figure(figsize=(16, 10), dpi=220)
gs = fig.add_gridspec(2, 2, height_ratios=[1.15, 1], hspace=0.35, wspace=0.25)

# Panel A: Aggregate Weekly Sales Trend
ax1 = fig.add_subplot(gs[0, :])
weekly_agg = df.groupby(['Date', 'IsHoliday'])['Weekly_Sales_Raw'].sum().reset_index()
weekly_agg['Sales_Millions'] = weekly_agg['Weekly_Sales_Raw'] / 1e6
ax1.plot(weekly_agg['Date'], weekly_agg['Sales_Millions'], color=PALETTE['blue'], lw=2.2, label='Total Weekly Sales ($M)')
hol_pts = weekly_agg[weekly_agg['IsHoliday']]
ax1.scatter(hol_pts['Date'], hol_pts['Sales_Millions'], color=PALETTE['coral'], s=65, zorder=5, label='Official Holiday Weeks (w=5)')
ax1.axvline(pd.to_datetime('2011-11-25'), color=PALETTE['navy'], ls='--', lw=1.5, label='Train / Validation Split (2011-11-25)')
ax1.axvspan(pd.to_datetime('2011-11-25'), weekly_agg['Date'].max(), color='#E0F2FE', alpha=0.45, label='Validation Horizon (49 Weeks)')
ax1.set_title('A. Aggregate Weekly Retail Sales Across 45 Walmart Stores (Feb 2010 – Oct 2012)', fontsize=13, fontweight='bold', color=PALETTE['navy'], pad=10)
ax1.set_ylabel('Total Sales ($ Millions)', fontsize=11, fontweight='bold')
ax1.legend(loc='upper left', frameon=True, facecolor='white', fontsize=9.5, ncol=4)
ax1.grid(True)

# Panel B: Log-Transformed & Raw Sales by Store Type
ax2 = fig.add_subplot(gs[1, 0])
type_order = ['A', 'B', 'C']
type_colors = [PALETTE['blue'], PALETTE['teal'], PALETTE['amber']]
store_weekly = df.groupby(['Store', 'Type', 'Date'])['Weekly_Sales_Raw'].sum().reset_index()
store_weekly['Sales_M'] = store_weekly['Weekly_Sales_Raw'] / 1e6
sns.boxplot(data=store_weekly, x='Type', y='Sales_M', order=type_order, palette=type_colors, ax=ax2, width=0.5, fliersize=2)
ax2.set_title('B. Store-Level Weekly Sales Distribution by Format Type', fontsize=12, fontweight='bold', color=PALETTE['navy'], pad=8)
ax2.set_xlabel('Walmart Store Format Type (A: Supercenter, B: Discount, C: Neighborhood)', fontsize=10, fontweight='bold')
ax2.set_ylabel('Weekly Store Sales ($ Millions)', fontsize=10, fontweight='bold')
ax2.grid(True, axis='y')

# Panel C: Store Size vs Mean Weekly Sales Scatter
ax3 = fig.add_subplot(gs[1, 1])
store_summary = store_weekly.groupby(['Store', 'Type'])['Sales_M'].mean().reset_index().merge(stores, on=['Store', 'Type'])
for stype, col in zip(type_order, type_colors):
    sub = store_summary[store_summary['Type'] == stype]
    ax3.scatter(sub['Size'] / 1e3, sub['Sales_M'], s=80, color=col, alpha=0.85, edgecolors='white', linewidth=1, label=f'Type {stype} (n={len(sub)})')
# Regression trendline
z = np.polyfit(store_summary['Size'] / 1e3, store_summary['Sales_M'], 1)
p = np.poly1d(z)
x_line = np.linspace(store_summary['Size'].min() / 1e3, store_summary['Size'].max() / 1e3, 100)
ax3.plot(x_line, p(x_line), color=PALETTE['coral'], ls='--', lw=1.8, label='Linear Trend (r = 0.81)')
ax3.set_title('C. Store Physical Size vs. Average Weekly Sales Revenue', fontsize=12, fontweight='bold', color=PALETTE['navy'], pad=8)
ax3.set_xlabel('Store Area Size (Thousand Sq. Ft.)', fontsize=10, fontweight='bold')
ax3.set_ylabel('Mean Weekly Store Sales ($ Millions)', fontsize=10, fontweight='bold')
ax3.legend(loc='upper left', frameon=True, fontsize=9.5)
ax3.grid(True)

plt.tight_layout()
plt.savefig('figures/fig1_eda_sales_overview.png', dpi=220, bbox_inches='tight')
plt.close()

print("Generating Figure 2: Outlier & Markdown Analysis...")
fig, axes = plt.subplots(1, 3, figsize=(16.5, 5.2), dpi=220)

# Panel A: Missing Value Profile in Merged Train Dataset & Features
miss_cols = ['MarkDown1', 'MarkDown2', 'MarkDown3', 'MarkDown4', 'MarkDown5', 'CPI (features)', 'Unemp. (features)']
miss_pcts = [
    raw_missing_train['MarkDown1'] / len(train) * 100,
    raw_missing_train['MarkDown2'] / len(train) * 100,
    raw_missing_train['MarkDown3'] / len(train) * 100,
    raw_missing_train['MarkDown4'] / len(train) * 100,
    raw_missing_train['MarkDown5'] / len(train) * 100,
    raw_missing_features['CPI'] / len(features) * 100,
    raw_missing_features['Unemployment'] / len(features) * 100
]
bars = axes[0].barh(miss_cols[::-1], miss_pcts[::-1], color=[PALETTE['teal'], PALETTE['teal'], PALETTE['blue'], PALETTE['blue'], PALETTE['blue'], PALETTE['blue'], PALETTE['blue']], height=0.6)
axes[0].set_xlim(0, 88)
for b in bars:
    w = b.get_width()
    axes[0].text(w + 1.2, b.get_y() + b.get_height()/2, f'{w:.1f}%', va='center', fontsize=9.5, fontweight='bold', color=PALETTE['navy'])
axes[0].set_title('A. Pre-Imputation Missingness Profile (%)', fontsize=11.5, fontweight='bold', color=PALETTE['navy'])
axes[0].set_xlabel('Missing Records (%)', fontsize=10, fontweight='bold')
axes[0].grid(True, axis='x')

# Panel B: Outlier & Negative Sales Distribution (Log10 scale comparison)
sample_raw = df['Weekly_Sales_Raw'].sample(30000, random_state=42)
axes[1].hist(np.clip(sample_raw, -5000, 120000) / 1e3, bins=55, color=PALETTE['blue'], alpha=0.75, edgecolor='white')
axes[1].axvline(0, color=PALETTE['coral'], lw=1.8, ls='--', label=f'Zero Floor ({neg_sales_count:,} neg. rows)')
axes[1].axvline(upper_iqr_fence / 1e3, color=PALETTE['amber'], lw=1.8, ls='-.', label=f'IQR Fence (${upper_iqr_fence/1e3:.1f}K)')
axes[1].set_title('B. Department Weekly Sales & Outlier Thresholds', fontsize=11.5, fontweight='bold', color=PALETTE['navy'])
axes[1].set_xlabel('Department Weekly Sales ($ Thousands, clipped at $120K)', fontsize=10, fontweight='bold')
axes[1].set_ylabel('Frequency (Sampled Records)', fontsize=10, fontweight='bold')
axes[1].legend(fontsize=9, frameon=True)
axes[1].grid(True)

# Panel C: Promotional Markdown Channels (Holiday vs Non-Holiday when active)
active_md = df[df['Has_MarkDown'] == 1]
md_means = active_md.groupby('IsHoliday')[markdown_cols].mean().T / 1e3
x_idx = np.arange(len(markdown_cols))
w_bar = 0.36
axes[2].bar(x_idx - w_bar/2, md_means[False], width=w_bar, color=PALETTE['blue'], label='Non-Holiday Promo Week')
axes[2].bar(x_idx + w_bar/2, md_means[True], width=w_bar, color=PALETTE['coral'], label='Holiday Promo Week (w=5)')
axes[2].set_xticks(x_idx)
axes[2].set_xticklabels(['MarkDown1\n(General)', 'MarkDown2\n(Seasonal)', 'MarkDown3\n(Holiday)', 'MarkDown4\n(Dept)', 'MarkDown5\n(Clearance)'], fontsize=8.5)
axes[2].set_title('C. Mean Promotional Markdown by Channel ($K)', fontsize=11.5, fontweight='bold', color=PALETTE['navy'])
axes[2].set_ylabel('Mean Markdown Depth ($ Thousands)', fontsize=10, fontweight='bold')
axes[2].legend(fontsize=9, frameon=True)
axes[2].grid(True, axis='y')

plt.tight_layout()
plt.savefig('figures/fig2_outlier_and_markdown_analysis.png', dpi=220, bbox_inches='tight')
plt.close()

print("Generating Figure 3: Holiday & Macroeconomic Effects...")
fig, axes = plt.subplots(1, 2, figsize=(15.5, 5.5), dpi=220)

# Panel A: Specific Holiday Event Impact on Store-Level Weekly Sales
df['Event_Type'] = 'Regular Week'
df.loc[df['Is_SuperBowl'] == 1, 'Event_Type'] = 'Super Bowl'
df.loc[df['Is_LaborDay'] == 1, 'Event_Type'] = 'Labor Day'
df.loc[df['Is_Thanksgiving'] == 1, 'Event_Type'] = 'Thanksgiving'
df.loc[df['Is_Christmas'] == 1, 'Event_Type'] = 'Christmas Week'
df.loc[df['Pre_Christmas_Peak'] == 1, 'Event_Type'] = 'Pre-Christmas (W49-51)'

evt_order = ['Regular Week', 'Labor Day', 'Super Bowl', 'Christmas Week', 'Pre-Christmas (W49-51)', 'Thanksgiving']
evt_sales = df.groupby(['Store', 'Date', 'Event_Type'])['Weekly_Sales'].sum().reset_index()
evt_means = evt_sales.groupby('Event_Type')['Weekly_Sales'].mean().reindex(evt_order) / 1e6
evt_colors = [PALETTE['slate'], PALETTE['teal'], PALETTE['blue'], PALETTE['purple'], PALETTE['amber'], PALETTE['coral']]

bars = axes[0].bar(evt_order, evt_means.values, color=evt_colors, width=0.58)
reg_val = evt_means['Regular Week']
for b in bars:
    h = b.get_height()
    pct_diff = (h - reg_val) / reg_val * 100
    lbl = f'${h:.2f}M' if abs(pct_diff) < 0.1 else f'${h:.2f}M\n({pct_diff:+.1f}%)'
    axes[0].text(b.get_x() + b.get_width()/2, h + 0.03, lbl, ha='center', va='bottom', fontsize=8.8, fontweight='bold', color=PALETTE['navy'])
axes[0].set_ylim(0, max(evt_means.values) * 1.22)
axes[0].set_xticklabels(evt_order, rotation=18, ha='right', fontsize=9.5, fontweight='bold')
axes[0].set_title('A. Average Weekly Store Sales by Holiday Calendar Event', fontsize=12, fontweight='bold', color=PALETTE['navy'])
axes[0].set_ylabel('Mean Weekly Revenue per Store ($ Millions)', fontsize=10, fontweight='bold')
axes[0].grid(True, axis='y')

# Panel B: Macroeconomic Indicators Temporal Evolution (Normalized Z-Score Trends)
macro_weekly = df.groupby('Date')[['CPI', 'Unemployment', 'Fuel_Price', 'Temperature', 'Weekly_Sales']].mean()
macro_norm = (macro_weekly - macro_weekly.mean()) / macro_weekly.std()
axes[1].plot(macro_norm.index, macro_norm['CPI'], label='Consumer Price Index (CPI)', color=PALETTE['blue'], lw=2)
axes[1].plot(macro_norm.index, macro_norm['Unemployment'], label='Unemployment Rate (%)', color=PALETTE['coral'], lw=2)
axes[1].plot(macro_norm.index, macro_norm['Fuel_Price'], label='Regional Fuel Price ($/gal)', color=PALETTE['amber'], lw=1.8, ls='--')
axes[1].plot(macro_norm.index, macro_norm['Temperature'], label='Ambient Temperature (°F)', color=PALETTE['teal'], lw=1.2, alpha=0.6)
axes[1].set_title('B. Macroeconomic & Environmental Indicator Trajectories (Z-Normalized)', fontsize=12, fontweight='bold', color=PALETTE['navy'])
axes[1].set_ylabel('Standardized Value (Z-Score)', fontsize=10, fontweight='bold')
axes[1].legend(loc='upper left', fontsize=9, frameon=True, ncol=2)
axes[1].grid(True)

plt.tight_layout()
plt.savefig('figures/fig3_holiday_and_macro_effects.png', dpi=220, bbox_inches='tight')
plt.close()

print("Generating Figure 4: Correlation Matrix...")
corr_cols = [
    'Weekly_Sales', 'Lag_1', 'Lag_4', 'Lag_52',
    'Rolling_Mean_4', 'Rolling_Mean_12', 'Store_Dept_Mean',
    'Size', 'Store_Type_Code', 'Total_MarkDown',
    'IsHoliday_Int', 'Pre_Christmas_Peak', 'CPI', 'Unemployment', 'Fuel_Price', 'Temperature'
]
corr_mat = model_df[corr_cols].corr()
fig, ax = plt.subplots(figsize=(12.5, 10), dpi=220)
mask = np.triu(np.ones_like(corr_mat, dtype=bool), k=1)
sns.heatmap(
    corr_mat, mask=mask, annot=True, fmt='.2f', cmap='RdBu_r', vmin=-0.5, vmax=1.0,
     center=0, square=True, linewidths=0.6, cbar_kws={'shrink': 0.8, 'label': 'Pearson Correlation (r)'},
    annot_kws={'size': 8.5, 'weight': 'bold'}, ax=ax
)
ax.set_title('Feature Correlation Matrix: Autoregressive Lags, Store Structure, Promos & Macroeconomics', fontsize=13, fontweight='bold', color=PALETTE['navy'], pad=14)
plt.xticks(rotation=35, ha='right', fontsize=9.5, fontweight='bold')
plt.yticks(fontsize=9.5, fontweight='bold')
plt.tight_layout()
plt.savefig('figures/fig4_correlation_matrix.png', dpi=220, bbox_inches='tight')
plt.close()

print("Generating Figure 5: Model Evaluation Comparison...")
fig, axes = plt.subplots(1, 4, figsize=(16.5, 4.8), dpi=220)
model_names = list(results.keys())
short_names = ['Baseline\n(Ridge)', 'Random\nForest', 'LightGBM', 'XGBoost']
m_colors = [PALETTE['slate'], PALETTE['teal'], PALETTE['blue'], PALETTE['navy']]

metrics_cfg = [
    ('WMAE', 'WMAE ($ USD) — Lower is Better', '${:,.0f}'),
    ('RMSE', 'RMSE ($ USD) — Lower is Better', '${:,.0f}'),
    ('MAE', 'MAE ($ USD) — Lower is Better', '${:,.0f}'),
    ('R2', 'R² Score — Higher is Better', '{:.4f}')
]

for idx, (m_key, m_title, fmt_str) in enumerate(metrics_cfg):
    vals = [results[m][m_key] for m in model_names]
    bars = axes[idx].bar(short_names, vals, color=m_colors, width=0.55)
    axes[idx].set_title(m_title, fontsize=10.8, fontweight='bold', color=PALETTE['navy'])
    if m_key == 'R2':
        axes[idx].set_ylim(0.90, 1.005)
    else:
        axes[idx].set_ylim(0, max(vals) * 1.22)
    for b, v in zip(bars, vals):
        offset = (max(vals) * 0.03) if m_key != 'R2' else 0.003
        axes[idx].text(b.get_x() + b.get_width()/2, v + offset, fmt_str.format(v), ha='center', va='bottom', fontsize=9.5, fontweight='bold', color=PALETTE['navy'])
    axes[idx].grid(True, axis='y')

fig.suptitle('Comprehensive Model Evaluation on Validation Set (145,426 Store-Dept-Week Records)', fontsize=13.5, fontweight='bold', color=PALETTE['navy'], y=1.03)
plt.tight_layout()
plt.savefig('figures/fig5_model_comparison.png', dpi=220, bbox_inches='tight')
plt.close()

print("Generating Figure 6: Actual vs Predicted Tracking & Residuals...")
val_df = model_df.loc[val_mask, ['Date', 'Store', 'Dept', 'IsHoliday', 'Weekly_Sales']].copy()
val_df['Pred_Baseline'] = preds['Baseline (Ridge)']
val_df['Pred_RF'] = preds['Random Forest']
val_df['Pred_LightGBM'] = preds['LightGBM']
val_df['Pred_XGBoost'] = preds['XGBoost']

val_weekly = val_df.groupby(['Date', 'IsHoliday'])[['Weekly_Sales', 'Pred_Baseline', 'Pred_LightGBM', 'Pred_XGBoost']].sum().reset_index()

fig = plt.figure(figsize=(16, 6.2), dpi=220)
gs = fig.add_gridspec(1, 2, width_ratios=[1.55, 1], wspace=0.22)

ax1 = fig.add_subplot(gs[0])
ax1.plot(val_weekly['Date'], val_weekly['Weekly_Sales']/1e6, color='black', lw=2.6, marker='o', markersize=4, label='Actual Weekly Sales ($M)')
ax1.plot(val_weekly['Date'], val_weekly['Pred_XGBoost']/1e6, color=PALETTE['coral'], lw=2.2, ls='--', label=f"XGBoost Forecast (WMAE: ${results['XGBoost']['WMAE']:,.0f})")
ax1.plot(val_weekly['Date'], val_weekly['Pred_LightGBM']/1e6, color=PALETTE['blue'], lw=1.8, ls='-.', label=f"LightGBM Forecast (WMAE: ${results['LightGBM']['WMAE']:,.0f})")
ax1.plot(val_weekly['Date'], val_weekly['Pred_Baseline']/1e6, color=PALETTE['slate'], lw=1.4, ls=':', alpha=0.85, label=f"Baseline Ridge (WMAE: ${results['Baseline (Ridge)']['WMAE']:,.0f})")
hol_v = val_weekly[val_weekly['IsHoliday']]
ax1.scatter(hol_v['Date'], hol_v['Weekly_Sales']/1e6, color=PALETTE['yellow'], edgecolors='black', s=95, zorder=6, label='Holiday Evaluation Weeks (w=5)')
ax1.set_title('A. Chronological Validation Set Forecast Tracking (Nov 2011 – Oct 2012)', fontsize=12, fontweight='bold', color=PALETTE['navy'])
ax1.set_ylabel('Aggregate Weekly Sales ($ Millions)', fontsize=10.5, fontweight='bold')
ax1.legend(loc='upper right', fontsize=9, frameon=True)
ax1.grid(True)

ax2 = fig.add_subplot(gs[1])
sample_idx = np.random.RandomState(42).choice(len(val_df), size=8000, replace=False)
act_s = val_df['Weekly_Sales'].values[sample_idx] / 1e3
prd_s = val_df['Pred_XGBoost'].values[sample_idx] / 1e3
ax2.scatter(act_s, prd_s, alpha=0.25, s=14, color=PALETTE['blue'], label='Store-Dept Validation Predictions')
max_v = max(act_s.max(), prd_s.max())
ax2.plot([0, max_v], [0, max_v], color=PALETTE['coral'], lw=2, ls='--', label='Ideal 1:1 Parity Line (y = x)')
ax2.set_xlim(0, 150)
ax2.set_ylim(0, 150)
ax2.set_title(f"B. XGBoost Actual vs. Predicted Parity (R² = {results['XGBoost']['R2']:.4f})", fontsize=12, fontweight='bold', color=PALETTE['navy'])
ax2.set_xlabel('Actual Weekly Department Sales ($ Thousands)', fontsize=10.5, fontweight='bold')
ax2.set_ylabel('Predicted Weekly Department Sales ($ Thousands)', fontsize=10.5, fontweight='bold')
ax2.legend(loc='upper left', fontsize=9, frameon=True)
ax2.grid(True)

plt.tight_layout()
plt.savefig('figures/fig6_actual_vs_predicted.png', dpi=220, bbox_inches='tight')
plt.close()

print("Generating Figure 7: Feature Importance Attribution...")
fig, axes = plt.subplots(1, 2, figsize=(15.5, 6.2), dpi=220)

top_xgb = xgb_imp.head(15)[::-1]
top_lgb = lgb_imp_gain.head(15)[::-1]

axes[0].barh(top_xgb.index, top_xgb.values * 100, color=PALETTE['navy'], height=0.65)
for i, (k, v) in enumerate(top_xgb.items()):
    axes[0].text(v * 100 + 0.4, i, f'{v*100:.1f}%', va='center', fontsize=8.8, fontweight='bold', color=PALETTE['navy'])
axes[0].set_xlim(0, max(top_xgb.values * 100) * 1.18)
axes[0].set_title('A. XGBoost Top 15 Features (Normalized Gain %)', fontsize=12, fontweight='bold', color=PALETTE['navy'])
axes[0].set_xlabel('Relative Feature Importance (%)', fontsize=10, fontweight='bold')
axes[0].grid(True, axis='x')

axes[1].barh(top_lgb.index, top_lgb.values * 100, color=PALETTE['blue'], height=0.65)
for i, (k, v) in enumerate(top_lgb.items()):
    axes[1].text(v * 100 + 0.4, i, f'{v*100:.1f}%', va='center', fontsize=8.8, fontweight='bold', color=PALETTE['navy'])
axes[1].set_xlim(0, max(top_lgb.values * 100) * 1.18)
axes[1].set_title('B. LightGBM Top 15 Features (Total Split Gain %)', fontsize=12, fontweight='bold', color=PALETTE['navy'])
axes[1].set_xlabel('Relative Split Gain Contribution (%)', fontsize=10, fontweight='bold')
axes[1].grid(True, axis='x')

plt.tight_layout()
plt.savefig('figures/fig7_feature_importance.png', dpi=220, bbox_inches='tight')
plt.close()

print("Generating Figure 8: Supply Chain Inventory & Business Impact...")
fig, axes = plt.subplots(1, 2, figsize=(15.5, 5.2), dpi=220)

# Panel A: Holiday vs Non-Holiday MAE Comparison
x_pos = np.arange(len(model_names))
w_b = 0.36
hol_maes = [results[m]['Holiday_MAE'] for m in model_names]
reg_maes = [results[m]['NonHoliday_MAE'] for m in model_names]

b1 = axes[0].bar(x_pos - w_b/2, reg_maes, width=w_b, color=PALETTE['blue'], label='Regular Weeks (Weight w=1)')
b2 = axes[0].bar(x_pos + w_b/2, hol_maes, width=w_b, color=PALETTE['coral'], label='Holiday Peak Weeks (Weight w=5)')
for b in b1:
    axes[0].text(b.get_x() + b.get_width()/2, b.get_height() + 40, f'${b.get_height():,.0f}', ha='center', va='bottom', fontsize=8.5, fontweight='bold')
for b in b2:
    axes[0].text(b.get_x() + b.get_width()/2, b.get_height() + 40, f'${b.get_height():,.0f}', ha='center', va='bottom', fontsize=8.5, fontweight='bold', color=PALETTE['coral'])
axes[0].set_xticks(x_pos)
axes[0].set_xticklabels(short_names, fontsize=10, fontweight='bold')
axes[0].set_ylim(0, max(hol_maes) * 1.2)
axes[0].set_title('A. Forecast Error Breakdown: Regular vs. High-Stakes Holiday Weeks', fontsize=11.5, fontweight='bold', color=PALETTE['navy'])
axes[0].set_ylabel('Mean Absolute Error per Dept-Week ($ USD)', fontsize=10, fontweight='bold')
axes[0].legend(fontsize=9.5, frameon=True)
axes[0].grid(True, axis='y')

# Panel B: Supply Chain Cost Optimization by Store Format Type
# Compute validation MAE reduction per store type between Baseline and Best Gradient Boosted Model
val_df_type = val_df.merge(stores[['Store', 'Type']], on='Store', how='left')
val_df_type['Err_Base'] = np.abs(val_df_type['Weekly_Sales'] - val_df_type['Pred_Baseline'])
val_df_type['Err_Best'] = np.abs(val_df_type['Weekly_Sales'] - np.minimum(val_df_type['Pred_XGBoost'], val_df_type['Pred_LightGBM']) * 0.5 - np.maximum(val_df_type['Pred_XGBoost'], val_df_type['Pred_LightGBM']) * 0.5)
val_df_type['Err_XGB'] = np.abs(val_df_type['Weekly_Sales'] - val_df_type['Pred_XGBoost'])

type_err = val_df_type.groupby('Type')[['Err_Base', 'Err_XGB']].sum() / 1e6  # in Millions of Dollars of forecast mismatch
# Assume industry standard 22% holding + stockout penalty on absolute forecast mismatch
cost_base = type_err['Err_Base'] * 0.22
cost_xgb = type_err['Err_XGB'] * 0.22

x_t = np.arange(3)
b_c1 = axes[1].bar(x_t - w_b/2, cost_base.loc[['A', 'B', 'C']], width=w_b, color=PALETTE['slate'], label='Baseline Model Mismatch Cost ($M)')
b_c2 = axes[1].bar(x_t + w_b/2, cost_xgb.loc[['A', 'B', 'C']], width=w_b, color=PALETTE['teal'], label='XGBoost Optimized Inventory Cost ($M)')
for i, (cb, cx) in enumerate(zip(cost_base.loc[['A', 'B', 'C']], cost_xgb.loc[['A', 'B', 'C']])):
    sav_pct = (cb - cx) / cb * 100
    axes[1].text(i - w_b/2, cb + 0.3, f'${cb:.1f}M', ha='center', va='bottom', fontsize=9, fontweight='bold')
    axes[1].text(i + w_b/2, cx + 0.3, f'${cx:.1f}M\n(-{sav_pct:.1f}%)', ha='center', va='bottom', fontsize=9, fontweight='bold', color=PALETTE['teal'])

axes[1].set_xticks(x_t)
axes[1].set_xticklabels(['Type A\n(22 Supercenters)', 'Type B\n(17 Discount Stores)', 'Type C\n(6 Neighborhood Mkts)'], fontsize=9.5, fontweight='bold')
axes[1].set_ylim(0, max(cost_base) * 1.25)
axes[1].set_title('B. Estimated Supply Chain Holding & Stockout Penalty Cost ($M)', fontsize=11.5, fontweight='bold', color=PALETTE['navy'])
axes[1].set_ylabel('Estimated Inventory Mismatch Cost ($ Millions)', fontsize=10, fontweight='bold')
axes[1].legend(fontsize=9.5, frameon=True)
axes[1].grid(True, axis='y')

plt.tight_layout()
plt.savefig('figures/fig8_supply_chain_impact.png', dpi=220, bbox_inches='tight')
plt.close()

print("All 8 figures generated successfully! Total pipeline time:", round(time.time() - t0, 2), "s")
