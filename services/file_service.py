"""
File Service - Service xử lý đọc/ghi file.

Service này quản lý:
- Đọc/ghi file cấu hình JSON
- Kiểm tra file/folder tồn tại
- Tạo thư mục output nếu chưa có
"""

import os
import shutil
from typing import Optional, Any, List
from utils.helpers import safe_json_load, safe_json_save, ensure_directory


class FileService:
    """
    Service xử lý các thao tác với file.

    Class này cung cấp các phương thức để:
    - Đọc/ghi file JSON
    - Kiểm tra sự tồn tại của file/folder
    - Quản lý thư mục output
    """

    def __init__(self):
        """Khởi tạo FileService."""
        pass

    @staticmethod
    def read_json(filepath: str, default: Any = None) -> Any:
        """
        Đọc file JSON.

        Args:
            filepath: Đường dẫn đến file JSON
            default: Giá trị mặc định nếu đọc thất bại

        Returns:
            Dữ liệu đã parse hoặc giá trị mặc định
        """
        return safe_json_load(filepath, default)

    @staticmethod
    def write_json(filepath: str, data: Any, indent: int = 4) -> bool:
        """
        Ghi dữ liệu vào file JSON.

        Args:
            filepath: Đường dẫn đến file JSON
            data: Dữ liệu cần ghi
            indent: Số spaces để indent

        Returns:
            True nếu ghi thành công
        """
        return safe_json_save(filepath, data, indent)

    @staticmethod
    def file_exists(filepath: str) -> bool:
        """
        Kiểm tra file có tồn tại không.

        Args:
            filepath: Đường dẫn đến file

        Returns:
            True nếu file tồn tại
        """
        return os.path.isfile(filepath)

    @staticmethod
    def folder_exists(folderpath: str) -> bool:
        """
        Kiểm tra folder có tồn tại không.

        Args:
            folderpath: Đường dẫn đến folder

        Returns:
            True nếu folder tồn tại
        """
        return os.path.isdir(folderpath)

    @staticmethod
    def create_folder(folderpath: str) -> bool:
        """
        Tạo folder nếu chưa tồn tại.

        Args:
            folderpath: Đường dẫn đến folder

        Returns:
            True nếu tạo thành công hoặc đã tồn tại
        """
        return ensure_directory(folderpath)

    @staticmethod
    def list_folders(parent_path: str) -> List[str]:
        """
        Liệt kê các folder con trong một folder.

        Args:
            parent_path: Đường dẫn đến folder cha

        Returns:
            Danh sách đường dẫn các folder con
        """
        if not os.path.isdir(parent_path):
            return []

        folders = []
        try:
            for item in os.listdir(parent_path):
                item_path = os.path.join(parent_path, item)
                if os.path.isdir(item_path):
                    folders.append(item_path)
        except OSError as e:
            print(f"Lỗi đọc thư mục {parent_path}: {e}")

        return folders

    @staticmethod
    def list_files(folder_path: str, extension: Optional[str] = None) -> List[str]:
        """
        Liệt kê các file trong một folder.

        Args:
            folder_path: Đường dẫn đến folder
            extension: Lọc theo đuôi file (vd: ".json")

        Returns:
            Danh sách đường dẫn các file
        """
        if not os.path.isdir(folder_path):
            return []

        files = []
        try:
            for item in os.listdir(folder_path):
                item_path = os.path.join(folder_path, item)
                if os.path.isfile(item_path):
                    if extension is None or item.endswith(extension):
                        files.append(item_path)
        except OSError as e:
            print(f"Lỗi đọc thư mục {folder_path}: {e}")

        return files

    @staticmethod
    def get_file_size(filepath: str) -> int:
        """
        Lấy kích thước file.

        Args:
            filepath: Đường dẫn đến file

        Returns:
            Kích thước file tính bằng bytes, -1 nếu lỗi
        """
        try:
            return os.path.getsize(filepath)
        except OSError:
            return -1

    @staticmethod
    def copy_file(src: str, dst: str) -> bool:
        """
        Copy file.

        Args:
            src: Đường dẫn file nguồn
            dst: Đường dẫn file đích

        Returns:
            True nếu copy thành công
        """
        try:
            shutil.copy2(src, dst)
            return True
        except OSError as e:
            print(f"Lỗi copy file {src} -> {dst}: {e}")
            return False

    @staticmethod
    def delete_file(filepath: str) -> bool:
        """
        Xóa file.

        Args:
            filepath: Đường dẫn đến file

        Returns:
            True nếu xóa thành công
        """
        try:
            if os.path.isfile(filepath):
                os.remove(filepath)
            return True
        except OSError as e:
            print(f"Lỗi xóa file {filepath}: {e}")
            return False

    @staticmethod
    def get_absolute_path(path: str) -> str:
        """
        Chuyển đổi thành đường dẫn tuyệt đối.

        Args:
            path: Đường dẫn cần chuyển đổi

        Returns:
            Đường dẫn tuyệt đối
        """
        return os.path.abspath(path)

    @staticmethod
    def join_paths(*paths: str) -> str:
        """
        Nối các phần đường dẫn.

        Args:
            *paths: Các phần đường dẫn

        Returns:
            Đường dẫn đã nối
        """
        return os.path.join(*paths)

    @staticmethod
    def get_parent_folder(path: str) -> str:
        """
        Lấy folder cha của đường dẫn.

        Args:
            path: Đường dẫn cần lấy folder cha

        Returns:
            Đường dẫn folder cha
        """
        return os.path.dirname(path)

    @staticmethod
    def get_filename(path: str, include_extension: bool = True) -> str:
        """
        Lấy tên file từ đường dẫn.

        Args:
            path: Đường dẫn đến file
            include_extension: Có bao gồm đuôi file không

        Returns:
            Tên file
        """
        filename = os.path.basename(path)
        if not include_extension:
            filename = os.path.splitext(filename)[0]
        return filename
