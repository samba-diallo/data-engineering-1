#!/usr/bin/env bash
set -euo pipefail
echo "== Conda =="
command -v conda || echo "conda not on PATH"
conda --version || true
conda info --envs || true
echo "== Java =="
java -version || true
echo "== Python/PySpark =="
python -V || true
python -c "import pyspark; print('PySpark', pyspark.__version__)" || true
echo "== Spark smoke test =="
python verify_de1_env.py