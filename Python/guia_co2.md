# 📊 CO₂ Emissions and GDP per Capita – Data Visualization Guide (Python)

## 1. Introduction
This guide accompanies the **Python notebook** for analyzing and visualizing the relationship between **CO₂ emissions per capita**, **GDP per capita**, and **population** across countries and regions.  
The workflow demonstrates how to move from raw data to **explanatory visualizations** that support storytelling.

**Learning goals:**
- Practice data cleaning and transformation with `pandas`.
- Explore different visualization types with `matplotlib` and `seaborn`.
- Highlight key points (e.g., last year, min, max) in time series.
- Compare countries and regions using horizontal bar charts and stacked areas.
- Examine relationships with scatterplots.
- Map emissions data using spatial tools (`plotly` for interactive maps, optional `geopandas`/`cartopy`).
- Understand how design choices (scales, colors, projection) affect narrative.

**Dataset used:**  
- **File**: `consumption-co2-per-capita-vs-gdppc.csv`  
- **Source**: [Our World in Data](https://ourworldindata.org/)  
- **Variables**:
  - `country`: Country name  
  - `code`: ISO3 country code  
  - `year`: Year of observation  
  - `co2_pc`: CO₂ emissions per capita  
  - `gdp_pc`: GDP per capita  
  - `pop`: Population  
  - `region`: Continent or region  

---
## 2. Required Libraries

The analysis uses a combination of libraries for **data manipulation**, **visualization**, and **mapping**:

- **pandas** → Wrangling and transforming data (filter, groupby, aggregation, mutate-like operations).  
- **matplotlib** → Creating static visualizations (bars, scatterplots, area plots).  
- **seaborn** → Enhancing plots with cleaner styles and easier syntax.  
- **plotly** → Interactive visualizations and world maps (choropleths with Robinson projection).  
- **geopandas** *(optional)* → Handling spatial data and merging with shapefiles.  
- **cartopy** *(optional)* → Working with map projections and advanced geographic plotting.  

---
## 3. Installation and Importing

### Installation (only once per environment)

In Jupyter Notebook, install packages directly with:

```python
%pip install pandas matplotlib seaborn plotly geopandas cartopy
```

Or using **conda**:

```python
conda install pandas matplotlib seaborn
conda install -c plotly plotly
conda install -c conda-forge geopandas cartopy
```

---

### Import libraries (every session)

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px   # interactive maps
# Optional for geographic analysis
# import geopandas as gpd
# import cartopy.crs as ccrs
```

👉 If a library is already installed, you only need the `import` command.
👉 For advanced dependency management, consider using tools like **venv**, **conda environments**, or **poetry**.

---

## 4. Loading and Preparing the Data  

Before creating visualizations, it is essential to **clean and prepare the dataset**. This ensures the analysis is consistent and avoids misleading results.  

---

### 4.1 Importing the dataset  

We use `pandas.read_csv()` to load the data. Note that in this case the file uses `;` as a separator and `,` as a decimal mark.  

```python
import pandas as pd

dataset = pd.read_csv("Data/csv/consumption-co2-per-capita-vs-gdppc.csv",
                      sep=";", decimal=",")
dataset.info()
dataset.describe(include="all")
```

The `.info()` and `.describe()` functions provide a quick overview of the dataset.

---

### 4.2 Renaming variables

To make the notebook more readable, we rename the variables with shorter and clearer names.

```python
dataset.columns = ["country", "code", "year", "co2_pc", "gdp_pc", "pop", "region"]
```

---

### 4.3 Handling missing values

It is important to remove rows with missing values (`NaN`) to avoid inconsistencies in calculations.

```python
dataset = dataset.dropna()
```

We can also compare summaries **with and without NaNs** to understand their impact:

```python
dataset.dropna().describe()
dataset.describe()
```

---

### 4.4 Converting variables

Text variables are transformed into **categorical data**, which are more efficient for grouping and analysis.

```python
for col in dataset.select_dtypes(include="object").columns:
    dataset[col] = dataset[col].astype("category")
```

---

### 4.5 Filtering irrelevant cases

We exclude records with missing country codes and the global aggregate (`OWID_WRL`) since they do not represent individual countries.

```python
dataset = dataset[(dataset["code"] != "") & (dataset["code"] != "OWID_WRL")]
```

---

### 4.6 Final check

We print the dataset to confirm the cleaning process.

```python
dataset.head()
```

---

✅ After this stage, the dataset is **clean and ready** for building explanatory visualizations.

---

## 5. Global Time Series of CO₂ Emissions per Capita  

### 5.1 Purpose of this visualization  
The objective is to show the **evolution of global CO₂ emissions per capita** over time.  
Instead of a simple average, we compute a **population-weighted mean** so that large countries contribute proportionally to the global measure.  

This type of visualization helps identify:  
- Long-term trends (growth or decline).  
- Key reference points: **minimum**, **maximum**, and **latest year**.  
- A **narrative** built around those points, making the chart explanatory rather than purely descriptive.  

---

### 5.2 Data preparation  
We calculate the global per-capita CO₂ emissions by year:  

```python
global_ts = (
    dataset
    .groupby("year")
    .apply(lambda df: (df["co2_pc"] * df["pop"]).sum() / df["pop"].sum())
    .reset_index(name="co2")
)
```

Next, we classify the years with markers:

* **A = Last year**
* **B = Minimum value**
* **C = Maximum value**
* **D = Other years**

This classification allows us to add emphasis in the visualization.

```python
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
```

---

### 5.3 Building the chart

We use a **bar chart** with custom colors for the markers.
Text labels highlight the exact values of the last, min, and max points.

```python
import matplotlib.pyplot as plt
import seaborn as sns

marker_colors = {
    "A": "#1E88E5",  # Last year
    "B": "#43A047",  # Minimum
    "C": "#E91E63",  # Maximum
    "D": "#F9A825"   # Others
}

plt.figure(figsize=(12,6))
plt.bar(
    global_ts["year"],
    global_ts["co2"],
    color=[marker_colors[m] for m in global_ts["marker"]]
)

# Labels for key points
for _, row in global_ts.dropna(subset=["value"]).iterrows():
    plt.text(
        row["year"], row["co2"] + 0.2,
        f"{row['value']:.1f}",
        ha="center", va="bottom", fontsize=10, fontweight="bold"
    )

plt.title("Per Capita CO₂ Footprint", fontsize=16, fontweight="bold")
plt.xlabel("Year")
plt.ylabel(None)
plt.ylim(0, global_ts["co2"].max() * 1.15)

sns.despine()
plt.show()
```

---

### 5.4 Storytelling element

The subtitle (or annotation) can be **automatically generated** by concatenating the key values (Last, Min, Max).
This ensures the chart not only shows data but also **tells a story** at a glance.

**Example narrative:**

> *"Global CO₂ per capita peaked at X in year Y, dropped to its minimum of Z in year W, and currently stands at K."*

---

✅ This visualization illustrates how to move from **exploratory analysis** (just showing trends) to **explanatory storytelling** (emphasizing the most relevant points).

---

## 6. Top 10 CO₂ Emitters by Country  

### 6.1 Purpose of this visualization  
This visualization highlights the **countries that contribute most to global CO₂ emissions** in the most recent year.  
Ranking countries allows us to focus the audience’s attention on **key players**, rather than being overwhelmed by the entire dataset.  

---

### 6.2 Data preparation  
We filter the dataset for the latest year and compute absolute emissions for each country:  

```python
latest_year = dataset["year"].max()

top10 = (
    dataset[dataset["year"] == latest_year]
    .groupby("country", as_index=False)
    .apply(lambda df: pd.Series({
        "co2": (df["co2_pc"] * df["pop"]).sum()
    }))
    .reset_index(drop=True)
)

# Select Top 10 emitters
top10 = top10.nlargest(10, "co2")
```

⚠️ **Pedagogical note:** the parameter `nlargest(10, "co2")` can be modified depending on the narrative goal (Top 5, Top 20, or regional subsets).

---

### 6.3 Variant 1 – Absolute values

We display the total emissions as raw absolute numbers.

* The **largest emitter** is labeled inside its bar (bold, white text).
* Other countries are labeled **aligned to the maximum bar**, facilitating visual comparison.

```python
plt.figure(figsize=(10,6))
bars = plt.barh(top10["country"], top10["co2"], color="#b3b3b3")

max_row = top10.loc[top10["co2"].idxmax()]
plt.text(max_row["co2"]*0.99, max_row["country"],
         f"{max_row['co2']:.0f}", color="white",
         ha="right", va="center", fontsize=11, fontweight="bold")

for _, row in top10.iterrows():
    if row["country"] != max_row["country"]:
        plt.text(max_row["co2"]*0.99, row["country"],
                 f"{row['co2']:.0f}", color="black",
                 ha="right", va="center", fontsize=10)

plt.title("Where most CO₂ comes from", fontsize=16, fontweight="bold")
plt.show()
```

---

### 6.4 Variant 2 – Values in billions (“bn”)

To improve readability for non-technical audiences, we transform emissions into **billions (× 1e9)**:

```python
top10["co2_B"] = top10["co2"] / 1e9
```

Labels are formatted as `"X.X bn"` for clarity:

```python
plt.figure(figsize=(10,6))
bars = plt.barh(top10["country"], top10["co2"], color="#b3b3b3")

max_row = top10.loc[top10["co2"].idxmax()]
plt.text(max_row["co2"]*0.99, max_row["country"],
         f"{max_row['co2_B']:.1f} bn", color="white",
         ha="right", va="center", fontsize=11, fontweight="bold")

for _, row in top10.iterrows():
    if row["country"] != max_row["country"]:
        plt.text(max_row["co2"]*0.99, row["country"],
                 f"{row['co2_B']:.1f} bn", color="black",
                 ha="right", va="center", fontsize=10)

plt.title("Where most CO₂ comes from", fontsize=16, fontweight="bold")
plt.show()
```

---

### 6.5 Storytelling element

Choosing between **raw absolute values** or **billions** changes the narrative:

* Absolute values are precise and emphasize **scale differences**.
* Billions are easier to understand and more effective in **public communication**.

**Example narrative:**

> *“In the most recent year, just 10 countries account for the vast majority of global emissions, with Country X alone surpassing Y billion tons.”*

---

✅ This visualization demonstrates how **ranking and scaling choices** are not purely technical, but part of the storytelling strategy.

---

## 7. Scatterplot – GDP per Capita vs CO₂ per Capita  

### 7.1 Purpose of this visualization  
This chart explores the **relationship between wealth and emissions**:  
- **X-axis:** GDP per capita (log scale).  
- **Y-axis:** CO₂ emissions per capita.  
- **Point size:** population of each country.  
- **Color:** continent/region.  

By combining four variables in a single chart, we can see **patterns of inequality**: wealthy countries often emit more CO₂ per person, but there are significant regional differences.  

---

### 7.2 Data preparation  
We filter the dataset for the **most recent year**:  

```python
latest_year = dataset["year"].max()
scatter_data = dataset[dataset["year"] == latest_year].copy()
```

---

### 7.3 Building the scatterplot

* Use `sns.scatterplot()` to represent countries.
* Encode population (`size`) and region (`color`).
* Apply `plt.xscale("log")` to handle the wide range of GDP values.
* Use a **manual color palette** to ensure visual consistency across all charts.

```python
import seaborn as sns
import matplotlib.pyplot as plt

region_colors = {
    "Africa": "#70B0E0",
    "Asia": "#FCB714",
    "Europe": "#2878BD",
    "North America": "#0EB194",
    "Oceania": "#108372",
    "South America": "#AF916D"
}

plt.figure(figsize=(10,7))
sns.scatterplot(
    data=scatter_data,
    x="gdp_pc", y="co2_pc",
    hue="region", size="pop",
    sizes=(20, 400), alpha=0.7,
    palette=region_colors, edgecolor="none"
)

plt.xscale("log")
plt.xlabel("GDP per capita")
plt.ylabel("CO₂ emissions per capita")
plt.title("Wealth, emissions and population combined", fontsize=16, fontweight="bold")

plt.legend(title=None, loc="best")
plt.show()
```

---

### 7.4 Storytelling element

This scatterplot allows us to highlight **contrasts**:

* Some countries with **high GDP per capita** but **low CO₂ per capita** (e.g., efficient economies).
* Others with **low GDP** but **high CO₂ per capita**, often linked to fossil fuel dependence.
* **Population size** underscores the global impact of large countries like China or India.

**Example narrative:**

> *“Wealthier nations tend to emit more CO₂ per person, but the scatterplot also reveals exceptions — some countries achieve higher GDP with relatively lower emissions.”*

---

✅ This visualization is effective for showing **relationships and inequalities**, and demonstrates how multiple dimensions can be combined in a single chart to enrich the story.

---

## 8. Regional Time Series – Stacked Area Chart  

### 8.1 Purpose of this visualization  
The stacked area chart shows how **different world regions contribute to global CO₂ emissions** over time.  
This visualization emphasizes the **composition of the total**, not only the overall growth.  

Key insights that can be derived:  
- Which regions drive the majority of emissions growth.  
- Shifts in regional contributions (e.g., rise of Asia, stabilization in Europe).  
- The interplay between global increase and regional dynamics.  

---

### 8.2 Data preparation  
We calculate total CO₂ emissions (absolute values) by **year and region**:  

```python
dataset["co2_abs"] = dataset["co2_pc"] * dataset["pop"]

regional_ts = (
    dataset
    .groupby(["year", "region"], as_index=False)
    .agg({"co2_abs": "sum"})
    .rename(columns={"co2_abs": "co2"})
)
```
---

### 8.3 Building the stacked area chart

* `plot.area()` to display stacked contributions.
* Overlay `plot()` lines for better readability.
* Consistent color palette with previous visualizations (scatterplot).
* Labels emphasize that the Y-axis shows **absolute emissions**.

```python
import matplotlib.pyplot as plt

region_colors = {
    "Africa": "#70B0E0",
    "Asia": "#FCB714",
    "Europe": "#2878BD",
    "North America": "#0EB194",
    "Oceania": "#108372",
    "South America": "#AF916D"
}

pivot_data = regional_ts.pivot(index="year", columns="region", values="co2").fillna(0)

fig, ax = plt.subplots(figsize=(12,7))

# Stacked area
pivot_data.plot.area(
    ax=ax, alpha=0.65, linewidth=0,
    color=[region_colors.get(r, "#cccccc") for r in pivot_data.columns]
)

# Overlay lines
pivot_data.plot(
    ax=ax, linewidth=1,
    color=[region_colors.get(r, "#cccccc") for r in pivot_data.columns],
    legend=False
)

ax.set_title("How regions drive global CO₂ growth", fontsize=16, fontweight="bold", pad=20)
ax.set_xlabel(None)
ax.set_ylabel("CO₂ emissions (absolute)")

ax.legend(title=None, loc="upper left")
plt.show()
```

---

### 8.4 Storytelling element

Stacked area charts are useful to show **parts of a whole** over time, but can be misleading for **direct comparisons** between regions (because the baseline is not equal for all).

**Pedagogical note:**
If the objective is to compare regions individually, a better choice could be:

* Faceted line charts (one per region).
* Indexed line charts (normalize all regions to 100 in a base year).

**Example narrative:**

> *“Global growth in CO₂ emissions is driven mainly by Asia, while Europe and North America show relative stabilization.”*

---

✅ This visualization strengthens the storytelling by connecting **time dynamics with regional patterns**.

---
## 9. Global and Regional Maps  

### 9.1 Purpose of this visualization  
Maps provide a **geographical perspective** of emissions, showing **where** CO₂ per capita is higher or lower.  
They are effective for audiences who need to connect data with spatial context.  

Key insights from maps:  
- Regional contrasts (e.g., North America vs. Africa).  
- Clusters of high emissions.  
- Gaps in data availability (countries with missing values).  

---

### 9.2 Data preparation  
We merge the emissions dataset with ISO3 country codes and use Plotly Express to display maps.  

```python
map_data = dataset[dataset["year"] == 2022].copy()
```

---

### 9.3 Global map with Robinson projection

We use the **Robinson projection** because it:

* Balances distortions of area and shape.
* Produces a visually pleasing representation of the entire globe.
* Is widely used in thematic world maps.

```python
import plotly.express as px

fig_global = px.choropleth(
    map_data,
    locations="code",        # ISO3 country codes
    color="co2_pc",          # CO₂ per capita
    hover_name="country",
    hover_data={"gdp_pc": True, "pop": True},
    color_continuous_scale=["#7D8B94", "#A0B2A6", "#CFCFCF"],
    projection="robinson",
    title="Global CO₂ emissions per capita (2022)"
)
fig_global.show()
```

---

### 9.4 Regional zoom example

We can highlight a specific region (e.g., **North America**) by filtering the data.

```python
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
fig_region.show()
```

**Pedagogical note:**
To highlight another region, simply change the filter condition:

```python
map_data[map_data["region"] == "Europe"]
map_data[map_data["region"] == "Asia"]
map_data[map_data["region"] == "South America"]
```

Also update the **title** accordingly.

---

### 9.5 Storytelling element

Maps add **geographical storytelling** to the analysis:

* Global view → general patterns.
* Regional zoom → focus on local differences.

**Example narrative:**

> *“In 2022, CO₂ per capita was highest in North America, while Africa and South Asia showed much lower values. Zooming into regions highlights the disparities even more clearly.”*

---

✅ Maps are powerful for connecting **data and geography**, but require careful choice of projection and color scale to avoid misinterpretation.

---
## 10. Closing Notes  

### 10.1 Recap of the workflow  
This guide walked through the complete process of turning raw data into a **visual narrative**:  

1. **Context and libraries**  
   - Defined the dataset and installed/imported the required packages.  

2. **Data preparation**  
   - Cleaned missing values, filtered irrelevant codes, converted variables into categorical data.  
   - Produced a tidy dataset ready for visualization.  

3. **Global time series**  
   - Showed the weighted average of CO₂ emissions per capita across time.  
   - Highlighted key points (last year, minimum, maximum).  

4. **Country comparisons**  
   - Ranked and visualized the Top 10 emitters.  
   - Presented values both in absolute numbers and in billions for clarity.  

5. **Scatterplot (relationships)**  
   - Connected GDP per capita, CO₂ per capita, and population in one chart.  
   - Used log scaling and regional colors to reveal inequality.  

6. **Regional contributions**  
   - Stacked area chart showing how different regions drive global growth.  
   - Added lines to improve readability of regional trajectories.  

7. **Maps**  
   - Global choropleth with Robinson projection for balance.  
   - Regional zooms to focus on specific continents or subregions.  

---

### 10.2 Pedagogical notes  
- **Explanatory vs. exploratory**: the charts were designed to highlight **specific insights**, not just raw data.  
- **Storytelling elements**: each visualization emphasizes comparisons, key points, or spatial context.  
- **Design choices**: scales, color palettes, and projections are not neutral — they shape the narrative.  

---

### 10.3 How to extend the analysis  
Students can adapt the workflow by:  
- Changing the **ranking size** (Top 5, Top 20).  
- Selecting **different years** or time ranges.  
- Filtering for **specific regions** (e.g., Asia, Africa).  
- Modifying **color palettes** for accessibility (color-blind safe).  
- Experimenting with **other chart types** (line charts, faceted plots).  

---

### 10.4 Key takeaway  
Data visualization is not just about creating charts, but about **guiding the audience through a story** supported by evidence.  
Every design choice — chart type, color, scale, projection — plays a role in shaping how the message is perceived.  

> **Visualize with purpose, and let the data tell a story.**  

---
