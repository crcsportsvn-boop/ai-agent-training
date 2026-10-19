"""
Điểm khởi chạy chính (Entry Point) của Supabase Keep-Alive Agent.
Hỗ trợ chế độ kiểm thử tức thì (--test) và chế độ lập lịch chạy nền 24/7 trên VPS.
"""

import sys
import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import settings
from keep_alive_worker import execute_keep_alive_cycle

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("supabase_keeper.main")


async def main():
    args = sys.argv[1:]

    # Chế độ 1: Kiểm thử tức thì một chu kỳ
    if args and args[0] == "--test":
        logger.info("🧪 [CHẾ ĐỘ KIỂM THỬ] Đang gửi truy vấn giữ ấm ngay lập tức...")
        results = await execute_keep_alive_cycle()
        print("\n" + "="*60)
        print("🎯 KẾT QUẢ KIỂM THỬ GIỮ ẤM SUPABASE:")
        print("="*60)
        for r in results:
            status = "THÀNH CÔNG" if r.is_active else "THẤT BẠI"
            print(f"- {r.instance_name} ({r.target_url}): {status} | Độ trễ: {r.latency_ms}ms")
            if r.error_detail:
                print(f"  Chi tiết lỗi: {r.error_detail}")
        print("="*60 + "\n")
        return

    # Chế độ 2: Chạy dịch vụ nền 24/7
    logger.info("======================================================")
    logger.info("🛡️ TÁC NHÂN GIỮ ẤM SUPABASE ĐANG CHẠY 24/7 TRÊN VPS...")
    logger.info(f"⏱️ Chu kỳ kích hoạt: Mỗi {settings.ping_interval_hours} tiếng")
    logger.info("======================================================")

    # Chạy ngay một chu kỳ đầu tiên khi vừa khởi động
    await execute_keep_alive_cycle()

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        execute_keep_alive_cycle,
        "interval",
        hours=settings.ping_interval_hours,
        id="supabase_ping_job",
        replace_existing=True
    )
    scheduler.start()

    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Đang dừng dịch vụ giữ ấm Supabase...")
        scheduler.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
