pkgs <- c("arrow","readr","ggplot2")
install.packages(setdiff(pkgs, rownames(installed.packages())))
