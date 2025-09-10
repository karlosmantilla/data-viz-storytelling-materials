##########################################################
# Fertility and Population Growth – Data Exploration and Visualization
# Author: Carlos Alfonso Mantilla Duarte
# Date: 2025-10-03
# Description:
#   This script demonstrates how to import, clean, and visualize
#   fertility and population growth data from Our World in Data.
#   It includes examples of:
#     - Data cleaning and variable renaming
#     - Merging reference tables
#     - Summarizing categorical variables
#     - Visualizing with maps, bar charts, and scatterplots
##########################################################

#---------------------------------------------------------
# Load required libraries
#---------------------------------------------------------

library(tidyverse)     # Collection of R packages (dplyr, readr, tidyr, etc.) 
                       # for data manipulation, cleaning, and wrangling.

library(rnaturalearth) # Provides Natural Earth vector map data 
                       # (country borders, coastlines, etc.) for mapping.

library(sf)            # Simple Features package for handling spatial data 
                       # (shapefiles, polygons, geometry operations).

library(ggplot2)       # Grammar of Graphics framework for creating 
                       # customizable, layered data visualizations.

library(forcats)       # Part of tidyverse, focused on handling factors 
                       # (categorical variables), useful for reordering levels.

library(scales)        # Provides scaling functions for ggplot2 
                       # (e.g., formatting numbers, percentages, custom axes).


#---------------------------------------------------------
# 1. Load the dataset
#---------------------------------------------------------

# Use read_csv with explicit options for better control:
# - col_types = cols() to avoid guessing column types
# - na = c("", "NA") to handle missing values consistently
fertility <- read_csv(
  "Data/csv/children-per-woman-vs-population-growth.csv",
  col_types = cols(),
  na = c("", "NA")
)

# Preview the structure of the dataset as a tibble
fertility %>% tibble()

#---------------------------------------------------------
# 2. Rename variables for clarity and consistency
#---------------------------------------------------------

# Rename columns to shorter, English-friendly names
fertility <- fertility %>%
  rename(
    country     = Entity,
    code        = Code,
    year        = Year,
    growth      = `Natural population growth rate - Sex: all - Age: all - Variant: estimates`,
    fertility   = `Fertility rate - Sex: all - Age: all - Variant: estimates`,
    population  = `Population (historical)`,
    continent   = `World regions according to OWID`
  )

#---------------------------------------------------------
# 3. Quick summary of the dataset
#---------------------------------------------------------

# Convert character variables to factors and produce summary statistics
fertility %>%
  mutate_if(is.character, factor) %>%
  summary()

#---------------------------------------------------------
# 4. Create a continent reference
#---------------------------------------------------------

# Extract the most recent non-missing continent reference for each country
continents_ref <- fertility %>%
  filter(!is.na(continent)) %>%
  distinct(country, continent)

# Merge continent information back into the full dataset
fertility <- fertility %>%
  select(-continent) %>%
  left_join(continents_ref, by = "country") %>%
  filter(!is.na(continent))

#---------------------------------------------------------
# 5. Choropleth map of fertility rate
#---------------------------------------------------------

# Load world map from Natural Earth
world <- ne_countries(scale = "medium", returnclass = "sf")

# Join fertility data (for a single year, e.g., 2023)
fert_map <- world %>%
  left_join(filter(fertility, year == 2023), by = c("iso_a3" = "code"))

# Plot fertility rates on the map
ggplot(fert_map) +
  geom_sf(aes(fill = fertility)) +
  scale_fill_viridis_c(option = "plasma", na.value = "gray90") +
  theme_minimal() +
  labs(
    title = "Fertility Rate by Country (2023)",
    fill  = "Children per Woman"
  )

#---------------------------------------------------------
# 6. Bar chart: number of countries by continent
#---------------------------------------------------------

fertility %>%
  filter(year == 2020) %>%
  group_by(continent) %>%
  summarise(n_countries = n_distinct(country)) %>%
  ggplot(aes(x = fct_reorder(continent, n_countries), y = n_countries)) +
  geom_col(fill = "#4682B4") +
  coord_flip() +
  labs(
    title = "Number of Countries by Continent",
    x     = "Continent",
    y     = "Number of Countries"
  ) +
  theme_minimal()

#---------------------------------------------------------
# 7. Scatterplot: fertility vs. population growth
#---------------------------------------------------------

fertility %>%
  filter(year == 2023) %>%
  ggplot(aes(x = fertility, y = growth, color = continent)) +
  geom_point(aes(size = population), alpha = 0.7) +
  scale_size_continuous(
    range  = c(1, 10),
    labels = label_number(scale_cut = cut_short_scale())
  ) +
  labs(
    title = "Relationship Between Fertility and Population Growth (2023)",
    x     = "Fertility Rate",
    y     = "Population Growth Rate (%)",
    size  = "Population",
    color = "Continent"
  ) +
  theme_minimal()
