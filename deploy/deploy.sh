#!/usr/bin/env bash
# ==============================================================================
# The Chronicle — Zero-Downtime Deployment Script
# ==============================================================================
set -euo pipefail

APP_DIR="/var/www/chronicle"
VENV_DIR="$APP_DIR/env"
PYTHON="$VENV_DIR/bin/python"
PIP="$VENV_DIR/bin/pip"
SERVICE_NAME="chronicle.service"

echo "=========================================="
echo "🚀 Starting The Chronicle Deployment..."
echo "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="

cd "$APP_DIR"

# 1. Fetch Latest Code
echo "📥 Pulling latest release from Git repository..."
git fetch origin main
git reset --hard origin/main

# 2. Activate Virtual Environment & Update Dependencies
echo "📦 Synchronizing Python dependencies..."
"$PIP" install --upgrade pip
"$PIP" install -r requirements.txt --quiet

# 3. Apply Database Migrations
echo "🗄️ Applying pending database migrations..."
"$PYTHON" manage.py migrate --noinput

# 4. Collect & Compress Static Assets
echo "🎨 Collecting and hashing static assets..."
"$PYTHON" manage.py collectstatic --noinput --clear

# 5. Reload Application Process (Zero-Downtime Graceful Reload)
echo "🔄 Reloading Gunicorn application workers..."
sudo systemctl reload "$SERVICE_NAME" || sudo systemctl restart "$SERVICE_NAME"

# 6. Verify Service Status
echo "🔍 Verifying application service health..."
sudo systemctl is-active --quiet "$SERVICE_NAME" && echo "✅ Service is ACTIVE and running." || {
    echo "❌ ERROR: Service failed to start. Review logs with: journalctl -u $SERVICE_NAME -n 50"
    exit 1
}

echo "=========================================="
echo "🎉 Deployment successfully completed!"
echo "=========================================="
