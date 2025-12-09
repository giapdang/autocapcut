"""
Config Model - Model lưu trữ cấu hình ứng dụng.

Model này quản lý:
- Đường dẫn CapCut.exe
- Đường dẫn thư mục data CapCut
- Các cài đặt xuất video
"""

import os
import json
from typing import Optional, Dict, Any
from dataclasses import dataclass, field, asdict

# Đường dẫn mặc định đến file config
DEFAULT_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'config',
    'settings.json'
)


@dataclass
class ExportSettings:
    """
    Cài đặt xuất video.

    Attributes:
        resolution: Độ phân giải (1080p, 4K, etc.)
        fps: Frame per second
        quality: Chất lượng (high, medium, low)
        format: Định dạng video (mp4, mov, etc.)
        output_folder: Thư mục xuất video
    """
    resolution: str = "1080p"
    fps: int = 30
    quality: str = "high"
    format: str = "mp4"
    output_folder: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Chuyển đổi thành dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExportSettings':
        """Tạo ExportSettings từ dictionary."""
        return cls(
            resolution=data.get('resolution', '1080p'),
            fps=data.get('fps', 30),
            quality=data.get('quality', 'high'),
            format=data.get('format', 'mp4'),
            output_folder=data.get('output_folder', '')
        )


@dataclass
class VisionSettings:
    """
    Cài đặt cho computer vision.

    Attributes:
        confidence_threshold: Ngưỡng độ tin cậy cho template matching
        max_wait_time: Thời gian chờ tối đa (giây)
        enable_ocr: Có bật OCR không
        screenshot_on_error: Có chụp screenshot khi lỗi không
        screenshot_dir: Thư mục lưu screenshots
    """
    confidence_threshold: float = 0.8
    max_wait_time: int = 60
    enable_ocr: bool = False
    screenshot_on_error: bool = True
    screenshot_dir: str = "./screenshots"

    def to_dict(self) -> Dict[str, Any]:
        """Chuyển đổi thành dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VisionSettings':
        """Tạo VisionSettings từ dictionary."""
        return cls(
            confidence_threshold=data.get('confidence_threshold', 0.8),
            max_wait_time=data.get('max_wait_time', 60),
            enable_ocr=data.get('enable_ocr', False),
            screenshot_on_error=data.get('screenshot_on_error', True),
            screenshot_dir=data.get('screenshot_dir', './screenshots')
        )


@dataclass
class AutomationSettings:
    """
    Cài đặt cho automation.

    Attributes:
        retry_attempts: Số lần thử lại
        retry_delay: Thời gian chờ giữa các lần thử (giây)
        use_vision_detection: Có sử dụng vision detection không
        fallback_to_coordinates: Có fallback sang coordinates không
        keyboard_shortcuts_enabled: Có bật keyboard shortcuts không
    """
    retry_attempts: int = 3
    retry_delay: int = 2
    use_vision_detection: bool = True
    fallback_to_coordinates: bool = False
    keyboard_shortcuts_enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Chuyển đổi thành dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AutomationSettings':
        """Tạo AutomationSettings từ dictionary."""
        return cls(
            retry_attempts=data.get('retry_attempts', 3),
            retry_delay=data.get('retry_delay', 2),
            use_vision_detection=data.get('use_vision_detection', True),
            fallback_to_coordinates=data.get('fallback_to_coordinates', False),
            keyboard_shortcuts_enabled=data.get('keyboard_shortcuts_enabled', True)
        )


@dataclass
class ExportDetectionSettings:
    """
    Cài đặt cho export detection.

    Attributes:
        method: Phương pháp detection (vision, manual)
        check_interval: Thời gian giữa các lần kiểm tra (giây)
        export_complete_template: Đường dẫn template export complete
        timeout: Timeout cho export (giây)
    """
    method: str = "vision"
    check_interval: int = 2
    export_complete_template: str = "templates/status/export_complete.png"
    timeout: int = 600

    def to_dict(self) -> Dict[str, Any]:
        """Chuyển đổi thành dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExportDetectionSettings':
        """Tạo ExportDetectionSettings từ dictionary."""
        return cls(
            method=data.get('method', 'vision'),
            check_interval=data.get('check_interval', 2),
            export_complete_template=data.get('export_complete_template', 'templates/status/export_complete.png'),
            timeout=data.get('timeout', 600)
        )


@dataclass
class Config:
    """
    Model lưu trữ cấu hình ứng dụng.

    Attributes:
        capcut_exe_path: Đường dẫn đến file CapCut.exe
        data_folder_path: Đường dẫn đến thư mục data CapCut
        export_settings: Cài đặt xuất video
        vision_settings: Cài đặt computer vision
        automation_settings: Cài đặt automation
        export_detection: Cài đặt export detection
        config_path: Đường dẫn đến file config
    """
    capcut_exe_path: str = ""
    data_folder_path: str = ""
    export_settings: ExportSettings = field(default_factory=ExportSettings)
    vision_settings: VisionSettings = field(default_factory=VisionSettings)
    automation_settings: AutomationSettings = field(default_factory=AutomationSettings)
    export_detection: ExportDetectionSettings = field(default_factory=ExportDetectionSettings)
    config_path: str = DEFAULT_CONFIG_PATH

    # Các đường dẫn mặc định trên Windows
    DEFAULT_CAPCUT_PATHS = [
        r"C:\Program Files\CapCut\CapCut.exe",
        r"C:\Program Files (x86)\CapCut\CapCut.exe",
        os.path.expanduser(r"~\AppData\Local\CapCut\Apps\CapCut.exe"),
    ]

    DEFAULT_DATA_PATHS = [
        os.path.expanduser(r"~\AppData\Local\JianyingPro\User Data\Projects\com.lveditor.draft"),
        os.path.expanduser(r"~\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft"),
    ]

    @classmethod
    def load(cls, config_path: Optional[str] = None) -> 'Config':
        """
        Tải cấu hình từ file JSON.

        Args:
            config_path: Đường dẫn đến file config (tùy chọn)

        Returns:
            Config object với cấu hình đã tải
        """
        path = config_path or DEFAULT_CONFIG_PATH
        config = cls(config_path=path)

        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    config.capcut_exe_path = data.get('capcut_exe_path', '')
                    config.data_folder_path = data.get('data_folder_path', '')

                    if 'export_settings' in data:
                        config.export_settings = ExportSettings.from_dict(
                            data['export_settings']
                        )

                    if 'vision_settings' in data:
                        config.vision_settings = VisionSettings.from_dict(
                            data['vision_settings']
                        )

                    if 'automation_settings' in data:
                        config.automation_settings = AutomationSettings.from_dict(
                            data['automation_settings']
                        )

                    if 'export_detection' in data:
                        config.export_detection = ExportDetectionSettings.from_dict(
                            data['export_detection']
                        )

            except (json.JSONDecodeError, OSError) as e:
                print(f"Lỗi đọc file config: {e}")

        return config

    def save(self) -> bool:
        """
        Lưu cấu hình vào file JSON.

        Returns:
            True nếu lưu thành công, False nếu thất bại
        """
        try:
            # Tạo thư mục config nếu chưa tồn tại
            config_dir = os.path.dirname(self.config_path)
            if config_dir and not os.path.exists(config_dir):
                os.makedirs(config_dir, exist_ok=True)

            data = {
                'capcut_exe_path': self.capcut_exe_path,
                'data_folder_path': self.data_folder_path,
                'export_settings': self.export_settings.to_dict(),
                'vision_settings': self.vision_settings.to_dict(),
                'automation_settings': self.automation_settings.to_dict(),
                'export_detection': self.export_detection.to_dict()
            }

            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

            return True
        except OSError as e:
            print(f"Lỗi lưu file config: {e}")
            return False

    def validate(self) -> Dict[str, bool]:
        """
        Kiểm tra tính hợp lệ của cấu hình.

        Returns:
            Dictionary với kết quả kiểm tra cho từng trường
        """
        return {
            'capcut_exe_valid': self._validate_capcut_exe(),
            'data_folder_valid': self._validate_data_folder(),
            'export_settings_valid': self._validate_export_settings()
        }

    def _validate_capcut_exe(self) -> bool:
        """Kiểm tra đường dẫn CapCut.exe hợp lệ."""
        if not self.capcut_exe_path:
            return False
        return os.path.isfile(self.capcut_exe_path)

    def _validate_data_folder(self) -> bool:
        """Kiểm tra thư mục data CapCut hợp lệ."""
        if not self.data_folder_path:
            return False
        return os.path.isdir(self.data_folder_path)

    def _validate_export_settings(self) -> bool:
        """Kiểm tra cài đặt xuất hợp lệ."""
        # Kiểm tra các giá trị cơ bản
        valid_resolutions = ['720p', '1080p', '2K', '4K']
        valid_qualities = ['low', 'medium', 'high']
        valid_formats = ['mp4', 'mov', 'avi']

        return (
            self.export_settings.resolution in valid_resolutions and
            self.export_settings.quality in valid_qualities and
            self.export_settings.format in valid_formats and
            1 <= self.export_settings.fps <= 120
        )

    def auto_detect_paths(self) -> bool:
        """
        Tự động tìm đường dẫn CapCut.exe và thư mục data.

        Returns:
            True nếu tìm được ít nhất một đường dẫn
        """
        found = False

        # Tìm CapCut.exe
        if not self._validate_capcut_exe():
            for path in self.DEFAULT_CAPCUT_PATHS:
                if os.path.isfile(path):
                    self.capcut_exe_path = path
                    found = True
                    break

        # Tìm thư mục data
        if not self._validate_data_folder():
            for path in self.DEFAULT_DATA_PATHS:
                if os.path.isdir(path):
                    self.data_folder_path = path
                    found = True
                    break

        return found

    def to_dict(self) -> Dict[str, Any]:
        """Chuyển đổi Config thành dictionary."""
        return {
            'capcut_exe_path': self.capcut_exe_path,
            'data_folder_path': self.data_folder_path,
            'export_settings': self.export_settings.to_dict(),
            'vision_settings': self.vision_settings.to_dict(),
            'automation_settings': self.automation_settings.to_dict(),
            'export_detection': self.export_detection.to_dict(),
            'config_path': self.config_path
        }

    def is_ready(self) -> bool:
        """
        Kiểm tra cấu hình đã sẵn sàng để sử dụng chưa.

        Returns:
            True nếu cả capcut_exe và data_folder đều hợp lệ
        """
        validation = self.validate()
        return (
            validation['capcut_exe_valid'] and
            validation['data_folder_valid']
        )
