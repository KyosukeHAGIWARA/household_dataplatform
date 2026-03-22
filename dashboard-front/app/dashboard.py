from __future__ import annotations

import os
from pathlib import Path

import duckdb
import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[1]

CSV_GLOB = os.getenv(
    "HOUSEHOLD_CSV_GLOB",
    (BASE_DIR / "data/raw/*.csv").as_posix(),
)
DUCKDB_PATH = os.getenv(
    "HOUSEHOLD_DUCKDB_PATH",
    (BASE_DIR / "data/household.duckdb").as_posix(),
)

st.set_page_config(page_title="Household Data Platform", layout="wide")
st.title("Household Data Platform")
st.caption("DuckDB + Streamlit CSV query")

csv_files = sorted((BASE_DIR / "data/raw").glob("*.csv"))
if not csv_files:
    st.warning("`data/raw` にCSVファイルが見つかりませんでした。")
    st.stop()

Path(DUCKDB_PATH).parent.mkdir(parents=True, exist_ok=True)
conn = duckdb.connect(DUCKDB_PATH)
source = f"read_csv_auto('{CSV_GLOB}', header=true, union_by_name=true, filename=true)"

count = conn.execute(f"SELECT COUNT(*) FROM {source}").fetchone()[0]
st.metric("Raw rows", count)

st.subheader("カテゴリ別合計")
sql = f"""
SELECT
    \"カテゴリ\",
    SUM(TRY_CAST(\"金額\" AS DOUBLE)) AS 合計
FROM {source}
WHERE TRY_CAST(\"支出に含める\" AS INTEGER) = 1
GROUP BY \"カテゴリ\"
ORDER BY 合計 DESC
"""
st.code(sql.strip(), language="sql")
summary_df = conn.execute(sql).fetchdf()
st.dataframe(summary_df, use_container_width=True)

st.subheader("Raw preview")
preview_df = conn.execute(f"SELECT * FROM {source} LIMIT 100").fetchdf()
st.dataframe(preview_df, use_container_width=True)

conn.close()
