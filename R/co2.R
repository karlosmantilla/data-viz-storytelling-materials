
dataset <- read.csv("Data/csv/consumption-co2-per-capita-vs-gdppc.csv", 
                         sep = ";", dec = ",")
summary(dataset)

library(dplyr)

names(dataset) <- c(
  'country','code','year','co2_pc','gdp_pc','pop','region'
)

dataset <- dataset %>% na.omit()

dataset %>% na.omit() %>% summary()
dataset %>% summary()

dataset <- dataset %>%
  mutate_if(is.character, factor)

dataset <- dataset %>%
  filter(
    code != "" & code != "OWID_WRL"
  )

dataset <- dataset %>% tibble()
dataset

library(ggplot2)

dataset %>%
  group_by(year) %>%
  summarise(
    co2 = sum(co2_pc * pop, na.rm = TRUE) / sum(pop, na.rm = TRUE),
    .groups = "drop"
  ) %>%
  mutate(
    marker = case_when(
      year == max(year) ~ "A",
      co2 == min(co2) ~ "B",
      co2 == max(co2) ~ "C",
      TRUE ~ "D"
    ),
    value = case_when(
      year == max(year) ~ co2,
      co2 == min(co2) ~ co2,
      co2 == max(co2) ~ co2,
      TRUE ~ NA_real_
    )
  ) %>%
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
        subtitle = paste(
          "Key points •",
          paste(
            subset(., marker %in% c("A","B","C")) %>%
              mutate(label = case_when(
                marker == "A" ~ paste0("Last: ", format(round(value,1), nsmall=1)),
                marker == "B" ~ paste0("Min: ",  format(round(value,1), nsmall=1), " (", year, ")"),
                marker == "C" ~ paste0("Max: ",  format(round(value,1), nsmall=1), " (", year, ")")
              )) %>%
              pull(label),
            collapse = " • "
          )
        )
      ) +
	  scale_y_continuous(expand = expansion(mult = c(0, 0.1))) +
      theme_minimal() +
  theme(
    legend.position = "none",
    plot.title = element_text(size = 16, face = "bold"),
    plot.subtitle = element_text(size = 12)
  )
  }

########################

library(dplyr)
library(ggplot2)

dataset %>%
  filter(year == max(year)) %>%
  group_by(country) %>%
  summarise(
    co2 = sum(co2_pc * pop, na.rm = TRUE),
    .groups = "drop"
  ) %>%
  slice_max(order_by = co2, n = 10) %>%
  mutate(pos_max = max(co2)) %>%
  ggplot(aes(x = reorder(country, co2), y = co2)) +
  geom_bar(stat = "identity", fill = "grey70") +
  # máximo dentro de la barra
  geom_text(
    data = ~filter(., co2 == max(co2)),
    aes(label = scales::comma(round(co2, 0))),
    hjust = 'right', color = "white", fontface = "bold"
  ) +
  # demás alineados en la vertical del máximo
  geom_text(
    data = ~filter(., co2 != max(co2)),
    aes(y = pos_max, label = scales::comma(round(co2, 0))),
    hjust = 'right'
  ) +
  coord_flip() +
  labs(
    x = NULL, y = NULL,
    title = bquote("Where most " ~ CO[2] ~ " comes from"),
    subtitle = "Top 10 emitters (absolute values -- selected period)"
  ) +
  scale_y_continuous(expand = expansion(mult = c(0, 0.15))) +
  theme_minimal() +
  theme(
    legend.position = "none",
    plot.title = element_text(size = 16, face = "bold"),
    plot.subtitle = element_text(size = 12),
    axis.text.x = element_blank(),
    axis.text.y = element_text(size = 12)
  )

####

library(dplyr)
library(ggplot2)
library(scales)

dataset %>%
  filter(year == max(year)) %>%
  group_by(country) %>%
  summarise(
    co2 = sum(co2_pc * pop, na.rm = TRUE),
    .groups = "drop"
  ) %>%
  slice_max(order_by = co2, n = 10) %>%
  mutate(
    pos_max = max(co2),
    co2_B   = co2 / 1e9   # convertir a miles de millones
  ) %>%
  ggplot(aes(x = reorder(country, co2), y = co2)) +
  geom_bar(stat = "identity", fill = "grey70") +
  # máximo dentro de la barra
  geom_text(
    data = ~filter(., co2 == max(co2)),
    aes(label = paste0(sprintf("%.1f", co2_B), " bn")),
    hjust = 1.1, color = "white", fontface = "bold", size = 4.5
  ) +
  # demás alineados a la derecha, en la vertical del máximo
  geom_text(
    data = ~filter(., co2 != max(co2)),
    aes(y = pos_max, label = paste0(sprintf("%.1f", co2_B), " bn")),
    hjust = "right"
  ) +
  coord_flip() +
  labs(
    x = NULL, y = NULL,
    title = bquote("Where most " ~ CO[2] ~ " comes from"),
    subtitle = "Top 10 emitters (absolute values -- last period)"
  ) +
  scale_y_continuous(
    expand = expansion(mult = c(0, 0.15)),
    labels = label_number(scale = 1e-9, suffix = "bn")
  ) +
  theme_minimal() +
  theme(
    legend.position = "none",
    plot.title = element_text(size = 16, face = "bold"),
    plot.subtitle = element_text(size = 12),
    axis.text.x = element_blank(),
    axis.text.y = element_text(size = 12)
  )

####################

library(scales)

dataset %>%
  filter(year == max(year)) %>%
  ggplot(aes(x = gdp_pc, y = co2_pc)) +
  geom_point(aes(size = pop, color = region), alpha = 0.7) +
  scale_x_log10(
    breaks = trans_breaks("log10", function(x) 10^x),
    labels = trans_format("log10", math_format(10^.x))
  ) +
  scale_color_manual(
    values = c(
      "Africa" = "#70B0E0",
      "Asia" = "#FCB714",
      "Europe" = "#2878BD",
      "North America" = "#0EB194",
      "Oceania" = "#108372",
      "South America" = "#AF916D"
    )
  ) +
  labs(
    x = "GDP per capita",
    y = bquote(CO[2] ~ " emissions per capita"),
    color = NULL,
    title = "Wealth, emissions and population combined",
    subtitle = "Worldwide - Entities: 120"
  ) +
  guides(size = "none") +
  theme_minimal() +
  theme(
    legend.justification = "top",
    legend.text = element_text(size = 12),
    legend.title = element_text(size = 12, face = "bold"),
    plot.title = element_text(size = 16, face = "bold"),
    plot.subtitle = element_text(size = 12),
    axis.text.x = element_text(size = 12),
    axis.text.y = element_text(size = 12)
  )

###################

dataset %>%
  group_by(year, region) %>%
  summarise(
    co2 = sum(co2_pc * pop, na.rm = TRUE),
    .groups = "drop"
  ) %>%
  ggplot(aes(x = year, y = co2, fill = region, color = region)) +
  geom_area(alpha = 0.65, position = position_stack(reverse = TRUE)) +
  geom_line(linewidth = 1, position = position_stack(reverse = TRUE)) +
  scale_fill_manual(
    values = c(
      "Africa" = "#70B0E0",
      "Asia" = "#FCB714",
      "Europe" = "#2878BD",
      "North America" = "#0EB194",
      "Oceania" = "#108372",
      "South America" = "#AF916D"
    )
  ) +
  scale_color_manual(
    values = c(
      "Africa" = "#70B0E0",
      "Asia" = "#FCB714",
      "Europe" = "#2878BD",
      "North America" = "#0EB194",
      "Oceania" = "#108372",
      "South America" = "#AF916D"
    ),
    guide = "none"   # ocultar la leyenda de líneas
  ) +
  labs(
    x = NULL,
    y = bquote(CO[2] ~ " emissions (absolute)"),
    fill = NULL,
    title = bquote("How regions drive global " ~ CO[2] ~ " growth"),
    subtitle = "Stacked area by region"
  ) +
  theme_minimal() +
  theme(
    legend.justification = "top",
    plot.title = element_text(size = 16, face = "bold"),
    plot.subtitle = element_text(size = 12),
    axis.text.x = element_text(size = 12),
    axis.text.y = element_text(size = 12)
  )

#############################

library(rnaturalearth)
library(sf)
library(ggplot2)
library(dplyr)

world <- ne_countries(scale = "medium", returnclass = "sf")

co2_map <- world %>%
  left_join(filter(dataset, year == 2022), by = c("adm0_a3" = "code"))

co2_map %>%
ggplot() +
  geom_sf(aes(fill = co2_pc), color = "#000000", size = 0.2) +
  scale_fill_gradientn(
    colors = c("#7D8B94", "#A0B2A6", "#CFCFCF"),
    na.value = "#333333"
  ) +
  coord_sf(crs = "+proj=robin") +
  theme_minimal() +
  theme(
    legend.position = "bottom",
    plot.title = element_text(size = 16, face = "bold"),
    axis.text = element_blank(),
    axis.ticks = element_blank()
  ) +
  labs(
    fill = bquote(CO[2] ~ " per capita"),
    title = bquote("Global " ~ CO[2] ~ " emissions per capita (2022)")
  )

####

ggplot() +
  geom_sf(
    data = co2_map,
    fill = "#F9F9F9", color = "#000000", size = 0.1
  ) +
  geom_sf(
    data = co2_map %>% filter(continent == "North America"),
    aes(fill = co2_pc), color = "#000000", size = 0.2
  ) +
  scale_fill_gradientn(
    colors = c("#7D8B94", "#A0B2A6", "#CFCFCF"),
    na.value = "#333333"
  ) +
  coord_sf(crs = "+proj=robin") +
  theme_minimal() +
  theme(
    legend.position = "bottom",
    plot.title = element_text(size = 16, face = "bold"),
    axis.text = element_blank(),
    axis.ticks = element_blank(),
    panel.grid = element_blank()
  ) +
  labs(
    fill = bquote(CO[2] ~ " per capita"),
    title = bquote("North America " ~ CO[2] ~ " emissions per capita (2022)")
  )

