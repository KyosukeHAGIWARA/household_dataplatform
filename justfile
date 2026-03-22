set shell := ["zsh", "-cu"]

run:
  streamlit run dashboard-front/app/main.py

poll:
  python dashboard-front/src/fetch_csv.py

worker-dev:
  cd depot-server && wrangler dev

lint:
  ruff check .
