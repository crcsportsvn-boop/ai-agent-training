"""
Lược đồ dữ liệu Pydantic cho Supabase Keep-Alive Agent.
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class SupabaseInstanceTarget(BaseModel):
    """Thông tin một dự án Supabase cần duy trì kết nối."""
    name: str = Field(default="Dự án Supabase", description="Tên gợi nhớ của cơ sở dữ liệu")
    url: str = Field(..., description="Đường dẫn gốc của dự án Supabase (https://xyz.supabase.co)")
    anon_key: str = Field(..., description="Khóa công khai anon key để gửi truy vấn")
    table: str = Field(default="dim_employee", description="Bảng dữ liệu thực hiện truy vấn SELECT")


class PingExecutionResult(BaseModel):
    """Kết quả kiểm tra trạng thái của một dự án Supabase."""
    instance_name: str
    target_url: str
    target_table: str
    status_code: int
    is_active: bool
    latency_ms: float
    message: str
    error_detail: Optional[str] = None
