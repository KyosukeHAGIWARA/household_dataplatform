# household_dataplatform

家計データのモニタリングダッシュボード。夫婦共有の家計データを可視化する個人用プロジェクト。

## アーキテクチャ概要

```
iPhone（家計アプリ）
  └─ CSVエクスポート
  └─ iOSショートカット → POST /upload
        ↓
Cloudflare Workers + KV（depot-server）
        ↓
Mac（dashboard-front/src/fetch_csv.py）
  └─ GET /files, GET /fetch/:key
  └─ dashboard-front/data/raw/*.csv に保存
        ↓
DuckDB（CSV直接クエリ）
        ↓
Streamlit ダッシュボード（dashboard-front）
```

## Cloudflare Workers (depot-server)

- 設定: `depot-server/wrangler.toml`
- エントリポイント: `depot-server/src/index.js`
- エンドポイント:
  - `POST /upload`
  - `GET /files`
  - `GET /fetch/:key`

## Streamlit (dashboard-front)

- エントリポイント: `dashboard-front/app/main.py`
- 認証: `streamlit-authenticator`（Secretsでユーザー/パスワードを管理）

## ディレクトリ構成

```
household_dataplatform/
├── depot-server/
│   ├── wrangler.toml
│   └── src/index.js
└── dashboard-front/
    ├── app/main.py
    ├── src/fetch_csv.py
    └── data/raw/        # 取得したCSV（gitignore）
```
