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

- **Giao diện hiện đại**: Sử dụng CustomTkinter để tạo giao diện đẹp mắt, hỗ trợ dark mode
- **Tự động phát hiện**: Tự động tìm đường dẫn CapCut.exe và thư mục data
- **Quản lý project**: Hiển thị danh sách tất cả projects với thông tin chi tiết
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
   - Tên project
   - Ngày tạo
   - Ngày chỉnh sửa gần nhất

### Bước 3: Chọn projects

1. Tick chọn các projects muốn xuất
2. Có thể dùng **"Chọn tất cả"** hoặc **"Bỏ chọn"**

### Bước 4: Xuất video

1. Click nút **"Export Selected"**
2. Tool sẽ tự động:
   - Mở CapCut với từng project
   - Click nút Export
   - Chờ xuất xong
   - Đóng CapCut và chuyển sang project tiếp theo

3. Theo dõi tiến trình qua progress bar và log

### Bước 5: Hoàn thành

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

**Nguyên nhân**: Thư mục data không đúng hoặc chưa có project
**Giải pháp**:
1. Kiểm tra đường dẫn thư mục data
2. Đảm bảo đã tạo ít nhất một project trong CapCut
3. Thử dùng Auto-detect

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

---

## 🚀 Computer Vision và AI Features (Mới!)

AutoCapCut đã được nâng cấp với các tính năng computer vision và AI tiên tiến để tăng độ tin cậy và tự động hóa!

### ✨ Tính năng mới

#### 1. **Computer Vision với OpenCV**
- **Template Matching**: Tự động tìm và click vào buttons/icons trên CapCut UI
- **Export Detection**: Phát hiện tự động khi export hoàn tất (không cần hard-coded delays)
- **Multi-resolution Support**: Hoạt động với nhiều độ phân giải màn hình khác nhau
- **Screenshot Debugging**: Tự động chụp màn hình khi có lỗi để debug

#### 2. **Template Management System**
- Quản lý templates cho các UI elements (buttons, icons, status)
- Versioning support cho các phiên bản CapCut khác nhau
- Auto-capture templates từ CapCut UI
- Template validation và caching

#### 3. **Smart Error Handling**
- Tự động chụp screenshot khi có lỗi
- Retry mechanism với exponential backoff
- Chi tiết logging với stack trace
- Thống kê lỗi và performance metrics

#### 4. **Database Tracking**
- Lưu trữ export history với SQLite
- Performance metrics và analytics
- Error logs với screenshots
- Export statistics và success rate

### 📦 Dependencies mới

Các thư viện đã được thêm vào `requirements.txt`:

```txt
opencv-python>=4.8.0    # Computer vision
numpy>=1.24.0           # Array processing
mss>=9.0.1              # Fast screenshot
pytesseract>=0.3.10     # OCR (optional)
```

### 🎯 Cách sử dụng Computer Vision Features

#### Sử dụng cơ bản

```python
from models.config import Config
from controllers.export_controller import ExportController

# Load config với vision settings
config = Config.load()
config.automation_settings.use_vision_detection = True
config.vision_settings.confidence_threshold = 0.8

# Tạo export controller
controller = ExportController(config=config, use_database=True)

# Export với vision detection
controller.batch_export_with_vision(projects)
```

#### Quản lý Templates

```python
from services.template_manager import TemplateManager

# Khởi tạo template manager
manager = TemplateManager()

# List templates
templates = manager.list_templates(category='buttons')

# Capture template mới từ màn hình
manager.capture_template(
    name='export_button',
    region=(100, 100, 200, 50),  # x, y, width, height
    category='buttons',
    description='Export button trong CapCut UI'
)

# Validate template
validation = manager.validate_template('export_button', 'buttons')
if validation['valid_size']:
    print("Template hợp lệ!")
```

#### Debug Vision Detection

```python
from services.vision_service import VisionService

# Khởi tạo vision service
vision = VisionService(
    confidence_threshold=0.8,
    screenshot_on_error=True
)

# Tìm button trên màn hình
result = vision.find_image_on_screen(
    'templates/buttons/export_button.png',
    confidence=0.8
)

if result.found:
    print(f"Found at ({result.x}, {result.y})")
    print(f"Confidence: {result.confidence}")
```

### 🗂️ Cấu trúc mới

```
autocapcut/
├── models/
│   ├── database.py           # SQLite database models
│   └── ...
├── services/
│   ├── vision_service.py     # Computer vision service
│   ├── template_manager.py   # Template management
│   └── ...
├── utils/
│   ├── error_handler.py      # Error handling với screenshots
│   └── ...
├── templates/                # Template images
│   ├── buttons/
│   ├── icons/
│   └── status/
├── examples/                 # Usage examples
│   ├── basic_usage.py
│   ├── vision_debugging.py
│   └── ...
├── tests/                    # Unit tests
│   ├── test_vision_service.py
│   └── ...
├── screenshots/              # Debug screenshots (auto-generated)
├── logs/                     # Log files (auto-generated)
└── autocapcut.db            # SQLite database (auto-generated)
```

### ⚙️ Cấu hình nâng cao

File `config/settings.json` đã được mở rộng:

```json
{
    "vision_settings": {
        "confidence_threshold": 0.8,
        "max_wait_time": 60,
        "enable_ocr": false,
        "screenshot_on_error": true,
        "screenshot_dir": "./screenshots"
    },
    "automation_settings": {
        "retry_attempts": 3,
        "retry_delay": 2,
        "use_vision_detection": true,
        "fallback_to_coordinates": false,
        "keyboard_shortcuts_enabled": true
    },
    "export_detection": {
        "method": "vision",
        "check_interval": 2,
        "export_complete_template": "templates/status/export_complete.png",
        "timeout": 600
    }
}
```

### 📊 Export Statistics

Xem thống kê xuất video:

```python
# Lấy statistics từ controller
stats = controller.get_export_statistics()

print(f"Total exports: {stats['all_time']['total_exports']}")
print(f"Success rate: {stats['all_time']['success_rate']:.1f}%")
print(f"Average duration: {stats['all_time']['average_duration']:.1f}s")
```

Hoặc truy vấn trực tiếp database:

```python
from models.database import Database

db = Database()

# Lấy export history
history = db.get_export_history(limit=10, status='success')

# Lấy statistics
stats = db.get_export_statistics()

# Lấy error logs
errors = db.get_error_logs(limit=20, severity='error')
```

### 🧪 Testing

Chạy unit tests:

```bash
# Test vision service
python tests/test_vision_service.py

# Run all tests
python -m unittest discover tests/
```

### 📚 Examples

Xem các ví dụ trong thư mục `examples/`:

```bash
# Basic usage example
python examples/basic_usage.py

# Vision debugging tool
python examples/vision_debugging.py
```

### 🔧 Troubleshooting Computer Vision

#### Template không tìm thấy

**Nguyên nhân**: Template không khớp với UI hiện tại
**Giải pháp**:
1. Capture template mới từ CapCut UI hiện tại
2. Giảm `confidence_threshold` xuống 0.7 hoặc 0.6
3. Kiểm tra screenshot debug trong folder `screenshots/`

#### Vision detection chậm

**Nguyên nhân**: Screenshot và template matching tốn thời gian
**Giải pháp**:
1. Giảm `check_interval` trong export detection settings
2. Sử dụng templates nhỏ hơn (crop chính xác vùng cần thiết)
3. Bật grayscale matching (mặc định đã bật)

#### OpenCV không khả dụng

**Nguyên nhân**: opencv-python chưa được cài đặt đúng
**Giải pháp**:
```bash
pip uninstall opencv-python
pip install opencv-python
```

#### Lỗi "No module named 'cv2'"

**Giải pháp**:
```bash
pip install --upgrade opencv-python numpy
```

### 🎨 Capture Templates

Để capture templates cho CapCut UI của bạn:

1. Mở CapCut
2. Navigate đến button/icon cần capture
3. Sử dụng vision debugging tool:

```bash
python examples/vision_debugging.py
```

4. Chọn option "Demo: Capture Template"
5. Hoặc sử dụng code:

```python
from services.template_manager import TemplateManager
import pyautogui

# Get position of button (hover mouse over it first)
position = pyautogui.position()
print(f"Mouse position: {position}")

# Capture template (adjust region)
manager = TemplateManager()
manager.capture_template(
    name='my_button',
    region=(position.x - 50, position.y - 25, 100, 50),
    category='buttons',
    description='My custom button'
)
```

### 💡 Best Practices

1. **Templates**: Capture templates từ độ phân giải màn hình phổ biến (1920x1080)
2. **Confidence**: Bắt đầu với 0.8, giảm dần nếu cần
3. **Retry**: Sử dụng retry mechanism (mặc định 3 lần)
4. **Debugging**: Bật screenshot_on_error để dễ debug
5. **Database**: Clean up old records định kỳ:

```python
from models.database import Database

db = Database()
deleted = db.cleanup_old_records(days=30)
print(f"Deleted {deleted['export_history']} old records")
```

### 🔒 Security Notes

- Screenshots có thể chứa sensitive information
- Database lưu trữ local, không upload lên cloud
- Error logs có thể chứa stack traces với paths
- Template images chỉ chứa UI elements, không chứa content

### 📈 Performance Tuning

**Tối ưu tốc độ:**
- Giảm `check_interval` trong export detection
- Sử dụng `mss` thay vì ImageGrab (đã mặc định)
- Cache templates trong memory
- Sử dụng grayscale matching

**Tối ưu độ chính xác:**
- Tăng `confidence_threshold` lên 0.9
- Capture templates rõ nét, độ phân giải cao
- Tạo multiple versions cho các phiên bản CapCut khác nhau
- Sử dụng `wait_for_image` với timeout hợp lý

