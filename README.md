# household_dataplatform

ローカルで動く家計管理データ基盤の起動テンプレートです。

- UI: Streamlit
- ローカル分析DB: DuckDB
- ETL入口: Cloudflare Workers endpoint から取得して `dashboard-front/data/raw` にCSVを蓄積（手動/cron等で実行）
- 開発環境: Nix Flake

## Quickstart

```bash
nix develop
streamlit run dashboard-front/app/main.py
```

別ターミナルで Workers からCSV取得:

```bash
export WORKER_ENDPOINT="http://127.0.0.1:8787"  # wrangler dev の場合
python dashboard-front/src/fetch_csv.py
```

Workers をローカルで起動（開発用）:

```bash
cd depot-server
wrangler dev
```

## Files

- `flake.nix`: 開発シェル定義
- `pyproject.toml`: Python依存関係
- `dashboard-front/app/main.py`: Streamlitダッシュボード（認証付きHello World）
- `dashboard-front/src/fetch_csv.py`: WorkersからのCSV取得処理
- `depot-server/wrangler.toml`: Cloudflare Workers 設定
- `depot-server/src/index.js`: Cloudflare Worker（upload/files/fetch）
