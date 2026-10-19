"""
Cấu hình cho Tác Nhân Giữ Ấm & Kích Hoạt Tự Động Supabase (Keep-Alive Agent).
Đảm bảo các cơ sở dữ liệu PostgreSQL trên Supabase không bị tạm ngưng sau 7 ngày không hoạt động.
"""

import os
from typing import List, Dict, Any
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Danh sách các dự án Supabase cần giữ ấm (định dạng URL|ANON_KEY|TABLE_TARGET, ngăn cách bởi dấu phẩy)
    # Ví dụ: https://xyz.supabase.co|your_anon_key|dim_employee
    supabase_targets_raw: str = Field(default="", env="SUPABASE_TARGETS")

    # Cấu hình chu kỳ kích hoạt (tính bằng giờ, mặc định mỗi 6 tiếng)
    ping_interval_hours: int = Field(default=6, env="PING_INTERVAL_HOURS")

    # Cấu hình Telegram nhận báo cáo định kỳ và cảnh báo khi dự án bị lỗi
    telegram_bot_token: str = Field(default="", env="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: str = Field(default="", env="TELEGRAM_CHAT_ID")

    # Tùy chọn đồng bộ kết quả kiểm tra vào Google Sheets
    google_sheet_id: str = Field(default="", env="GOOGLE_SHEET_ID")
    google_service_account_file: str = Field(default="credentials.json", env="GOOGLE_SERVICE_ACCOUNT_FILE")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
