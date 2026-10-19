#!/bin/bash
# ==============================================================================
# Kịch bản cài đặt tự động dịch vụ chạy 24/7 cho AI Agent Sàng Lọc CV
# Dành cho máy chủ Google Cloud Compute Engine (Ubuntu / Debian)
# ==============================================================================

set -e

SERVICE_NAME="ai-agent-cv-extract"
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CURRENT_USER="$(whoami)"
PYTHON_EXEC="$APP_DIR/.venv/bin/python"

echo "=========================================================="
echo "🚀 Đang thiết lập dịch vụ Systemd 24/7 cho: $SERVICE_NAME"
echo "📂 Thư mục làm việc: $APP_DIR"
echo "👤 Người dùng thực thi: $CURRENT_USER"
echo "=========================================================="

# 1. Khởi tạo môi trường ảo Python nếu chưa có
if [ ! -d "$APP_DIR/.venv" ]; then
    echo "📦 Đang khởi tạo môi trường ảo Python .venv..."
    python3 -m venv "$APP_DIR/.venv"
    "$APP_DIR/.venv/bin/pip" install --upgrade pip
    "$APP_DIR/.venv/bin/pip" install -r "$APP_DIR/requirements.txt"
fi

# 2. Tạo file cấu hình dịch vụ Systemd
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

echo "📝 Đang ghi nhận cấu hình dịch vụ vào $SERVICE_FILE..."
sudo bash -c "cat > $SERVICE_FILE" <<EOF
[Unit]
Description=AI Agent Sàng Lọc & Tuyển Dụng Nhân Sự 24/7
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$APP_DIR
ExecStart=$PYTHON_EXEC $APP_DIR/main.py
Restart=always
RestartSec=10
EnvironmentFile=$APP_DIR/.env

# Tối ưu hóa ghi log hệ thống
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# 3. Kích hoạt và khởi chạy dịch vụ
echo "🔄 Nạp lại danh sách dịch vụ hệ thống..."
sudo systemctl daemon-reload
echo "⭐ Đặt dịch vụ tự động khởi động cùng hệ thống khi khởi động lại máy chủ..."
sudo systemctl enable ${SERVICE_NAME}
echo "▶️ Bắt đầu chạy dịch vụ..."
sudo systemctl restart ${SERVICE_NAME}

echo "=========================================================="
echo "✅ DỊCH VỤ ĐÃ ĐƯỢC KÍCH HOẠT THÀNH CÔNG!"
echo "Kiểm tra trạng thái dịch vụ bằng lệnh:"
echo "  sudo systemctl status ${SERVICE_NAME}"
echo "Xem nhật ký chạy thực tế theo thời gian thực:"
echo "  sudo journalctl -u ${SERVICE_NAME} -f"
echo "=========================================================="
