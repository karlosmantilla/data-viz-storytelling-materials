pkgs <- c("tidyverse", "ggplot2", "scales", "arrow", "readr", "readxl")
install.packages(setdiff(pkgs, rownames(installed.packages())))
