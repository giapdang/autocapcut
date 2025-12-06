"""
Helpers Module - Các hàm tiện ích hỗ trợ.

Module này chứa các hàm helper được sử dụng xuyên suốt ứng dụng.
"""

import os
import json
import platform
from datetime import datetime
from typing import Optional, Any, Tuple


def format_datetime(dt: Optional[datetime], format_str: str = "%d/%m/%Y %H:%M") -> str:
    """
    Format datetime thành string.

    Args:
        dt: Datetime object cần format
        format_str: Chuỗi định dạng (mặc định: "dd/mm/yyyy HH:MM")

    Returns:
        Chuỗi datetime đã format, hoặc "N/A" nếu dt là None
    """
    if dt is None:
        return "N/A"
    return dt.strftime(format_str)


def get_user_home() -> str:
    """
    Lấy đường dẫn thư mục home của user hiện tại.

    Returns:
        Đường dẫn thư mục home
    """
    return os.path.expanduser("~")


def get_default_capcut_paths() -> Tuple[list, list]:
    """
    Lấy danh sách các đường dẫn mặc định của CapCut.

    Returns:
        Tuple gồm (danh sách đường dẫn exe, danh sách đường dẫn data)
    """
    home = get_user_home()

    # Đường dẫn mặc định đến CapCut.exe
    exe_paths = [
        os.path.join("C:", "Program Files", "CapCut", "CapCut.exe"),
        os.path.join("C:", "Program Files (x86)", "CapCut", "CapCut.exe"),
        os.path.join(home, "AppData", "Local", "CapCut", "Apps", "CapCut.exe"),
    ]

    # Đường dẫn mặc định đến thư mục data
    data_paths = [
        os.path.join(
            home, "AppData", "Local", "JianyingPro",
            "User Data", "Projects", "com.lveditor.draft"
        ),
        os.path.join(
            home, "AppData", "Local", "CapCut",
            "User Data", "Projects", "com.lveditor.draft"
        ),
    ]

    return exe_paths, data_paths


def validate_path(path: str, is_file: bool = True) -> bool:
    """
    Kiểm tra đường dẫn có hợp lệ không.

    Args:
        path: Đường dẫn cần kiểm tra
        is_file: True nếu kiểm tra file, False nếu kiểm tra folder

    Returns:
        True nếu đường dẫn hợp lệ
    """
    if not path:
        return False

    if is_file:
        return os.path.isfile(path)
    return os.path.isdir(path)


def safe_json_load(filepath: str, default: Any = None) -> Any:
    """
    Đọc file JSON một cách an toàn.

    Args:
        filepath: Đường dẫn đến file JSON
        default: Giá trị mặc định nếu đọc thất bại

    Returns:
        Dữ liệu đã parse hoặc giá trị mặc định
    """
    if default is None:
        default = {}

    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Lỗi đọc file JSON {filepath}: {e}")

    return default


def safe_json_save(filepath: str, data: Any, indent: int = 4) -> bool:
    """
    Ghi dữ liệu vào file JSON một cách an toàn.

    Args:
        filepath: Đường dẫn đến file JSON
        data: Dữ liệu cần ghi
        indent: Số spaces để indent

    Returns:
        True nếu ghi thành công, False nếu thất bại
    """
    try:
        # Tạo thư mục nếu chưa tồn tại
        dir_path = os.path.dirname(filepath)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        return True
    except OSError as e:
        print(f"Lỗi ghi file JSON {filepath}: {e}")
        return False


def is_windows() -> bool:
    """
    Kiểm tra có đang chạy trên Windows không.

    Returns:
        True nếu đang chạy trên Windows
    """
    return platform.system() == 'Windows'


def get_timestamp_string() -> str:
    """
    Lấy timestamp string cho tên file.

    Returns:
        Timestamp string dạng YYYYMMDD_HHMMSS
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def truncate_string(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Cắt ngắn string nếu quá dài.

    Args:
        text: Chuỗi cần cắt
        max_length: Độ dài tối đa
        suffix: Hậu tố thêm vào nếu bị cắt

    Returns:
        Chuỗi đã được cắt ngắn
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def ensure_directory(path: str) -> bool:
    """
    Đảm bảo thư mục tồn tại, tạo nếu chưa có.

    Args:
        path: Đường dẫn thư mục

    Returns:
        True nếu thư mục tồn tại hoặc được tạo thành công
    """
    try:
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        return True
    except OSError as e:
        print(f"Lỗi tạo thư mục {path}: {e}")
        return False


def format_file_size(size_bytes: int) -> str:
    """
    Format kích thước file thành dạng dễ đọc.

    Args:
        size_bytes: Kích thước tính bằng bytes

    Returns:
        Chuỗi kích thước đã format (KB, MB, GB)
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def get_relative_time(dt: datetime) -> str:
    """
    Lấy thời gian tương đối (vd: "2 giờ trước").

    Args:
        dt: Datetime cần tính

    Returns:
        Chuỗi thời gian tương đối
    """
    if dt is None:
        return "N/A"

    now = datetime.now()
    diff = now - dt

    seconds = diff.total_seconds()

    if seconds < 60:
        return "Vừa xong"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} phút trước"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} giờ trước"
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f"{days} ngày trước"
    elif seconds < 2592000:
        weeks = int(seconds / 604800)
        return f"{weeks} tuần trước"
    else:
        return format_datetime(dt)
