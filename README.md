# 🤖 BỘ MÃ NGUỒN TỰ ĐỘNG HÓA AI AGENT 24/7 TRÊN GOOGLE CLOUD VPS
> **Chương trình đào tạo HR Data & AI — Buổi 15 (Bế mạc khóa học)**  
> **Repository:** `https://github.com/crcsportsvn-boop/ai-agent-training`

---

## 🌟 GIỚI THIỆU TỔNG QUAN

Kho mã nguồn này chứa trọn bộ 2 tác nhân thông minh được thiết kế đặc thù cho bài toán tự động hóa vận hành nhân sự và duy trì hạ tầng đám mây với chi phí 0 đồng:

1. **Tác nhân 1: Sàng lọc hồ sơ ứng viên & Đồng bộ bảng tính (`agent_1_cv_extract`)**
   - Tự động quét tập tin từ thư mục đám mây theo chu kỳ định sẵn.
   - Trích xuất thông tin cá nhân, học vấn, kinh nghiệm và kỹ năng từ PDF, Word và ảnh chụp scan.
   - Đối soát vị trí ứng tuyển với danh mục chức danh chuẩn hóa doanh nghiệp (DA01, HR01, CS01, AC01).
   - Chấm điểm năng lực từ 1.0 đến 10.0, viết nhận xét khách quan.
   - Đồng bộ tự động vào Google Sheets bảo toàn chữ số 0 ở đầu số điện thoại.
   - Tích hợp rào chắn an toàn: Cơ chế con người tham gia phê duyệt khi điểm thấp hoặc không khớp mã vị trí.
   - Bắn thông báo báo cáo và cảnh báo lỗi tức thì về Telegram.

2. **Tác nhân 2: Giữ ấm cơ sở dữ liệu Supabase định kỳ (`agent_2_supabase_keepalive`)**
   - Tự động gửi truy vấn kiểm tra dữ liệu đến các dự án Supabase mỗi 6 tiếng.
   - Đặt lại bộ đếm thời gian 7 ngày không hoạt động, ngăn chặn tình trạng cơ sở dữ liệu bị tạm dừng.
   - Báo cáo trạng thái kết nối và độ trễ phản hồi về Telegram.

---

## 📂 CẤU TRÚC KHO MÃ NGUỒN

```
ai-agent-training/
├── deploy_to_vps_guide.md           # Cẩm nang 4 bước cài đặt và vận hành trên Google Cloud VPS
├── credentials.json.example         # Mẫu cấu hình tài khoản dịch vụ Google an toàn
├── .gitignore                       # Chặn đẩy nhầm tệp môi trường và khóa cá nhân
│
├── agent_1_cv_extract/              # TÁC NHÂN SÀNG LỌC HỒ SƠ ỨNG VIÊN
│   ├── config.py                    # Cấu hình biến môi trường
│   ├── schemas.py                   # Lược đồ dữ liệu Pydantic và rào chắn an toàn
│   ├── prompts.py                   # Chỉ dẫn hệ thống cho Gemini 2.5 Flash
│   ├── tools.py                     # Bộ công cụ đọc văn bản, ghi Google Sheets và gửi Telegram
│   ├── graph.py                     # Luồng điều phối LangGraph xử lý 6 bước
│   ├── scheduler.py                 # Bộ lập lịch quét định kỳ
│   ├── main.py                      # Điểm khởi chạy hỗ trợ kiểm thử và chạy nền 24/7
│   ├── service_setup.sh             # Kịch bản cài đặt tự động dịch vụ Systemd trên VPS
│   ├── requirements.txt             # Danh mục thư viện Python cần thiết
│   └── .env.example                 # Mẫu khai báo thông số bảo mật cá nhân
│
├── agent_2_supabase_keepalive/      # TÁC NHÂN GIỮ ẤM CƠ SỞ DỮ LIỆU SUPABASE
│   ├── config.py                    # Cấu hình danh sách dự án
│   ├── schemas.py                   # Lược đồ dữ liệu kiểm tra
│   ├── keep_alive_worker.py         # Tiến trình gửi truy vấn PostgREST làm mới bộ đếm
│   ├── main.py                      # Điểm khởi chạy lập lịch định kỳ mỗi 6 tiếng
│   ├── service_setup.sh             # Kịch bản cài đặt tự động dịch vụ Systemd 24/7
│   ├── requirements.txt             # Danh mục thư viện Python
│   └── .env.example                 # Mẫu cấu hình kết nối Supabase
│
└── sample_cvs/                      # HỒ SƠ ỨNG VIÊN MẪU KIỂM THỬ THỰC TẾ
    ├── CV_Nguyen_Van_An_Chuyen_Vien_Du_Lieu.txt
    ├── CV_Tran_Thi_Bich_Nhan_Vien_Thu_Ngan.txt
    └── CV_Le_Hoang_Nam_Truong_Nhom_Tuyen_Dung.txt
```

---

## 🚀 HƯỚNG DẪN KHỞI CHẠY NHANH CHO HỌC VIÊN

### Bước 1: Sao chép kho mã nguồn về máy tính hoặc máy chủ VPS
```bash
git clone https://github.com/crcsportsvn-boop/ai-agent-training.git
cd ai-agent-training
```

### Bước 2: Thiết lập cấu hình bảo mật
1. Truy cập thư mục tác nhân cần dùng (ví dụ: `agent_1_cv_extract`):
   ```bash
   cd agent_1_cv_extract
   cp .env.example .env
   ```
2. Mở file `.env` và điền khóa Gemini API, thông tin bảng tính Google Sheets và thông tin Telegram Bot cá nhân.
3. Đặt tệp `credentials.json` (tải từ Google Cloud Service Account) vào thư mục tác nhân.

### Bước 3: Chạy thử nghiệm ngay tại máy tính
```bash
# Cài đặt thư viện cần thiết
pip install -r requirements.txt

# Chạy thử nghiệm thẩm định 1 hồ sơ mẫu
python main.py --test
```

### Bước 4: Đưa lên máy chủ Google Cloud VPS chạy 24/7
Xem chi tiết hướng dẫn từng bước trực quan tại tài liệu [deploy_to_vps_guide.md](deploy_to_vps_guide.md).
Chỉ cần thực hiện lệnh một chạm:
```bash
chmod +x service_setup.sh
./service_setup.sh
```
Sau đó kiểm tra trạng thái hoạt động:
```bash
sudo systemctl status ai-agent-cv-extract
```
Khi nhìn thấy dòng chữ màu xanh lá cây `Active: active (running)`, tác nhân của bạn đã chính thức làm việc độc lập 24/7!
