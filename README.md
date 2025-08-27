# Data Visualization & Storytelling · Teaching Kit

Ready-to-use teaching materials for Power BI, R, and Python.  
Focused on visual design, narrative clarity, and accessibility.  
Optimized for short sessions with guided practice.

## Repository Goal
Help students build confidence in turning data into clear and compelling stories.  
Provide ready-to-use resources that minimize technical setup so class time can focus on design choices and communication.  
Encourage consistent use of visual patterns, accessible palettes, and narrative techniques across different tools.  

## Audience & Scope
This course is designed for undergraduate students from any area of study who have a basic knowledge of statistics and wish to enhance their ability to communicate data effectively.  
6 hours total.  
Hands-on practice with portable datasets and templates.  


## How to Get the Materials
Preferred: download the ZIP from the latest release.  
Path: Releases → “DVST_Kit_vX.Y.zip”.  
Alternative: clone the repo with Git LFS enabled for large binaries.

## Requirements

- **Power BI Desktop** (Windows, latest version)  
  🔗 [Download](https://www.microsoft.com/en-us/download/details.aspx?id=58494)  

- **R** (latest release) with `arrow` and `readr`  
  🔗 [Download R](https://cloud.r-project.org/)  
  🔗 [Download RStudio](https://posit.co/download/rstudio-desktop/)  

- **Python 3.10+** with `pandas` and `pyarrow` or `fastparquet`  
  🔗 [Download Python](https://www.python.org/downloads/)  
  🔗 You may also use [Anaconda with Jupyter](https://www.anaconda.com/download), or another compatible environment  

- **QGIS** (for optional GIS exercises)  
  🔗 [Download QGIS](https://qgis.org/download/)  

- **Git LFS** (for `*.pbix`, `*.feather`, `*.parquet`, `*.qgz`)  
  🔗 [Git LFS setup guide](https://git-lfs.com/)  


## Quick Start

### Power BI (3 steps)
Open `PBIX/00_Basics.pbix`.  
Confirm data loads without credentials (local sources).  
Explore bookmarks “Overview”, “Focus”, “Insight” in the nav bar.

### R (3 steps)
Open `R/01_fast_load.R`.  
Run and check that `fert`, `origin`, and `variable_dictionary` are in memory.  
Use `R/02_visual_patterns.R` to create base charts (with updated `linewidth`).

### Python (3 steps)
Open `Python/01_fast_load.ipynb`.  
Run cells to load `parquet/feather` and apply `utils/uis.mplstyle`.  
Try patterns in `02_visual_patterns.ipynb` (bars, lines, dotplots, small multiples).

## Repository Structure
`PBIX/` ready files and templates with navigation and narrative tooltips.  
`Data/` portable formats (RData, RDS, Parquet, Feather, CSV) and `variable_dictionary.csv`.  
`R/` scripts for loading, visual patterns, and storytelling tips (`theme_uis.R`, `palette_accessible.R`).  
`Python/` notebooks and utils (`palette_accessible.py`, `uis.mplstyle`).  
`Themes/` JSON themes for Power BI and shared styles.  
`GIS/` `countries.geojson`, `colombia_departments.geojson`, and a base QGIS project.  
`Docs/` quick guides, class checklist, licenses, credits.  
`.github/` smoke-test workflow and issue/discussion templates.

## Visual Storytelling Patterns
Use a **title** with an explicit insight (what happened, where).  
Add a **subtitle** for context and period.  
Include **source notes** and key definitions.  
Annotate directly on the chart to point at the insight.  
Use color to highlight 1–2 elements; keep the rest neutral.  
Avoid 3D, heavy backgrounds, and unnecessary axes.

## Accessibility & Consistency
Color-blind-safe palette defined in `Themes/` and utilities in R/Python.  
Minimum AA text contrast; consistent type scale and hierarchy.  
Selective data labels (top or filtered elements) and informative tooltips.  
Alt-text for exported images and descriptions for key Power BI visuals.

## Frictionless Data Loading
R: `load("Data/portable/Data_R.RData")` or `readRDS("Data/portable/fert.rds")`.  
Python: `pd.read_parquet("Data/portable/fert.parquet")` or `pd.read_feather("Data/portable/fert.feather")`.  
CSV: UTF-8, comma delimiter, dot decimals, ISO-8601 dates.  
GIS: ISO3/DANE keys prepared for quick joins.

## Classroom Good Practices
Work with relative paths; don’t overwrite portables.  
Copy templates to a personal folder before editing.  
Log design and message decisions in each exercise’s README.  
Version only lightweight student outputs (scripts/notebooks).

## Licenses & Credits
Code: MIT (`Docs/LICENSE-CODE.txt`).  
Content (docs, images, templates): CC BY-NC 4.0 (`Docs/LICENSE-CONTENT.txt`).  
Cite data sources in `Docs/CREDITS.md` and in final visuals.

## Bibliography
The complete list of references and recommended readings is available in [bibliography.md](./bibliography.md).

## Contributing & Support
Open a **Class question** in Issues for specific doubts.  
Share results in Discussions → **Show and tell**.  
All contributions go via PR to `dev`; smoke test must pass before merging to `main`.

## Verification & Releases
“Smoke test (R/Python data load)” validates minimal loads.  
Releases include `SHA256SUMS.txt` for integrity checks.  
CHANGELOG maintained in each release’s notes.

## Contact
For class support use Issues/Discussions.  
For improvements, submit a PR with the checklist.
