# Contributing

## Branches
- `main`: stable  
- `dev`: integration branch for new features and fixes  

## Pull Requests
1. Create a feature branch from `dev` (e.g., `feat/...`, `fix/...`, `docs/...`).  
2. Follow the PR checklist and ensure the *Smoke test* passes.  
3. Use descriptive commits following conventional format (`feat:`, `fix:`, `docs:`).  

## Coding Standards
- **R**: use `linewidth` in `geom_*`; apply the accessible palette.  
- **Python**: use `pandas` + `matplotlib`; avoid forcing custom styles beyond `uis.mplstyle`.  

## How to Run
- **R**:  
  ```bash
  Rscript R/01_fast_load.R
