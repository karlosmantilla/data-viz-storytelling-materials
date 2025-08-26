# Contributing
## Branches
- `main`: estable · `dev`: integración.
## Pull requests
1) Crea rama desde `dev` (feat/fix/docs).
2) Sigue el checklist del PR y pasa el *Smoke test*.
3) Usa commits descriptivos (convencional: feat:, fix:, docs:).
## Coding standards
- R: `linewidth` en `geom_*`, paleta accesible.
- Python: `pandas` + `matplotlib`, sin estilos forzados.
## How to run
- R: `Rscript R/01_fast_load.R`
- Python: `python -c "import pandas as pd; pd.read_parquet('Data/portable/fert.parquet')"`
