"""
Bộ lập lịch tự động (Scheduler) cho AI Agent Tuyển Dụng.
Quét định kỳ thư mục tập tin đầu vào để kích hoạt luồng xử lý tự động 24/7 trên VPS.
"""

import os
import asyncio
import logging
from pathlib import Path
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import settings
from graph import run_cv_screening_workflow

logger = logging.getLogger("cv_agent.scheduler")


async def scan_and_process_incoming_files():
    """Hàm quét định kỳ các tập tin mới trong thư mục tạm hoặc Drive."""
    logger.info("🔍 [Scheduler] Bắt đầu quét các tập tin ứng viên mới...")
    
    incoming_dir = settings.temp_dir / "incoming"
    incoming_dir.mkdir(parents=True, exist_ok=True)

    files = [f for f in incoming_dir.iterdir() if f.is_file() and not f.name.startswith(".")]
    if not files:
        logger.info("ℹ️ Không có tập tin mới nào cần xử lý.")
        return

    logger.info(f"⚡ Phát hiện {len(files)} tập tin mới. Đang bắt đầu xử lý...")
    for file_path in files:
        logger.info(f"▶️ Đang xử lý: {file_path.name}")
        state = await run_cv_screening_workflow(str(file_path), file_path.name)
        
        # Di chuyển tập tin đã xử lý sang thư mục lưu trữ đã hoàn tất
        processed_dir = settings.temp_dir / "processed"
        processed_dir.mkdir(parents=True, exist_ok=True)
        new_path = processed_dir / file_path.name
        file_path.rename(new_path)
        logger.info(f"✅ Hoàn tất tập tin: {file_path.name}")


def start_scheduler():
    """Khởi tạo và cấu hình bộ lập lịch AsyncIOScheduler."""
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        scan_and_process_incoming_files,
        "interval",
        minutes=settings.polling_interval_minutes,
        id="cv_scanner_job",
        replace_existing=True
    )
    scheduler.start()
    logger.info(f"🚀 Bộ lập lịch đã kích hoạt. Chu kỳ quét: mỗi {settings.polling_interval_minutes} phút.")
    return scheduler
