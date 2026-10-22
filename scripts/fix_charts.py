import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

NAVY = '#0F2942'
BLUE = '#0071CE'
CORAL = '#E11D48'
GREEN = '#10B981'
LIGHT_GRAY = '#64748B'
AMBER = '#D97706'

# Fix Chart 5: Cost Savings
cats = ['Type A\n(Supercenters)', 'Type B\n(Discount)', 'Type C\n(Neighborhood)', 'Total Across\nAll 45 Stores']
base_costs = [46.5, 29.7, 4.1, 80.3]
opt_costs = [29.4, 16.9, 2.3, 48.6]

x = np.arange(len(cats))
w_bar = 0.35

fig, ax = plt.subplots(figsize=(8.5, 4.8), dpi=200)
b1 = ax.bar(x - w_bar/2, base_costs, width=w_bar, color=LIGHT_GRAY, label='Baseline Model Mismatch Cost ($M)')
b2 = ax.bar(x + w_bar/2, opt_costs, width=w_bar, color=GREEN, label='Machine Learning Optimized Cost ($M)')

for b, v in zip(b1, base_costs):
    ax.text(b.get_x() + b.get_width()/2, v + 1.8, f"${v:.1f}M", ha='center', va='bottom', fontsize=11, fontweight='bold', color=NAVY)

for i, (b, v, b_old) in enumerate(zip(b2, opt_costs, base_costs)):
    pct = (b_old - v) / b_old * 100
    ax.text(b.get_x() + b.get_width()/2, v + 1.8, f"${v:.1f}M\n(-{pct:.0f}%)", ha='center', va='bottom', fontsize=11, fontweight='bold', color=GREEN)

ax.set_xticks(x)
ax.set_xticklabels(cats, fontsize=11.5, fontweight='bold')
ax.set_title('Business Impact: $31.7M Saved in Holding & Stockout Penalties', fontsize=14, fontweight='bold', color=NAVY, pad=14)
ax.set_ylabel('Estimated Inventory Mismatch Cost ($M)', fontsize=12, fontweight='bold', color=NAVY)
ax.tick_params(axis='both', labelsize=11)
ax.legend(loc='upper left', fontsize=10.5, frameon=True)
ax.set_ylim(0, 102)
ax.grid(True, axis='y')
plt.tight_layout()
plt.savefig('slide_charts/chart5_cost_savings.png', dpi=200)
plt.close()

# New Clean Chart: Preprocessing Summary
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.5, 4.8), dpi=200)

# Panel 1: MarkDown Missingness
md_labels = ['MarkDown 1', 'MarkDown 2', 'MarkDown 3', 'MarkDown 4', 'MarkDown 5']
missing_pcts = [64.3, 73.6, 67.5, 68.0, 64.1]
bars1 = ax1.barh(md_labels[::-1], missing_pcts[::-1], color=BLUE, height=0.55)
for b in bars1:
    w = b.get_width()
    ax1.text(w + 1.5, b.get_y() + b.get_height()/2, f"{w:.1f}%", va='center', fontsize=11, fontweight='bold', color=NAVY)
ax1.set_xlim(0, 90)
ax1.set_title('1. Promotional MarkDowns:\n64%–74% Missing (Pre-2011)', fontsize=12.5, fontweight='bold', color=NAVY)
ax1.set_xlabel('Missing Records (%) -> Imputed 0.0 + Flag', fontsize=10.5, fontweight='bold', color=NAVY)
ax1.grid(True, axis='x')

# Panel 2: Returns & Outliers
outlier_types = ['Negative Returns\n(< $0 Sales)', 'Upper Outliers\n(> 99.95th Pct)']
outlier_counts = [1285, 422]
bars2 = ax2.bar(outlier_types, outlier_counts, color=[CORAL, AMBER], width=0.45)
for b in bars2:
    h = b.get_height()
    ax2.text(b.get_x() + b.get_width()/2, h + 35, f"{h:,} rows", ha='center', va='bottom', fontsize=11.5, fontweight='bold', color=NAVY)
ax2.set_ylim(0, 1600)
ax2.set_title('2. Anomaly Cleaning:\nReturns & Outlier Caps', fontsize=12.5, fontweight='bold', color=NAVY)
ax2.set_ylabel('Number of Affected Records', fontsize=10.5, fontweight='bold', color=NAVY)
ax2.grid(True, axis='y')

plt.tight_layout()
plt.savefig('slide_charts/chart_preprocessing_simple.png', dpi=200)
plt.close()

print("Updated Chart 5 and generated chart_preprocessing_simple.png!")
