"""
Lược đồ dữ liệu Pydantic và Trạng thái luồng thực thi (State).
Đảm bảo tính toàn vẹn dữ liệu và kiểm tra rào chắn an toàn (Guardrails).
"""

from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field, field_validator


class CandidatePersonalInfo(BaseModel):
    """Thông tin cá nhân cơ bản của ứng viên trích xuất từ CV."""
    full_name: str = Field(default="Ứng viên chưa rõ tên", description="Họ và tên đầy đủ")
    phone_number: str = Field(default="", description="Số điện thoại liên hệ")
    email: str = Field(default="", description="Địa chỉ thư điện tử")
    city: str = Field(default="Chưa rõ", description="Tỉnh thành hoặc nơi cư trú")
    birth_year: Optional[int] = Field(default=None, description="Năm sinh 4 chữ số")
    applied_position: str = Field(default="Chưa xác định", description="Vị trí ứng tuyển ghi trên hồ sơ")
    matched_job_code: str = Field(default="UNMAPPED", description="Mã công việc chuẩn hóa theo danh mục")
    matched_position_id: str = Field(default="POS-PENDING", description="Mã vị trí chuẩn hóa")

    @field_validator("phone_number", mode="before")
    @classmethod
    def normalize_phone_number(cls, v: Any) -> str:
        """Đảm bảo số điện thoại giữ nguyên số 0 ở đầu và loại bỏ ký tự lạ."""
        if not v:
            return ""
        digits = "".join([c for c in str(v) if c.isdigit()])
        if digits.startswith("84") and len(digits) >= 11:
            digits = "0" + digits[2:]
        elif not digits.startswith("0") and len(digits) >= 9:
            digits = "0" + digits
        return digits


class CandidateJobInfo(BaseModel):
    """Kinh nghiệm làm việc, học vấn và kỹ năng của ứng viên."""
    education_level: str = Field(default="Đại học", description="Trình độ học vấn cao nhất")
    university: str = Field(default="", description="Tên trường tốt nghiệp")
    major: str = Field(default="", description="Chuyên ngành đào tạo")
    graduation_year: Optional[int] = Field(default=None, description="Năm tốt nghiệp")
    years_of_experience: float = Field(default=0.0, description="Tổng số năm kinh nghiệm làm việc")
    work_history_summary: str = Field(default="", description="Tóm tắt lịch sử công tác")
    key_skills: str = Field(default="", description="Danh sách kỹ năng cốt lõi")
    certifications: str = Field(default="", description="Chứng chỉ chuyên môn liên quan")


class CandidateEvaluation(BaseModel):
    """Kết quả đánh giá và chấm điểm mức độ phù hợp của hồ sơ."""
    score: float = Field(default=5.0, description="Điểm đánh giá từ 1.0 đến 10.0")
    recommendation: Literal["Phù hợp - Mời phỏng vấn", "Xem xét thêm", "Chưa phù hợp", "Chờ xác nhận"] = Field(
        default="Chờ xác nhận", description="Khuyến nghị xử lý tuyển dụng"
    )
    strengths: str = Field(default="", description="3 điểm mạnh nổi bật của ứng viên")
    areas_for_growth: str = Field(default="", description="Điểm còn thiếu hoặc cần kiểm tra thêm khi phỏng vấn")
    summary_reason: str = Field(default="", description="Nhận xét tổng quan của trợ lý tuyển dụng")

    @field_validator("score", mode="before")
    @classmethod
    def validate_score(cls, v: Any) -> float:
        try:
            val = float(v)
            return max(1.0, min(10.0, round(val, 1)))
        except (ValueError, TypeError):
            return 5.0


class CVProcessingState(BaseModel):
    """Trạng thái điều phối dữ liệu xuyên suốt các bước xử lý của AI Agent."""
    file_id: str = ""
    file_name: str = ""
    local_file_path: str = ""
    file_type: str = "pdf"
    raw_text: str = ""
    needs_ocr: bool = False
    personal_info: Optional[CandidatePersonalInfo] = None
    job_info: Optional[CandidateJobInfo] = None
    evaluation: Optional[CandidateEvaluation] = None
    sheet_synced: bool = False
    drive_archived_url: str = ""
    error_message: Optional[str] = None
    step_count: int = 0
