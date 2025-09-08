# 📊 CO₂ Emissions and GDP per Capita – Data Visualization Guide

## 1. Introduction
This guide accompanies the R script for analyzing and visualizing the relationship between **CO₂ emissions per capita**, **GDP per capita**, and **population** across countries and regions.  
The workflow demonstrates how to move from raw data to **explanatory visualizations** that support storytelling.  

**Learning goals:**
- Practice data cleaning and transformation with `dplyr`.
- Explore different visualization types with `ggplot2`.
- Highlight key points (e.g., last year, min, max) in time series.
- Compare countries and regions using bar charts and stacked areas.
- Examine relationships with scatterplots.
- Map emissions data using spatial tools (`sf`, `rnaturalearth`).
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

- **dplyr** → Wrangling and transforming data (filter, group_by, summarise, mutate).  
- **ggplot2** → Creating static visualizations (bars, scatterplots, areas, maps).  
- **scales** → Formatting numbers and axes (commas, billions, log transformations).  
- **rnaturalearth** → Geographic boundaries of countries.  
- **sf** → Handling and visualizing spatial data in R.  

---

## 3. Installation and Loading

### Installation (only once per computer)
```r
install.packages(c("dplyr", "ggplot2", "scales", "rnaturalearth", "sf"))
````

### Load libraries (every session)

```r
library(dplyr)
library(ggplot2)
library(scales)
library(rnaturalearth)
library(sf)
```

👉 If a library is already installed, you only need the `library()` command.
👉 For advanced dependency management, consider using `pacman` or `renv`.

---

## 4. Loading and Preparing the Data  

Before creating visualizations, it is essential to **clean and prepare the dataset**. This ensures the analysis is consistent and avoids misleading results.  

### 4.1 Importing the dataset  
We use `read.csv()` (base R) to load the data. Note that in this case the file uses `;` as a separator and `,` as a decimal mark.  

```r
dataset <- read.csv("Data/csv/consumption-co2-per-capita-vs-gdppc.csv", 
                    sep = ";", dec = ",")
summary(dataset)
````

The `summary()` function provides a quick overview of the dataset.

---

### 4.2 Renaming variables

To make the script more readable, we rename the variables with shorter and clearer names.

```r
names(dataset) <- c(
  "country", "code", "year", "co2_pc", "gdp_pc", "pop", "region"
)
```

---

### 4.3 Handling missing values

It is important to remove rows with missing values (`NA`) to avoid inconsistencies in calculations.

```r
dataset <- dataset %>% na.omit()
```

We can also compare summaries **with and without NAs** to understand their impact:

```r
dataset %>% na.omit() %>% summary()
dataset %>% summary()
```

---

### 4.4 Converting variables

Text variables are transformed into **factors**, which are more efficient for grouping and analysis.

```r
dataset <- dataset %>% 
  mutate_if(is.character, factor)
```

---

### 4.5 Filtering irrelevant cases

We exclude records with missing country codes and the global aggregate (`OWID_WRL`) since they do not represent individual countries.

```r
dataset <- dataset %>% 
  filter(code != "" & code != "OWID_WRL")
```

---

### 4.6 Converting to tibble

Finally, we convert the dataset into a **tibble**, which is a modern and user-friendly data frame from the `tibble/dplyr` ecosystem.

```r
dataset <- dataset %>% tibble()
dataset
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

```r
dataset %>%
  group_by(year) %>%
  summarise(
    co2 = sum(co2_pc * pop, na.rm = TRUE) / sum(pop, na.rm = TRUE),
    .groups = "drop"
  )
````

Next, we use `mutate()` to flag key points in the series:

* **A = Last year**
* **B = Minimum value**
* **C = Maximum value**
* **D = Other years**

This classification allows us to add emphasis in the visualization.

---

### 5.3 Building the chart

We use a **bar chart** with custom colors for the markers.
Text labels highlight the exact values of the last, min, and max points.

```r
{ ggplot(., aes(x = year, y = co2)) +
    geom_bar(stat = "identity", aes(fill = marker)) +
    scale_fill_manual(values = c("A"="#1E88E5","B"="#43A047","C"="#E91E63","D"="#F9A825")) +
    geom_text(
      data = subset(., !is.na(value)),
      aes(label = format(round(value, 1), nsmall = 1)),
      vjust = -0.5
    ) +
    labs(
      x = "Year", y = NULL,
      title = bquote("Per Capita " ~ CO[2] ~ " Footprint"),
      subtitle = "Key points • Last • Min • Max"
    ) +
    scale_y_continuous(expand = expansion(mult = c(0, 0.1))) +
    theme_minimal() +
    theme(
      legend.position = "none",
      plot.title = element_text(size = 16, face = "bold"),
      plot.subtitle = element_text(size = 12)
    )
}
```

---

### 5.4 Storytelling element

The subtitle is **automatically generated** by concatenating the key values (Last, Min, Max).
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

```r
dataset %>%
  filter(year == max(year)) %>%
  group_by(country) %>%
  summarise(
    co2 = sum(co2_pc * pop, na.rm = TRUE),
    .groups = "drop"
  )
````

Next, we rank the countries and select the **Top 10** using `slice_max()`.
⚠️ **Pedagogical note:** the parameter `n = 10` can be modified depending on the narrative goal (Top 5, Top 20, or regional subsets).

---

### 6.3 Variant 1 – Absolute values

We display the total emissions as raw absolute numbers.

* The **largest emitter** is labeled inside its bar (bold, white text).
* Other countries are labeled **aligned to the maximum bar**, facilitating visual comparison.

```r
geom_text(
  data = ~filter(., co2 == max(co2)),
  aes(label = scales::comma(round(co2, 0))),
  hjust = "right", color = "white", fontface = "bold"
)
```

This approach emphasizes **the disproportionate weight of the top emitter** while still making other values readable.

---

### 6.4 Variant 2 – Values in billions (“bn”)

To improve readability for non-technical audiences, we transform emissions into **billions (× 1e9)**:

```r
mutate(co2_B = co2 / 1e9)
```

Labels are formatted as `"X.X bn"` for clarity:

```r
aes(label = paste0(sprintf("%.1f", co2_B), " bn"))
```

This reduces cognitive load and supports presentations where **round numbers** are easier to grasp.

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

```r
dataset %>%
  filter(year == max(year))
````

---

### 7.3 Building the scatterplot

* Use `geom_point()` to represent countries.
* Encode population (`size`) and region (`color`).
* Apply `scale_x_log10()` to handle the wide range of GDP values.
* Use a **manual color palette** to ensure visual consistency across all charts.

```r
ggplot(aes(x = gdp_pc, y = co2_pc)) +
  geom_point(aes(size = pop, color = region), alpha = 0.7) +
  scale_x_log10() +
  scale_color_manual(values = c("Africa"="#70B0E0","Asia"="#FCB714","Europe"="#2878BD",
                                "North America"="#0EB194","Oceania"="#108372","South America"="#AF916D"))
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

```r
dataset %>%
  group_by(year, region) %>%
  summarise(
    co2 = sum(co2_pc * pop, na.rm = TRUE),
    .groups = "drop"
  )
````

---

### 8.3 Building the stacked area chart

* `geom_area()` to display stacked contributions.
* `geom_line()` over the areas for better readability.
* Consistent color palette with previous visualizations (scatterplot).
* Labels emphasize that the Y-axis shows **absolute emissions**.

```r
ggplot(aes(x = year, y = co2, fill = region, color = region)) +
  geom_area(alpha = 0.65, position = position_stack(reverse = TRUE)) +
  geom_line(linewidth = 1, position = position_stack(reverse = TRUE)) +
  labs(
    x = NULL,
    y = expression(CO[2] ~ " emissions (absolute)"),
    title = expression("How regions drive global " ~ CO[2] ~ " growth"),
    subtitle = "Stacked area by region"
  )
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
We combine the emissions dataset with country boundaries from **Natural Earth**.  

```r
world <- ne_countries(scale = "medium", returnclass = "sf")

co2_map <- world %>%
  left_join(filter(dataset, year == 2022), by = c("adm0_a3" = "code"))
````

Here, `adm0_a3` is the ISO3 country code used in the shapefile.

---

### 9.3 Global map with Robinson projection

We use the **Robinson projection** (`+proj=robin`) because it:

* Balances distortions of area and shape.
* Produces a visually pleasing representation of the entire globe.
* Is widely used in thematic world maps.

```r
ggplot(co2_map) +
  geom_sf(aes(fill = co2_pc), color = "#000000", size = 0.2) +
  scale_fill_gradientn(
    colors = c("#7D8B94", "#A0B2A6", "#CFCFCF"),
    na.value = "#333333"
  ) +
  coord_sf(crs = "+proj=robin") +
  labs(
    fill = expression(CO[2] ~ " per capita"),
    title = expression("Global " ~ CO[2] ~ " emissions per capita (2022)")
  )
```

---

### 9.4 Regional zoom example

We can highlight a specific region (e.g., **North America**) by filtering the data.

```r
ggplot() +
  geom_sf(data = co2_map, fill = "#F9F9F9", color = "#000000", size = 0.1) +
  geom_sf(
    data = co2_map %>% filter(continent == "North America"),
    aes(fill = co2_pc), color = "#000000", size = 0.2
  ) +
  scale_fill_gradientn(
    colors = c("#7D8B94", "#A0B2A6", "#CFCFCF"),
    na.value = "#333333"
  ) +
  coord_sf(crs = "+proj=robin") +
  labs(
    fill = expression(CO[2] ~ " per capita"),
    title = expression("North America " ~ CO[2] ~ " emissions per capita (2022)")
  )
```

**Pedagogical note:**
To highlight another region, simply change the filter condition:

```r
filter(continent == "Europe")
filter(continent == "Asia")
filter(continent == "South America")
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
   - Defined the dataset and installed/loaded the required packages.  

2. **Data preparation**  
   - Cleaned missing values, filtered irrelevant codes, converted variables into factors.  
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
