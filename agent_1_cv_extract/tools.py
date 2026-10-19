"""
Bộ công cụ thực thi (Tools) cho AI Agent Tuyển Dụng.
Bao gồm: Trích xuất tập tin văn bản, kết nối Google Sheets, lưu trữ Drive và phát thông báo Telegram.
"""

import os
import re
import logging
from datetime import datetime
from typing import Optional, Tuple, List, Dict, Any

import httpx

logger = logging.getLogger("cv_agent.tools")


# ==============================================================================
# 1. CÔNG CỤ TRÍCH XUẤT VĂN BẢN ĐA ĐỊNH DẠNG (TEXT EXTRACTION)
# ==============================================================================
def extract_text_from_file(file_path: str) -> Tuple[str, bool]:
    """
    Đọc văn bản từ các định dạng tập tin phổ biến: PDF, DOCX, TXT.
    Trả về: (văn bản trích xuất, cờ báo hiệu cần xử lý OCR qua hình ảnh)
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Không tìm thấy tập tin: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()
    extracted_text = ""

    try:
        if ext == ".txt":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                extracted_text = f.read()

        elif ext == ".pdf":
            try:
                import pypdf
                reader = pypdf.PdfReader(file_path)
                pages_text = [page.extract_text() or "" for page in reader.pages]
                extracted_text = "\n".join(pages_text).strip()
            except ImportError:
                logger.warning("Thư viện pypdf chưa được cài đặt, chuyển sang chế độ đọc thô.")
                with open(file_path, "rb") as f:
                    extracted_text = f.read().decode("utf-8", errors="ignore")

        elif ext in (".docx", ".doc"):
            try:
                import docx
                doc = docx.Document(file_path)
                paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
                tables_text = []
                for table in doc.tables:
                    for row in table.rows:
                        row_content = " | ".join([cell.text.strip() for cell in row.cells if cell.text.strip()])
                        if row_content:
                            tables_text.append(row_content)
                extracted_text = "\n".join(paragraphs + tables_text).strip()
            except Exception as e:
                logger.warning(f"Lỗi khi đọc file Word: {e}")

        # Rào chắn kiểm tra: Nếu văn bản trích xuất dưới 50 ký tự, rất có thể là file scan dạng ảnh
        if len(extracted_text.strip()) < 50:
            return extracted_text, True

        return extracted_text, False

    except Exception as e:
        logger.error(f"Lỗi ngoại lệ khi xử lý file {file_path}: {e}")
        return "", True


# ==============================================================================
# 2. CÔNG CỤ ĐỒNG BỘ GOOGLE SHEETS VỚI CHẾ ĐỘ USER_ENTERED
# ==============================================================================
def append_candidate_to_sheet(
    sheet_id: str,
    sheet_name: str,
    service_account_path: str,
    row_values: List[Any]
) -> bool:
    """
    Ghi một dòng dữ liệu ứng viên vào Google Sheets.
    Sử dụng value_input_option='USER_ENTERED' để đảm bảo không bị mất số 0 ở đầu số điện thoại.
    """
    if not sheet_id or not os.path.exists(service_account_path):
        logger.warning("Chưa cấu hình Google Sheet ID hoặc file chứng thực service account. Ghi nhận log mô phỏng.")
        logger.info(f"Dữ liệu ghi vào bảng tính: {row_values}")
        return True

    try:
        import gspread
        gc = gspread.service_account(filename=service_account_path)
        sh = gc.open_by_key(sheet_id)
        worksheet = sh.worksheet(sheet_name)
        
        # Bắt buộc dùng USER_ENTERED để bảo toàn số 0 ở đầu số điện thoại
        worksheet.append_row(row_values, value_input_option="USER_ENTERED")
        logger.info(f"Đã ghi thành công dữ liệu ứng viên vào sheet '{sheet_name}'.")
        return True
    except Exception as e:
        logger.error(f"Lỗi khi ghi dữ liệu vào Google Sheets: {e}")
        return False


# ==============================================================================
# 3. CÔNG CỤ ĐỔI TÊN VÀ LƯU TRỮ GOOGLE DRIVE
# ==============================================================================
def generate_standard_filename(position_title: str, candidate_name: str) -> str:
    """Tạo tên file lưu trữ chuẩn hóa theo định dạng: YYYY-MM-DD - Vị trí - Họ và tên.pdf"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    clean_name = re.sub(r'[\\/*?:"<>|]', "", candidate_name).strip()
    clean_pos = re.sub(r'[\\/*?:"<>|]', "", position_title).strip()
    return f"{date_str} - {clean_pos} - {clean_name}.pdf"


# ==============================================================================
# 4. CÔNG CỤ CẢNH BÁO TỨC THÌ QUA TELEGRAM BOT
# ==============================================================================
async def send_telegram_alert(
    bot_token: str,
    chat_id: str,
    message: str
) -> bool:
    """Gửi thông báo định dạng HTML về kênh Telegram của chuyên viên nhân sự."""
    if not bot_token or not chat_id:
        logger.info(f"[Telegram Thông Báo - Mô Phỏng]:\n{message}")
        return True

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                logger.info("Đã gửi thông báo Telegram thành công.")
                return True
            else:
                logger.error(f"Lỗi gửi Telegram: HTTP {resp.status_code} - {resp.text}")
                return False
    except Exception as e:
        logger.error(f"Ngoại lệ kết nối Telegram API: {e}")
        return False
