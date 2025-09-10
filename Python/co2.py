# ============================================================
# Script: CO2 Emissions and GDP per Capita Visualizations
# Author: Carlos Alfonso Mantilla Duarte
# Date: 03-10-2025
#


# ============================================================
# SECTION 1: Load and Prepare the Data
#
# Purpose:
# - Import dataset from CSV
# - Explore structure and summary
# - Clean missing values (drop NAs)
# - Rename columns for clarity
# - Convert text variables into categorical
# - Filter out empty codes and world aggregate (OWID_WRL)
#
# Note:
# - This section also includes guidance on how to install
#   required libraries in case they are not available.
# ============================================================

# --- Check and install required libraries if needed ---
import importlib
import sys
import subprocess

def install_if_missing(package):
    try:
        importlib.import_module(package)
    except ImportError:
        print(f"⚠️ {package} not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Core libraries for Section 1
for pkg in ["pandas", "seaborn", "matplotlib"]:
    install_if_missing(pkg)

# --- Import libraries ---
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# --- Load dataset ---
# Note: Adjust separator and decimal format according to file
dataset = pd.read_csv("Data/csv/consumption-co2-per-capita-vs-gdppc.csv",
                      sep=";", decimal=",")

# --- Quick overview ---
print("Dataset dimensions:", dataset.shape)
print("\nFirst rows:")
display(dataset.head())

print("\nStatistical summary:")
display(dataset.describe(include="all"))

# --- Rename columns ---
dataset.columns = ["country", "code", "year", "co2_pc", "gdp_pc", "pop", "region"]

# --- Remove missing values ---
dataset = dataset.dropna()

# --- Convert object (string) columns into categorical ---
for col in dataset.select_dtypes(include="object").columns:
    dataset[col] = dataset[col].astype("category")

# --- Filter out empty codes and OWID_WRL (world aggregate) ---
dataset = dataset[(dataset["code"] != "") & (dataset["code"] != "OWID_WRL")]

# --- Final check ---
print("\nDimensions after cleaning:", dataset.shape)
display(dataset.head())


# ============================================================
# SECTION 2: Global Time Series of CO2 Emissions per Capita
# ============================================================

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# --- Group by year and calculate population-weighted CO2 per capita ---
global_ts = (
    dataset
    .groupby("year")
    .apply(lambda df: (df["co2_pc"] * df["pop"]).sum() / df["pop"].sum())
    .reset_index(name="co2")   # reset index to keep 'year' as a column
)

# --- Ensure year is numeric ---
global_ts["year"] = pd.to_numeric(global_ts["year"], errors="coerce")

# --- Identify markers for key points ---
last_year = global_ts["year"].max()
min_val = global_ts["co2"].min()
max_val = global_ts["co2"].max()

global_ts["marker"] = global_ts.apply(
    lambda row: "A" if row["year"] == last_year else
                "B" if row["co2"] == min_val else
                "C" if row["co2"] == max_val else "D",
    axis=1
)

global_ts["value"] = global_ts.apply(
    lambda row: row["co2"] if row["marker"] in ["A", "B", "C"] else None,
    axis=1
)

# --- Custom colors for markers ---
marker_colors = {
    "A": "#1E88E5",  # Blue for last year
    "B": "#43A047",  # Green for minimum
    "C": "#E91E63",  # Pink for maximum
    "D": "#F9A825"   # Yellow for other years
}

# --- Build subtitle text (dynamic) ---
subtitle_labels = []
for _, row in global_ts[global_ts["marker"].isin(["A","B","C"])].iterrows():
    if row["marker"] == "A":
        subtitle_labels.append(f"Last: {row['value']:.1f}")
    elif row["marker"] == "B":
        subtitle_labels.append(f"Min: {row['value']:.1f} ({int(row['year'])})")
    elif row["marker"] == "C":
        subtitle_labels.append(f"Max: {row['value']:.1f} ({int(row['year'])})")

subtitle_text = "Key points • " + " • ".join(subtitle_labels)

# --- Plot ---
plt.figure(figsize=(12,6))
plt.bar(
    global_ts["year"],
    global_ts["co2"],
    color=[marker_colors[m] for m in global_ts["marker"]]
)

# Add labels for highlighted values
for _, row in global_ts.dropna(subset=["value"]).iterrows():
    plt.text(
        row["year"], row["co2"] + 0.2,
        f"{row['value']:.1f}",
        ha="center", va="bottom", fontsize=10, fontweight="bold"
    )

# Titles (mimicking ggplot2 labs)
plt.title("Per Capita CO₂ Footprint", fontsize=16, fontweight="bold", loc="center", pad=20)
plt.text(
    0.5, 1.02, subtitle_text,
    ha="center", va="bottom", transform=plt.gca().transAxes,
    fontsize=12
)

# Axis adjustments
plt.ylim(0, global_ts["co2"].max() * 1.15)
plt.xlabel("Year")
plt.ylabel(None)

sns.despine()
plt.show()

# ============================================================
# SECTION 3: Top 10 Countries by Absolute CO2 Emissions
#
# Purpose:
# - Focus on the most recent year available
# - Calculate total CO2 emissions (population × per capita)
# - Rank countries and select the Top 10 emitters
# - Visualize with horizontal bars and aligned labels
# ============================================================

# --- Filter most recent year ---
latest_year = dataset["year"].max()

top10 = (
    dataset[dataset["year"] == latest_year]
    .groupby("country", as_index=False)
    .agg({"co2_pc": "mean", "pop": "mean"})   # keep columns
)

# --- Calculate absolute emissions ---
top10["co2"] = top10["co2_pc"] * top10["pop"]

# --- Select Top 10 emitters ---
top10 = top10.nlargest(10, "co2").copy()

# --- Sort for horizontal plot ---
top10 = top10.sort_values("co2", ascending=True)

# --- Plot ---
plt.figure(figsize=(10,6))
bars = plt.barh(top10["country"], top10["co2"], color="#b3b3b3")  # 70% grey

# Highlight the maximum emitter (bold, inside the bar)
max_row = top10.loc[top10["co2"].idxmax()]
plt.text(
    max_row["co2"]*0.99, max_row["country"],
    f"{max_row['co2']:.0f}", color="white",
    ha="right", va="center", fontsize=11, fontweight="bold"
)

# Labels for other countries (aligned with the maximum bar)
for _, row in top10.iterrows():
    if row["country"] != max_row["country"]:
        plt.text(
            max_row["co2"]*0.99, row["country"],
            f"{row['co2']:.0f}", color="black",
            ha="right", va="center", fontsize=10
        )

# Titles and subtitles
plt.title("Where most CO₂ comes from", fontsize=16, fontweight="bold", pad=20)
plt.text(
    0.5, 1.02, "Top 10 emitters (absolute values – selected period)",
    ha="center", va="bottom", transform=plt.gca().transAxes, fontsize=12
)

# Axis cleanup
plt.xlabel(None)
plt.ylabel(None)
plt.xlim(0, top10["co2"].max() * 1.15)  # <-- fixed

sns.despine(left=True, bottom=True)
plt.show()

# ============================================================
# SECTION 4: Top 10 Countries (Values in Billions – "bn")
#
# Purpose:
# - Extend the previous Top 10 analysis
# - Express emissions in billions (× 1e9) for readability
# - Visualize with horizontal bars and labels in "X.X bn"
# ============================================================

# --- Filter most recent year ---
latest_year = dataset["year"].max()

top10_bn = (
    dataset[dataset["year"] == latest_year]
    .groupby("country", as_index=False)
    .agg({"co2_pc": "mean", "pop": "mean"})
)

# --- Calculate absolute emissions and convert to billions ---
top10_bn["co2"] = top10_bn["co2_pc"] * top10_bn["pop"]
top10_bn["co2_B"] = top10_bn["co2"] / 1e9   # billions

# --- Select Top 10 emitters ---
top10_bn = top10_bn.nlargest(10, "co2").copy()

# --- Sort for horizontal plot ---
top10_bn = top10_bn.sort_values("co2", ascending=True)

# --- Plot ---
plt.figure(figsize=(10,6))
bars = plt.barh(top10_bn["country"], top10_bn["co2"], color="#b3b3b3")

# Highlight the maximum emitter with bold label inside the bar
max_row = top10_bn.loc[top10_bn["co2"].idxmax()]
plt.text(
    max_row["co2"]*0.99, max_row["country"],
    f"{max_row['co2_B']:.1f} bn", color="white",
    ha="right", va="center", fontsize=11, fontweight="bold"
)

# Labels for other emitters aligned with the maximum bar
for _, row in top10_bn.iterrows():
    if row["country"] != max_row["country"]:
        plt.text(
            max_row["co2"]*0.99, row["country"],
            f"{row['co2_B']:.1f} bn", color="black",
            ha="right", va="center", fontsize=10
        )

# Titles and subtitles
plt.title("Where most CO₂ comes from", fontsize=16, fontweight="bold", pad=20)
plt.text(
    0.5, 1.02, "Top 10 emitters (absolute values in billions – last period)",
    ha="center", va="bottom", transform=plt.gca().transAxes, fontsize=12
)

# Axis cleanup
plt.xlabel(None)
plt.ylabel(None)
plt.xlim(0, top10_bn["co2"].max() * 1.15)

# Format x-axis ticks to billions
plt.xticks(
    plt.xticks()[0],
    [f"{x/1e9:.1f} bn" for x in plt.xticks()[0]]
)

sns.despine(left=True, bottom=True)
plt.show()

# ============================================================
# SECTION 5: Scatterplot - GDP per Capita vs CO2 per Capita
#
# Purpose:
# - Explore the relationship between GDP per capita and CO2 per capita
# - Encode population size (point size) and region (color)
# - Use logarithmic scale for GDP per capita
# ============================================================

import seaborn as sns
import matplotlib.ticker as mticker

# --- Filter most recent year ---
latest_year = dataset["year"].max()
scatter_data = dataset[dataset["year"] == latest_year].copy()

# --- Custom color palette for regions ---
region_colors = {
    "Africa": "#70B0E0",
    "Asia": "#FCB714",
    "Europe": "#2878BD",
    "North America": "#0EB194",
    "Oceania": "#108372",
    "South America": "#AF916D"
}

# --- Plot ---
plt.figure(figsize=(10,7))
sns.scatterplot(
    data=scatter_data,
    x="gdp_pc", y="co2_pc",
    hue="region", size="pop",
    sizes=(20, 400), alpha=0.7,
    palette=region_colors, edgecolor="none"
)

# Logarithmic scale for GDP per capita
plt.xscale("log")
plt.gca().xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))

# Titles and labels
plt.title("Wealth, emissions and population combined", fontsize=16, fontweight="bold", pad=20)
plt.text(
    0.5, 1.02,
    f"Worldwide – Entities: {scatter_data['country'].nunique()}",
    ha="center", va="bottom", transform=plt.gca().transAxes, fontsize=12
)

plt.xlabel("GDP per capita", fontsize=12)
plt.ylabel("CO₂ emissions per capita", fontsize=12)

# Remove redundant size legend
handles, labels = plt.gca().get_legend_handles_labels()
# Keep only region labels (skip 'size')
new_handles, new_labels = [], []
for h, l in zip(handles, labels):
    if not l.startswith("pop"):
        new_handles.append(h)
        new_labels.append(l)
plt.legend(new_handles, new_labels, title=None, loc="best")

sns.despine()
plt.show()

# ============================================================
# SECTION 6: Regional Time Series - Stacked Area Chart
#
# Purpose:
# - Show how different world regions contribute to total CO2 emissions over time
# - Each region stacked to represent absolute contribution
# - Lines added on top for better readability
# ============================================================

# ============================================================
# SECTION 6: Regional Time Series - Stacked Area Chart
# ============================================================

# --- Create absolute emissions first ---
dataset["co2_abs"] = dataset["co2_pc"] * dataset["pop"]

# --- Aggregate emissions by year and region ---
regional_ts = (
    dataset
    .groupby(["year", "region"], as_index=False)
    .agg({"co2_abs": "sum"})
    .rename(columns={"co2_abs": "co2"})
)

# --- Custom color palette (consistent with Section 5) ---
region_colors = {
    "Africa": "#70B0E0",
    "Asia": "#FCB714",
    "Europe": "#2878BD",
    "North America": "#0EB194",
    "Oceania": "#108372",
    "South America": "#AF916D"
}

# --- Pivot for stacked area ---
pivot_data = regional_ts.pivot(index="year", columns="region", values="co2").fillna(0)

# --- Plot ---
fig, ax = plt.subplots(figsize=(12,7))

# Stacked area
pivot_data.plot.area(
    ax=ax, alpha=0.65, linewidth=0,
    color=[region_colors.get(r, "#cccccc") for r in pivot_data.columns]
)

# Add lines on top of areas for readability
pivot_data.plot(
    ax=ax, linewidth=1,
    color=[region_colors.get(r, "#cccccc") for r in pivot_data.columns],
    legend=False
)

# Titles and labels
ax.set_title("How regions drive global CO₂ growth", fontsize=16, fontweight="bold", pad=20)
ax.text(
    0.5, 1.02, "Stacked area by region",
    ha="center", va="bottom", transform=ax.transAxes, fontsize=12
)

ax.set_xlabel(None)
ax.set_ylabel("CO₂ emissions (absolute)", fontsize=12)

# Legend cleanup
ax.legend(title=None, loc="upper left")

sns.despine()
plt.show()

# ============================================================
# SECTION 7: Global and Regional Maps of CO2 Emissions
#
# Purpose:
# - Visualize CO2 emissions per capita on world maps
# - Use ISO3 codes with Plotly Express (no geopandas required)
# - Show global map and an example of regional zoom (North America)
# ============================================================

import plotly.express as px

# --- Prepare dataset for mapping (2022) ---
map_data = dataset[dataset["year"] == 2022].copy()

# --- Global map ---
fig_global = px.choropleth(
    map_data,
    locations="code",              # ISO3 country codes
    color="co2_pc",                # CO₂ per capita
    hover_name="country",
    hover_data={"gdp_pc": True, "pop": True},
    color_continuous_scale=["#7D8B94", "#A0B2A6", "#CFCFCF"],  # custom scale from R script
    projection="robinson",
    title="Global CO₂ emissions per capita (2022)"
)
fig_global.update_layout(
    coloraxis_colorbar=dict(title="CO₂ per capita"),
    margin=dict(l=0, r=0, t=50, b=0)
)
fig_global.show()

# --- Regional map (example: North America) ---
map_region = map_data[map_data["region"] == "North America"].copy()

fig_region = px.choropleth(
    map_region,
    locations="code",
    color="co2_pc",
    hover_name="country",
    hover_data={"gdp_pc": True, "pop": True},
    color_continuous_scale=["#7D8B94", "#A0B2A6", "#CFCFCF"],
    projection="robinson",
    title="North America CO₂ emissions per capita (2022)"
)
fig_region.update_layout(
    coloraxis_colorbar=dict(title="CO₂ per capita"),
    margin=dict(l=0, r=0, t=50, b=0)
)
fig_region.show()

# ============================================================
# SECTION 8: Closing Notes
#
# Purpose:
# - Summarize the workflow of data storytelling with CO₂ emissions
# - Highlight pedagogical aspects and adaptation possibilities
# ============================================================

print("""
📌 Workflow Recap

1. Context and libraries
   - Defined the purpose, dataset, and required packages.

2. Data preparation
   - Imported, cleaned, and transformed the dataset.
   - Removed missing values and irrelevant codes.

3. Global time series
   - Showed CO₂ per capita evolution over time.
   - Highlighted key points (last, min, max).

4. Country comparisons
   - Ranked countries by total emissions.
   - Displayed Top 10 in absolute values and billions ("bn").

5. Scatterplot (relationships)
   - Linked GDP per capita, CO₂ per capita, and population.
   - Highlighted global inequality in wealth and emissions.

6. Regional contributions
   - Stacked area chart showing regional shares across time.

7. Maps
   - Global map with Robinson projection.
   - Regional zooms (North America as example; customizable).

------------------------------------------------------------

🎓 Pedagogical Notes

- Each visualization was designed to be explanatory, not just exploratory.
- Storytelling elements emphasized comparisons, trends, and regional patterns.
- Students can adapt the workflow by:
  * Changing ranking size (Top 5, Top 20).
  * Modifying region filters (Africa, Asia, etc.).
  * Exploring different years.
  * Adjusting color palettes for accessibility.

------------------------------------------------------------

✅ Key Takeaway

Data visualization is not just about creating charts.
It’s about guiding the audience through a clear narrative supported by evidence.
Each design choice (chart type, color, scale, projection) plays a role in telling the story.
""")
