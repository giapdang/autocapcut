# AutoCapCut - Công cụ tự động xuất video từ CapCut

🎬 **AutoCapCut** là một công cụ Python với giao diện đồ họa giúp tự động xuất nhiều project CapCut một cách tuần tự, tiết kiệm thời gian và công sức.

## 📋 Mục lục

- [Tính năng](#tính-năng)
- [Yêu cầu hệ thống](#yêu-cầu-hệ-thống)
- [Cài đặt](#cài-đặt)
- [Cách sử dụng](#cách-sử-dụng)
- [Cấu trúc dự án](#cấu-trúc-dự-án)
- [Troubleshooting](#troubleshooting)
- [Đóng góp](#đóng-góp)

## ✨ Tính năng

- **Giao diện hiện đại**: Sử dụng CustomTkinter với theme sáng, giao diện đẹp mắt, dễ nhìn
- **Tự động phát hiện**: Tự động tìm đường dẫn CapCut.exe và thư mục data
- **Quản lý project nâng cao**: 
  - Hiển thị danh sách projects với thông tin chi tiết và thumbnail
  - Tìm kiếm/lọc projects theo tên
  - Chỉ hiển thị projects local hiện tại (lọc bỏ trash và cloud)
  - Sắp xếp theo ngày sửa đổi (mới nhất trước)
- **Mở project trong CapCut**: Click nút "Open" để mở project trực tiếp trong CapCut
- **Xuất hàng loạt**: Chọn nhiều projects và xuất tự động
- **Theo dõi tiến trình**: Progress bar và log chi tiết
- **Lưu cấu hình**: Tự động lưu cấu hình cho lần sử dụng sau
- **Hỗ trợ tiếng Việt**: Giao diện hoàn toàn bằng tiếng Việt

## 💻 Yêu cầu hệ thống

- **Hệ điều hành**: Windows 10/11
- **Python**: 3.8 trở lên
- **CapCut**: Đã cài đặt trên máy
- **RAM**: Tối thiểu 4GB
- **Dung lượng**: 100MB cho tool + dung lượng video xuất

## 📥 Cài đặt

### Bước 1: Cài đặt Python

1. Tải Python từ [python.org](https://www.python.org/downloads/)
2. Khi cài đặt, **bắt buộc tick chọn** "Add Python to PATH"
3. Khởi động lại máy tính sau khi cài

### Bước 2: Clone hoặc tải repository

```bash
git clone https://github.com/giapdang/autocapcut.git
cd autocapcut
```

Hoặc tải trực tiếp file ZIP và giải nén.

### Bước 3: Cài đặt dependencies

Mở Command Prompt hoặc PowerShell trong thư mục project và chạy:

```bash
pip install -r requirements.txt
```

### Bước 4: Chạy ứng dụng

```bash
python main.py
```

## 🚀 Cách sử dụng

### Bước 1: Cấu hình đường dẫn

1. **CapCut.exe**: Click "Browse" để chọn file CapCut.exe
   - Thường nằm ở: `C:\Program Files\CapCut\CapCut.exe`
   - Hoặc: `C:\Users\[Username]\AppData\Local\CapCut\Apps\CapCut.exe`

2. **Thư mục data**: Click "Browse" để chọn thư mục chứa projects
   - Thường nằm ở: `C:\Users\[Username]\AppData\Local\JianyingPro\User Data\Projects\com.lveditor.draft`

3. Hoặc nhấn **"Auto-detect"** để tool tự động tìm

### Bước 2: Load projects

1. Click nút **"Load Projects"**
2. Danh sách projects sẽ hiển thị với:
   - Thumbnail (hình thu nhỏ)
   - Tên project
   - Ngày tạo
   - Ngày chỉnh sửa gần nhất
   - Nút "Open" để mở project
3. Sử dụng thanh tìm kiếm để lọc projects theo tên
4. **Lưu ý**: Chỉ hiển thị projects local hiện tại, không bao gồm projects trong thùng rác hoặc cloud

### Bước 3: Mở project trong CapCut

1. Click nút **"📂 Open"** bên cạnh project muốn mở
2. Tool sẽ tự động:
   - Thử mở project bằng tham số dòng lệnh
   - Nếu không được, thử mở bằng file project
   - Nếu vẫn không được, tự động thao tác UI để mở project
3. CapCut sẽ được mở với project đã chọn

### Bước 4: Chọn projects để xuất

1. Tick chọn các projects muốn xuất
2. Có thể dùng **"Chọn tất cả"** hoặc **"Bỏ chọn"**

### Bước 5: Xuất video

1. Click nút **"Export Selected"**
2. Tool sẽ tự động:
   - Mở CapCut với từng project
   - Click nút Export
   - Chờ xuất xong
   - Đóng CapCut và chuyển sang project tiếp theo

3. Theo dõi tiến trình qua progress bar và log

### Bước 6: Hoàn thành

- Khi xuất xong, sẽ có thông báo hoàn thành
- Video được lưu theo cài đặt mặc định của CapCut

## 📁 Cấu trúc dự án

```
autocapcut/
├── models/             # Data models
│   ├── __init__.py
│   ├── project.py      # Project model
│   └── config.py       # Config model
├── views/              # Giao diện
│   ├── __init__.py
│   ├── main_window.py  # Cửa sổ chính
│   └── components.py   # Các component UI
├── controllers/        # Business logic
│   ├── __init__.py
│   ├── main_controller.py
│   └── export_controller.py
├── services/           # Services
│   ├── __init__.py
│   ├── capcut_service.py     # Tương tác với CapCut
│   ├── automation_service.py # Tự động hóa
│   └── file_service.py       # Đọc/ghi file
├── utils/              # Tiện ích
│   ├── __init__.py
│   └── helpers.py
├── config/
│   └── settings.json   # File cấu hình
├── requirements.txt    # Dependencies
├── main.py            # Entry point
└── README.md          # Hướng dẫn
```

## ⚙️ Cấu hình nâng cao

File `config/settings.json` chứa cấu hình:

```json
{
    "capcut_exe_path": "C:\\Program Files\\CapCut\\CapCut.exe",
    "data_folder_path": "C:\\Users\\Username\\AppData\\Local\\JianyingPro\\User Data\\Projects\\com.lveditor.draft",
    "export_settings": {
        "resolution": "1080p",
        "fps": 30,
        "quality": "high",
        "format": "mp4",
        "output_folder": ""
    }
}
```

## 🔧 Troubleshooting

### Lỗi: "Không tìm thấy CapCut"

**Nguyên nhân**: Tool không tìm được CapCut.exe
**Giải pháp**: 
1. Cài đặt CapCut từ trang chính thức
2. Chọn đường dẫn thủ công bằng nút Browse

### Lỗi: "Không có project nào"

**Nguyên nhân**: Thư mục data không đúng hoặc chưa có project, hoặc tất cả projects đều trong trash/cloud
**Giải pháp**:
1. Kiểm tra đường dẫn thư mục data
2. Đảm bảo đã tạo ít nhất một project local trong CapCut (không phải cloud project)
3. Kiểm tra log để xem lý do project bị bỏ qua
4. Thử dùng Auto-detect

### Lỗi: "Không thể mở project"

**Nguyên nhân**: CapCut không hỗ trợ tham số dòng lệnh hoặc UI automation không hoạt động
**Giải pháp**:
1. Thử mở project thủ công trong CapCut để xác nhận project còn tồn tại
2. Kiểm tra log để xem phương pháp nào đã được thử
3. Đảm bảo đã cài đặt pyperclip: `pip install pyperclip`
4. Nếu UI automation không hoạt động, có thể cần điều chỉnh tọa độ click trong code

### Lỗi: "ModuleNotFoundError"

**Nguyên nhân**: Chưa cài dependencies
**Giải pháp**:
```bash
pip install -r requirements.txt
```

### Lỗi: "customtkinter not found"

**Nguyên nhân**: Chưa cài customtkinter
**Giải pháp**:
```bash
pip install customtkinter
```

### Export không hoạt động

**Nguyên nhân**: 
1. CapCut đang chạy
2. Quyền admin

**Giải pháp**:
1. Đóng CapCut trước khi export
2. Chạy tool với quyền Administrator

### Giao diện bị lỗi font tiếng Việt

**Nguyên nhân**: Font không hỗ trợ Unicode
**Giải pháp**: Cài đặt font hỗ trợ tiếng Việt (như Arial Unicode MS)

## 📝 Ghi chú

- Tool chỉ hoạt động trên Windows
- Cần đóng CapCut trước khi chạy export
- Video được lưu theo cài đặt mặc định của CapCut
- Không nên sử dụng máy tính khi đang export
- Tool tự động lọc bỏ projects trong thùng rác và cloud projects
- Projects được quét từ nhiều thư mục: Projects, User Data/Projects, AutoSave
- Chức năng mở project hỗ trợ nhiều phương pháp fallback để tương thích với các phiên bản CapCut khác nhau

## 🤝 Đóng góp

Mọi đóng góp đều được hoan nghênh! Vui lòng:

1. Fork repository
2. Tạo branch mới (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push lên branch (`git push origin feature/AmazingFeature`)
5. Tạo Pull Request

## 📄 License

Dự án được phân phối dưới giấy phép MIT. Xem file `LICENSE` để biết thêm chi tiết.

## 📧 Liên hệ

- GitHub Issues: [github.com/giapdang/autocapcut/issues](https://github.com/giapdang/autocapcut/issues)

---

Made with ❤️ by AutoCapCut Team
