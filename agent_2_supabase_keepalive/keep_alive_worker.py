"""
Tiến trình thực thi giữ ấm và kích hoạt định kỳ các dự án Supabase.
Gửi truy vấn SELECT thực tế đến cơ sở dữ liệu PostgreSQL qua PostgREST để đặt lại bộ đếm 7 ngày.
"""

import time
import logging
from datetime import datetime
from typing import List, Dict, Any

import httpx

from config import settings
from schemas import SupabaseInstanceTarget, PingExecutionResult

logger = logging.getLogger("supabase_keeper.worker")


def parse_targets_from_config() -> List[SupabaseInstanceTarget]:
    """Phân giải chuỗi cấu hình biến môi trường thành danh sách các đối tượng SupabaseInstanceTarget."""
    raw = settings.supabase_targets_raw.strip()
    if not raw:
        # Nếu chưa cấu hình, trả về cấu hình mẫu mô phỏng phục vụ kiểm thử
        return [
            SupabaseInstanceTarget(
                name="HR Data Production",
                url="https://mock-demo-project.supabase.co",
                anon_key="mock-anon-key-placeholder",
                table="dim_employee"
            )
        ]

    targets = []
    items = raw.split(",")
    for idx, item in enumerate(items, 1):
        parts = item.strip().split("|")
        if len(parts) >= 2:
            url = parts[0].strip()
            anon_key = parts[1].strip()
            table = parts[2].strip() if len(parts) >= 3 else "dim_employee"
            name = f"Dự Án Supabase #{idx}"
            targets.append(SupabaseInstanceTarget(name=name, url=url, anon_key=anon_key, table=table))
    return targets


async def ping_single_instance(
    client: httpx.AsyncClient,
    instance: SupabaseInstanceTarget
) -> PingExecutionResult:
    """Gửi một truy vấn đọc dữ liệu thực tế tới API PostgREST của Supabase."""
    url = instance.url.rstrip("/")
    headers = {
        "apikey": instance.anon_key,
        "Authorization": f"Bearer {instance.anon_key}",
        "User-Agent": "SupabaseKeepAliveAgent/1.0",
        "Accept": "application/json"
    }

    endpoint = f"{url}/rest/v1/{instance.table}?select=*&limit=1"
    start_time = time.time()

    try:
        resp = await client.get(endpoint, headers=headers)
        latency = round((time.time() - start_time) * 1000, 2)

        # Trạng thái 200 (OK) hoặc 206 (Partial Content) chứng minh database đang hoạt động tốt
        if resp.status_code in (200, 206):
            return PingExecutionResult(
                instance_name=instance.name,
                target_url=url,
                target_table=instance.table,
                status_code=resp.status_code,
                is_active=True,
                latency_ms=latency,
                message=f"Truy vấn bảng '{instance.table}' thành công ({latency} ms)."
            )

        # Thử phương án dự phòng với bảng documents hoặc thông tin hệ thống nếu bảng chính báo lỗi 404
        fallback_endpoint = f"{url}/rest/v1/?select=*"
        resp_fallback = await client.get(fallback_endpoint, headers=headers)
        latency_fb = round((time.time() - start_time) * 1000, 2)

        if resp_fallback.status_code in (200, 206):
            return PingExecutionResult(
                instance_name=instance.name,
                target_url=url,
                target_table="root_metadata",
                status_code=resp_fallback.status_code,
                is_active=True,
                latency_ms=latency_fb,
                message="Truy vấn qua cổng metadata gốc thành công."
            )

        err_text = resp.text[:150]
        return PingExecutionResult(
            instance_name=instance.name,
            target_url=url,
            target_table=instance.table,
            status_code=resp.status_code,
            is_active=False,
            latency_ms=latency,
            message=f"Phản hồi không như mong đợi (Mã {resp.status_code}).",
            error_detail=err_text
        )

    except Exception as e:
        latency = round((time.time() - start_time) * 1000, 2)
        return PingExecutionResult(
            instance_name=instance.name,
            target_url=url,
            target_table=instance.table,
            status_code=0,
            is_active=False,
            latency_ms=latency,
            message="Không thể kết nối đến máy chủ Supabase.",
            error_detail=str(e)
        )


async def send_telegram_summary(results: List[PingExecutionResult]):
    """Gửi báo cáo tổng hợp trạng thái các cơ sở dữ liệu về Telegram."""
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        return

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [f"⚡ <b>BÁO CÁO GIỮ ẤM SUPABASE (24/7 AGENT)</b>", f"⏱️ <i>Thời gian: {now_str}</i>\n"]

    all_success = True
    for res in results:
        status_icon = "🟢" if res.is_active else "🔴"
        if not res.is_active:
            all_success = False
        lines.append(f"{status_icon} <b>{res.instance_name}</b>: {res.message}")

    if all_success:
        lines.append("\n✅ <i>Tất cả cơ sở dữ liệu đã được làm mới bộ đếm 7 ngày thành công!</i>")
    else:
        lines.append("\n⚠️ <i>Phát hiện cơ sở dữ liệu gặp sự cố kết nối, hãy kiểm tra ngay!</i>")

    msg = "\n".join(lines)
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    payload = {
        "chat_id": settings.telegram_chat_id,
        "text": msg,
        "parse_mode": "HTML"
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            await client.post(url, json=payload)
    except Exception as e:
        logger.error(f"Lỗi gửi báo cáo Telegram: {e}")


async def execute_keep_alive_cycle() -> List[PingExecutionResult]:
    """Khởi chạy một chu kỳ kiểm tra và kích hoạt toàn bộ các cơ sở dữ liệu."""
    targets = parse_targets_from_config()
    logger.info(f"🔄 Bắt đầu chu kỳ giữ ấm cho {len(targets)} cơ sở dữ liệu Supabase...")

    results: List[PingExecutionResult] = []
    async with httpx.AsyncClient(timeout=20.0) as client:
        for t in targets:
            res = await ping_single_instance(client, t)
            results.append(res)
            if res.is_active:
                logger.info(f"✅ [{res.instance_name}] Hoạt động tốt: {res.message}")
            else:
                logger.error(f"❌ [{res.instance_name}] Lỗi: {res.error_detail}")

    await send_telegram_summary(results)
    return results
