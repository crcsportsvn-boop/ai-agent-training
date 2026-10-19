"""
Điểm khởi chạy chính (Entry Point) của AI Agent Tuyển Dụng.
Hỗ trợ cả chế độ kiểm thử cục bộ một file (Test mode) và chế độ chạy dịch vụ ngầm 24/7 (Daemon mode).
"""

import sys
import asyncio
import logging
from pathlib import Path

from config import settings
from graph import run_cv_screening_workflow
from scheduler import start_scheduler

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("cv_agent.main")


async def main():
    args = sys.argv[1:]
    
    # Chế độ 1: Kiểm thử trực tiếp 1 tập tin CV
    if args and args[0] == "--test":
        file_to_test = args[1] if len(args) > 1 else str(Path(__file__).parent.parent / "sample_cvs" / "CV_Nguyen_Van_An_Chuyen_Vien_Du_Lieu.txt")
        file_name = Path(file_to_test).name
        
        logger.info(f"🧪 [CHẾ ĐỘ KIỂM THỬ] Khởi chạy thẩm định hồ sơ: {file_name}")
        state = await run_cv_screening_workflow(file_to_test, file_name)
        
        print("\n" + "="*60)
        print("🎯 KẾT QUẢ SÀNG LỌC CỦA AI AGENT:")
        print("="*60)
        if state.personal_info:
            print(f"Họ tên ứng viên: {state.personal_info.full_name}")
            print(f"Số điện thoại  : {state.personal_info.phone_number}")
            print(f"Thư điện tử    : {state.personal_info.email}")
            print(f"Vị trí khớp    : {state.personal_info.matched_job_code} ({state.personal_info.matched_position_id})")
        if state.evaluation:
            print(f"Điểm số AI     : {state.evaluation.score}/10")
            print(f"Khuyến nghị    : {state.evaluation.recommendation}")
            print(f"Đánh giá tóm tắt: {state.evaluation.summary_reason}")
            print(f"Điểm mạnh      : {state.evaluation.strengths}")
        print("="*60 + "\n")
        return

    # Chế độ 2: Chạy dịch vụ nền 24/7 trên máy chủ đám mây
    logger.info("======================================================")
    logger.info("🤖 AI AGENT TUYỂN DỤNG ĐANG KHỞI ĐỘNG CHẠY 24/7...")
    logger.info(f"🌐 Nền tảng máy chủ: Google Cloud VPS")
    logger.info(f"🧠 Mô hình ngôn ngữ : {settings.ai_model_name}")
    logger.info(f"⏱️ Chu kỳ kiểm tra   : Mỗi {settings.polling_interval_minutes} phút")
    logger.info("======================================================")

    scheduler = start_scheduler()

    # Vòng lặp duy trì tiến trình không bao giờ tắt
    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Đang dừng dịch vụ AI Agent...")
        scheduler.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
