from __future__ import annotations

from pathlib import Path

import streamlit as st
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities.hasher import Hasher

try:
    from streamlit.errors import StreamlitSecretNotFoundError
except Exception:  # pragma: no cover
    StreamlitSecretNotFoundError = Exception  # type: ignore[assignment]

BASE_DIR = Path(__file__).resolve().parents[1]


def _load_auth_from_local_secrets_file() -> dict:
    secrets_path = BASE_DIR / ".streamlit/secrets.toml"
    if not secrets_path.exists():
        return {}

    import tomllib

    return tomllib.loads(secrets_path.read_text(encoding="utf-8"))


def _load_auth_settings() -> tuple[dict, str, str, int, set[str] | None]:
    try:
        auth = st.secrets.get("auth", {})
    except StreamlitSecretNotFoundError:
        local = _load_auth_from_local_secrets_file()
        auth = local.get("auth", {}) if isinstance(local, dict) else {}

    users = auth.get("usernames")
    cookie_name = auth.get("cookie_name")
    cookie_key = auth.get("cookie_key")
    cookie_expiry_days = auth.get("cookie_expiry_days")
    allowed_usernames = auth.get("allowed_usernames")

    if not isinstance(users, dict) or not cookie_name or not cookie_key or not cookie_expiry_days:
        st.error("認証設定が見つかりません（`st.secrets.auth`）。")
        st.code(
            """# dashboard-front/.streamlit/secrets.toml（ローカル）または SCC の Secrets に設定
[auth]
cookie_name = "household"
cookie_key = "CHANGE_ME_TO_A_LONG_RANDOM_SECRET"
cookie_expiry_days = 30

[auth.usernames.user1]
name = "user1"
email = "user1@example.com"
plain_password = "CHANGE_ME"
""",
            language="toml",
        )
        st.stop()

    if not isinstance(cookie_expiry_days, int):
        st.error("`auth.cookie_expiry_days` は int にしてください")
        st.stop()

    allowed: set[str] | None = None
    if isinstance(allowed_usernames, list):
        allowed = {str(u) for u in allowed_usernames}

    normalized_users: dict = {}
    for username, info in users.items():
        if not isinstance(info, dict):
            continue

        hashed_password = info.get("password")
        if not hashed_password:
            plain_password = info.get("plain_password")
            if plain_password:
                hashed_password = Hasher.hash(str(plain_password))

        if not hashed_password:
            st.error(
                f"認証設定が不完全です: auth.usernames.{username} に password または plain_password が必要です"
            )
            st.stop()

        normalized_users[str(username)] = {
            "name": info.get("name", str(username)),
            "email": info.get("email", ""),
            "password": hashed_password,
        }

    credentials = {"usernames": normalized_users}
    return credentials, str(cookie_name), str(cookie_key), cookie_expiry_days, allowed


st.set_page_config(page_title="Dashboard Front", layout="centered")

credentials, cookie_name, cookie_key, cookie_expiry_days, allowed = _load_auth_settings()
authenticator = stauth.Authenticate(
    credentials,
    cookie_name,
    cookie_key,
    cookie_expiry_days,
)

authenticator.login(location="main")

authentication_status = st.session_state.get("authentication_status")
username = st.session_state.get("username")
display_name = st.session_state.get("name")

if authentication_status is False:
    st.error("ユーザー名またはパスワードが違います")
    st.stop()
if authentication_status is None:
    st.warning("ログインしてください")
    st.stop()

if not isinstance(username, str):
    st.error("ログイン状態が不正です（username が取得できませんでした）")
    st.stop()

if allowed is not None and username not in allowed:
    st.error("このユーザーはアクセスできません")
    st.stop()

with st.sidebar:
    authenticator.logout("Logout")
    if display_name:
        st.caption(f"Logged in as: {display_name} ({username})")
    else:
        st.caption(f"Logged in as: {username}")

st.title("Hello, world")
st.write("dashboard-front is running locally.")

your_name = st.text_input("Your name", "")
if your_name:
    st.success(f"Hello, {your_name}!")

st.caption("Next: wire this app to depot-server.")
