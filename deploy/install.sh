#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
INSTALL_DIR="${INSTALL_DIR:-/opt/newsbot}"
ENV_FILE="${ENV_FILE:-/etc/newsbot.env}"
DB_DIR="${DB_DIR:-/var/lib/newsbot}"
SERVICE_NAME="newsbot"

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
  cat > "$ENV_FILE" <<'EOF'
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
TZ=Asia/Shanghai
NEWSBOT_DB=/var/lib/newsbot/seen.sqlite
LLM_API_KEY=
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
EOF
  chown root:newsbot "$ENV_FILE"
chmod 640 "$ENV_FILE"
echo "created $ENV_FILE — fill TELEGRAM_BOT_TOKEN (and TELEGRAM_CHAT_ID) then restart"
fi

chown -R newsbot:newsbot "$INSTALL_DIR" "$DB_DIR"
chown root:newsbot "$ENV_FILE"
chmod 640 "$ENV_FILE"
chmod 750 "$INSTALL_DIR" "$DB_DIR"

install -m 644 "$ROOT/deploy/newsbot.service" /etc/systemd/system/newsbot.service
systemctl daemon-reload

if grep -q '^TELEGRAM_BOT_TOKEN=.\+' "$ENV_FILE"; then
  systemctl enable --now "$SERVICE_NAME"
  systemctl restart "$SERVICE_NAME"
  systemctl --no-pager --full status "$SERVICE_NAME" || true
else
  echo "TELEGRAM_BOT_TOKEN is empty; service files installed but not started."
  echo "Edit $ENV_FILE then: systemctl enable --now newsbot"
fi
