#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
INSTALL_DIR="${INSTALL_DIR:-/opt/newsbot}"
ENV_FILE="${ENV_FILE:-/etc/newsbot.env}"
DB_DIR="${DB_DIR:-/var/lib/newsbot}"
SERVICE_NAME="newsbot"

ensure_env_key() {
  local key="$1"
  local default="${2-}"
  if [[ ! -f "$ENV_FILE" ]] || ! grep -q "^${key}=" "$ENV_FILE"; then
    printf '%s=%s\n' "$key" "$default" >> "$ENV_FILE"
  fi
}

if [[ "$(id -u)" -ne 0 ]]; then
  echo "run as root: sudo $0" >&2
  exit 1
fi

if ! id -u newsbot >/dev/null 2>&1; then
  useradd --system --home "$DB_DIR" --shell /usr/sbin/nologin newsbot
fi

apt-get update -qq
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq python3 python3-venv python3-pip rsync

mkdir -p "$INSTALL_DIR" "$DB_DIR"
rsync -a --delete \
  --exclude '.git' \
  --exclude '.venv' \
  --exclude '__pycache__' \
  --exclude '*.sqlite' \
  "$ROOT/" "$INSTALL_DIR/"

python3 -m venv "$INSTALL_DIR/.venv"
"$INSTALL_DIR/.venv/bin/pip" install -q --upgrade pip
"$INSTALL_DIR/.venv/bin/pip" install -q -r "$INSTALL_DIR/requirements.txt"

if [[ ! -f "$ENV_FILE" ]]; then
  umask 077
  touch "$ENV_FILE"
fi
ensure_env_key TELEGRAM_BOT_TOKEN
ensure_env_key TELEGRAM_CHAT_ID
ensure_env_key MAIL_TO
ensure_env_key SMTP_USER
ensure_env_key SMTP_PASSWORD
ensure_env_key SMTP_HOST
ensure_env_key SMTP_PORT
ensure_env_key SMTP_FROM
ensure_env_key SMTP_SECURITY
ensure_env_key TZ Asia/Shanghai
ensure_env_key NEWSBOT_DB /var/lib/newsbot/seen.sqlite
ensure_env_key LLM_API_KEY
ensure_env_key LLM_BASE_URL https://api.deepseek.com
ensure_env_key LLM_MODEL deepseek-chat

chown -R newsbot:newsbot "$INSTALL_DIR" "$DB_DIR"
chown root:newsbot "$ENV_FILE"
chmod 640 "$ENV_FILE"
chmod 750 "$INSTALL_DIR" "$DB_DIR"

install -m 644 "$ROOT/deploy/newsbot.service" /etc/systemd/system/newsbot.service
systemctl daemon-reload

mail_ready=0
tg_ready=0
if grep -qE '^MAIL_TO=.+' "$ENV_FILE" && grep -qE '^SMTP_PASSWORD=.+' "$ENV_FILE"; then
  mail_ready=1
fi
if grep -qE '^TELEGRAM_BOT_TOKEN=.+' "$ENV_FILE"; then
  tg_ready=1
fi

if [[ "$mail_ready" -eq 1 || "$tg_ready" -eq 1 ]]; then
  systemctl enable --now "$SERVICE_NAME"
  systemctl restart "$SERVICE_NAME"
  systemctl --no-pager --full status "$SERVICE_NAME" || true
else
  echo "MAIL_TO/SMTP_PASSWORD (or TELEGRAM_BOT_TOKEN) is empty; installed but not started."
  echo "Edit $ENV_FILE then: systemctl enable --now newsbot"
  echo "Send a digest immediately with: cd /opt/newsbot && sudo -u newsbot /opt/newsbot/.venv/bin/python -m newsbot --send"
fi
