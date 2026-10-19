"""
Cấu hình hệ thống cho AI Agent Trích Xuất & Sàng Lọc CV Tuyển Dụng.
Quản lý các tham số môi trường, khóa API và đường dẫn tài nguyên.
"""

import os
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Khóa kết nối Google AI Studio (Gemini 2.5 Flash)
    gemini_api_key: str = Field(default="", env="GEMINI_API_KEY")
    ai_model_name: str = Field(default="gemini-2.5-flash", env="AI_MODEL_NAME")

    # Cấu hình Google Sheets & Drive
    google_service_account_file: str = Field(
        default="credentials.json", env="GOOGLE_SERVICE_ACCOUNT_FILE"
    )
    google_sheet_id: str = Field(default="", env="GOOGLE_SHEET_ID")
    google_sheet_name: str = Field(default="Ứng Viên Tuyển Dụng", env="GOOGLE_SHEET_NAME")
    drive_incoming_folder_id: str = Field(default="", env="DRIVE_INCOMING_FOLDER_ID")
    drive_talent_pool_folder_id: str = Field(default="", env="DRIVE_TALENT_POOL_FOLDER_ID")

    # Cấu hình thông báo Telegram
    telegram_bot_token: str = Field(default="", env="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: str = Field(default="", env="TELEGRAM_CHAT_ID")

    # Chu kỳ quét tự động (tính bằng phút)
    polling_interval_minutes: int = Field(default=10, env="POLLING_INTERVAL_MINUTES")

    # Đường dẫn cục bộ lưu trữ file tạm
    temp_dir: Path = Path(__file__).parent / "temp_files"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
settings.temp_dir.mkdir(parents=True, exist_ok=True)
