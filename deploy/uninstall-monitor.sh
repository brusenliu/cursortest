#!/usr/bin/env bash
set -euo pipefail

NGINX_SNIPPET="/etc/nginx/snippets/monitor-location.conf"
HTPASSWD_FILE="/etc/nginx/.htpasswd-monitor"
NETDATA_DROPIN="/etc/netdata/netdata.conf.d/lowmem.conf"
NETDATA_MARKER="# newsbot-lowmem-config"
NGINX_MARKER="# newsbot-monitor-include"
CREDENTIALS_FILE="/root/monitor-access.txt"

if [[ "$(id -u)" -ne 0 ]]; then
  echo "run as root: sudo $0" >&2
  exit 1
fi

echo "==> Removing nginx /monitor/ reverse proxy..."
for site in /etc/nginx/sites-enabled/* /etc/nginx/sites-available/*; do
  [[ -f "$site" ]] || continue
  if grep -q 'monitor-location.conf\|newsbot-monitor-include' "$site"; then
    sed -i '/monitor-location.conf/d' "$site"
    sed -i '/newsbot-monitor-include/d' "$site"
    echo "  cleaned $site"
  fi
done
rm -f "$NGINX_SNIPPET" "$HTPASSWD_FILE"

if command -v nginx >/dev/null 2>&1; then
  nginx -t
  systemctl reload nginx
fi

echo "==> Uninstalling Netdata..."
if command -v netdata >/dev/null 2>&1 || dpkg -l netdata >/dev/null 2>&1; then
  tmp_kickstart="$(mktemp)"
  if curl -fsSL https://get.netdata.cloud/kickstart.sh -o "$tmp_kickstart"; then
    sh "$tmp_kickstart" --uninstall --non-interactive --yes || true
    rm -f "$tmp_kickstart"
  fi
  DEBIAN_FRONTEND=noninteractive apt-get purge -y -qq \
    netdata netdata-dashboard netdata-plugin-* netdata-user netdata-repo 2>/dev/null || true
  DEBIAN_FRONTEND=noninteractive apt-get autoremove -y -qq 2>/dev/null || true
  rm -rf /var/lib/netdata /var/cache/netdata /etc/netdata
fi

rm -f "$CREDENTIALS_FILE"

echo
echo "Done. Monitor removed."
echo "  nginx:  systemctl is-active nginx"
echo "  netdata: should be inactive / not installed"
