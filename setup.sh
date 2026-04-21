#!/bin/bash
set -euo pipefail

die() { echo "ERROR: $*" >&2; exit 1; }
info() { echo "==> $*"; }

if [[ ${EUID:-$(id -u)} -ne 0 ]]; then
  die "Run as root: sudo $0"
fi

command -v apt >/dev/null 2>&1 || die "This script expects Debian/Raspberry Pi OS (apt)."

info "Running apt update..."
export DEBIAN_FRONTEND=noninteractive
apt update -y

info "Installing Kiwix (the kiwix-serve binary comes from the kiwix-tools package)..."
apt install -y --no-install-recommends kiwix-tools ca-certificates

info "Verifying installation..."
command -v kiwix-serve >/dev/null 2>&1 || die "kiwix-serve was not found after installation."

KIWIX_PORT="${KIWIX_PORT:-8080}"
ZIM_DIR="${ZIM_DIR:-/srv/kiwix/content}"

info "Ensuring ZIM directory exists: ${ZIM_DIR}"
mkdir -p "${ZIM_DIR}"

if ! command -v systemctl >/dev/null 2>&1; then
  die "systemctl not found. This script expects a systemd-based OS."
fi

setup_kiwix_systemd_service() {
  info "Creating/Updating kiwix-serve systemd service..."
  cat >/etc/default/kiwix-serve <<EOF
KIWIX_PORT=${KIWIX_PORT}
ZIM_DIR=${ZIM_DIR}
EOF

  cat >/etc/systemd/system/kiwix-serve.service <<EOF
[Unit]
Description=Kiwix offline content server
After=network-online.target
Wants=network-online.target
ConditionPathExistsGlob=${ZIM_DIR}/*.zim

[Service]
Restart=always
RestartSec=15
ExecStart=/usr/bin/bash -c "/usr/bin/kiwix-serve -p ${KIWIX_PORT} ${ZIM_DIR}/*.zim"

[Install]
WantedBy=multi-user.target
EOF

  systemctl daemon-reload
  systemctl enable kiwix-serve >/dev/null
}

service_is_active() {
  systemctl is-active --quiet kiwix-serve.service
}

zim_present() {
  compgen -G "${ZIM_DIR}/*.zim" >/dev/null
}

start_or_restart_kiwix() {
  if ! zim_present; then
    info "No .zim files found in ${ZIM_DIR}. Not starting kiwix-serve yet."
    info "Tip: re-run this script and answer 'y' to download a ZIM (or copy your own .zim files)."
    return 0
  fi

  if service_is_active; then
    info "kiwix-serve is already running; restarting it to apply changes..."
    systemctl restart kiwix-serve.service
  else
    info "Starting kiwix-serve..."
    systemctl start kiwix-serve.service
  fi
}

ensure_curl() {
  if ! command -v curl >/dev/null 2>&1; then
    info "curl not found; installing curl..."
    apt install -y --no-install-recommends curl
  fi
}

install_pmtiles() {
  if command -v pmtiles >/dev/null 2>&1; then
    info "pmtiles already installed."
    return
  fi
  info "Installing pmtiles CLI..."
  ensure_curl
  local version="1.22.3"
  local arch
  case "$(uname -m)" in
    aarch64|arm64) arch="arm64" ;;
    armv7l|armv6l) arch="arm"   ;;
    x86_64)        arch="x86_64" ;;
    *) die "Unsupported architecture for pmtiles: $(uname -m)" ;;
  esac
  curl -fsSL "https://github.com/protomaps/go-pmtiles/releases/download/v${version}/go-pmtiles_${version}_Linux_${arch}.tar.gz" \
    | tar xz -C /usr/local/bin pmtiles
  chmod +x /usr/local/bin/pmtiles
  info "pmtiles installed."
}


setup_kiwix_systemd_service

start_or_restart_kiwix

if zim_present && service_is_active; then
  info "Kiwix is running on port ${KIWIX_PORT} (serving ZIMs from ${ZIM_DIR})."
else
  info "Kiwix is not running yet (it requires at least one .zim in ${ZIM_DIR})."
fi

# ── Dashboard ──────────────────────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DASHBOARD_SRC="${SCRIPT_DIR}/dashboard"
DASHBOARD_DEST="/opt/gridlib/dashboard"
DASHBOARD_PORT="${DASHBOARD_PORT:-9080}"
NVM_DIR="${HOME}/.nvm"

load_nvm() {
  export NVM_DIR="${NVM_DIR}"
  # shellcheck source=/dev/null
  . "${NVM_DIR}/nvm.sh"
}

install_node() {
  if [[ -s "${NVM_DIR}/nvm.sh" ]]; then
    info "nvm already installed, loading..."
    load_nvm
  else
    info "Installing nvm..."
    ensure_curl
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.4/install.sh | bash
    load_nvm
  fi

  if command -v node >/dev/null 2>&1; then
    info "Node.js already installed: $(node -v)"
  else
    info "Installing Node.js 24..."
    nvm install 24
  fi

  if ! command -v yarn >/dev/null 2>&1; then
    info "Enabling Yarn via corepack..."
    corepack enable yarn
  fi

  info "Node $(node -v) · Yarn $(yarn -v)"
}

install_dashboard() {
  info "Installing GridLib dashboard..."

  install_node
  install_pmtiles

  # Install nginx if missing
  if ! command -v nginx >/dev/null 2>&1; then
    info "Installing nginx..."
    apt install -y --no-install-recommends nginx
  fi

  # Build the Vue project on the Pi
  info "Building dashboard (this may take a minute)..."
  (
    cd "${DASHBOARD_SRC}"
    load_nvm
    yarn install --frozen-lockfile
    yarn build
  )

  # Copy built dist, Python services, and collections
  mkdir -p "${DASHBOARD_DEST}" /opt/gridlib/collections
  cp -r "${DASHBOARD_SRC}/dist/."           "${DASHBOARD_DEST}/"
  cp "${DASHBOARD_SRC}/generate-status.py"  "${DASHBOARD_DEST}/generate-status.py"
  cp "${DASHBOARD_SRC}/api.py"              "${DASHBOARD_DEST}/api.py"
  cp "${SCRIPT_DIR}/collections/"*.json     /opt/gridlib/collections/
  chmod +x "${DASHBOARD_DEST}/generate-status.py" "${DASHBOARD_DEST}/api.py"

  # Generate initial status.json before starting the daemon
  if [[ ! -f "${DASHBOARD_DEST}/status.json" ]]; then
    info "Generating initial status snapshot..."
    ZIM_DIR="${ZIM_DIR}" timeout 3 python3 "${DASHBOARD_DEST}/generate-status.py" 2>/dev/null || true
  fi

  # Create map storage directory
  mkdir -p /srv/gridlib/maps

  # nginx site config — serves static files + proxies /api/ to api.py (port 9081)
  cat >/etc/nginx/sites-available/gridlib <<EOF
server {
    listen ${DASHBOARD_PORT};
    server_name _;

    root ${DASHBOARD_DEST};
    index index.html;

    location = /status.json {
        add_header Cache-Control "no-store";
        add_header Pragma "no-cache";
        etag off;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:9081/;
        proxy_set_header Host \$host;
        proxy_read_timeout 10s;
    }

    location /maps/ {
        alias /srv/gridlib/maps/;
        add_header Access-Control-Allow-Origin "*";
        add_header Accept-Ranges bytes;
    }

    location / {
        try_files \$uri \$uri/ /index.html;
    }
}
EOF

  ln -sf /etc/nginx/sites-available/gridlib /etc/nginx/sites-enabled/gridlib
  rm -f /etc/nginx/sites-enabled/default

  nginx -t && systemctl reload nginx || systemctl restart nginx
  systemctl enable nginx >/dev/null

  # Systemd service — status generator (writes status.json every 15s)
  cat >/etc/systemd/system/gridlib-status.service <<EOF
[Unit]
Description=GridLib status generator
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 ${DASHBOARD_DEST}/generate-status.py
Environment=ZIM_DIR=${ZIM_DIR}
Environment=GRIDLIB_INTERVAL=15
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

  # Systemd service — API server (handles downloads, port 9081)
  cat >/etc/systemd/system/gridlib-api.service <<EOF
[Unit]
Description=GridLib API server
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 ${DASHBOARD_DEST}/api.py
Environment=ZIM_DIR=${ZIM_DIR}
Environment=MAPS_DIR=/srv/gridlib/maps
Environment=GRIDLIB_COLLECTIONS_DIR=/opt/gridlib/collections
Environment=GRIDLIB_API_PORT=9081
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

  systemctl daemon-reload
  systemctl enable gridlib-status gridlib-api >/dev/null
  systemctl restart gridlib-status gridlib-api

  info "Dashboard installed!"
  info "  URL: http://10.3.141.1:${DASHBOARD_PORT}"
}

install_dashboard
