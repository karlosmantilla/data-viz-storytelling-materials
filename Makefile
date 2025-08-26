.PHONY: setup smoke format

setup:
\tRscript install.R
\tpython -m pip install -r requirements.txt

smoke:
\tpython - <<'PY'\nimport pandas as pd; pd.read_parquet('Data/portable/fert.parquet'); print('OK Python')\nPY
\tRscript -e "if (file.exists('Data/portable/Data_R.RData')) load('Data/portable/Data_R.RData'); cat('OK R\\n')"

format:
\truff check --fix || true
