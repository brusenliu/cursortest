#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NETDATA_SNIPPET_SRC="$ROOT/deploy/netdata.conf.snippet"
NGINX_SNIPPET_SRC="$ROOT/deploy/nginx-monitor.conf"
NETDATA_DROPIN="/etc/netdata/netdata.conf.d/lowmem.conf"
NGINX_SNIPPET="/etc/nginx/snippets/monitor-location.conf"
HTPASSWD_FILE="/etc/nginx/.htpasswd-monitor"
MARKER="# newsbot-monitor-include"

MONITOR_USER="${MONITOR_USER:-admin}"
MONITOR_PASSWORD="${MONITOR_PASSWORD:-}"

if [[ "$(id -u)" -ne 0 ]]; then
  echo "run as root: sudo $0" >&2
  exit 1
fi

echo "==> Installing Netdata (kickstart)..."
if ! command -v netdata >/dev/null 2>&1; then
  tmp_kickstart="$(mktemp)"
  curl -fsSL https://get.netdata.cloud/kickstart.sh -o "$tmp_kickstart"
  sh "$tmp_kickstart" --non-interactive --stable-channel --dont-wait
  rm -f "$tmp_kickstart"
else
  echo "Netdata already installed, skipping kickstart."
fi

echo "==> Applying low-memory Netdata config..."
mkdir -p /etc/netdata/netdata.conf.d
install -m 644 "$NETDATA_SNIPPET_SRC" "$NETDATA_DROPIN"
systemctl enable netdata
systemctl restart netdata

echo "==> Installing nginx basic-auth tools..."
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq nginx apache2-utils curl

echo "==> Creating monitor credentials..."
if [[ ! -f "$HTPASSWD_FILE" ]]; then
  if [[ -z "$MONITOR_PASSWORD" ]]; then
    echo "Set MONITOR_PASSWORD env var for non-interactive install, or enter a password now."
    htpasswd -c "$HTPASSWD_FILE" "$MONITOR_USER"
  else
    htpasswd -bc "$HTPASSWD_FILE" "$MONITOR_USER" "$MONITOR_PASSWORD"
  fi
else
  echo "Password file exists: $HTPASSWD_FILE (unchanged)"
fi
chmod 640 "$HTPASSWD_FILE"
chown root:www-data "$HTPASSWD_FILE" 2>/dev/null || chown root:nginx "$HTPASSWD_FILE" 2>/dev/null || true

echo "==> Configuring nginx reverse proxy for /monitor/ ..."
mkdir -p /etc/nginx/snippets
install -m 644 "$NGINX_SNIPPET_SRC" "$NGINX_SNIPPET"

include_site=""
for site in /etc/nginx/sites-enabled/*; do
  [[ -f "$site" ]] || continue
  if grep -qE 'listen[[:space:]]+80(\s|;|$)' "$site"; then
    include_site="$site"
    break
  fi
done

if [[ -z "$include_site" ]]; then
  include_site="/etc/nginx/sites-available/default"
  mkdir -p /etc/nginx/sites-enabled
  if [[ ! -f "$include_site" ]]; then
    cat >"$include_site" <<'EOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;
    root /var/www/html;
    index index.html;
    include /etc/nginx/snippets/monitor-location.conf;
    location / {
        try_files $uri $uri/ =404;
    }
}
EOF
    ln -sf "$include_site" /etc/nginx/sites-enabled/default
  fi
fi

if ! grep -q "$MARKER" "$include_site"; then
  if grep -q 'monitor-location.conf' "$include_site"; then
    echo "monitor-location.conf already referenced in $include_site"
  else
    sed -i "/^[[:space:]]*server[[:space:]]*{/a\\    include /etc/nginx/snippets/monitor-location.conf; ${MARKER}" "$include_site"
  fi
fi

nginx -t
systemctl enable nginx
systemctl reload nginx

echo
echo "Done."
echo "  Netdata:  http://127.0.0.1:19999 (localhost only)"
echo "  Monitor:  http://$(hostname -I | awk '{print $1}')/monitor/"
echo "  User:     $MONITOR_USER"
echo
echo "Verify:"
echo "  systemctl is-active netdata nginx"
echo "  curl -sI http://127.0.0.1:19999 | head -1"
