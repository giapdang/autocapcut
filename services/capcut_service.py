"""
CapCut Service - Service tương tác với CapCut.

Service này cung cấp các chức năng:
- Tìm đường dẫn CapCut.exe tự động
- Tìm thư mục data CapCut
- Đọc danh sách projects
- Parse metadata từ draft files
"""

import os
from typing import Optional, List
from models.project import Project
from models.config import Config
from services.file_service import FileService


class CapCutService:
    """
    Service tương tác với CapCut.

    Class này quản lý việc tìm kiếm và đọc thông tin
    từ các project CapCut trên máy.
    """

    # Đường dẫn mặc định trên Windows
    DEFAULT_EXE_PATHS = [
        r"C:\Program Files\CapCut\CapCut.exe",
        r"C:\Program Files (x86)\CapCut\CapCut.exe",
        os.path.expanduser(r"~\AppData\Local\CapCut\Apps\CapCut.exe"),
        os.path.expanduser(r"~\AppData\Local\Programs\CapCut\CapCut.exe"),
    ]

    DEFAULT_DATA_PATHS = [
        os.path.expanduser(
            r"~\AppData\Local\JianyingPro\User Data\Projects\com.lveditor.draft"
        ),
        os.path.expanduser(
            r"~\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft"
        ),
    ]

    def __init__(self, config: Optional[Config] = None):
        """
        Khởi tạo CapCutService.

        Args:
            config: Config object (tùy chọn)
        """
        self.config = config or Config()
        self.file_service = FileService()

    def find_capcut_exe(self) -> Optional[str]:
        """
        Tự động tìm đường dẫn CapCut.exe.

        Tìm kiếm trong các vị trí mặc định trên Windows.

        Returns:
            Đường dẫn đến CapCut.exe nếu tìm thấy, None nếu không
        """
        # Kiểm tra config trước
        if self.config.capcut_exe_path:
            if self.file_service.file_exists(self.config.capcut_exe_path):
                return self.config.capcut_exe_path

        # Tìm trong các đường dẫn mặc định
        for path in self.DEFAULT_EXE_PATHS:
            if self.file_service.file_exists(path):
                return path

        return None

    def find_data_folder(self) -> Optional[str]:
        """
        Tự động tìm thư mục data CapCut.

        Thư mục này thường nằm ở:
        - C:\\Users\\[Username]\\AppData\\Local\\JianyingPro\\User Data\\Projects
        - C:\\Users\\[Username]\\AppData\\Local\\CapCut\\User Data\\Projects

        Returns:
            Đường dẫn đến thư mục data nếu tìm thấy, None nếu không
        """
        # Kiểm tra config trước
        if self.config.data_folder_path:
            if self.file_service.folder_exists(self.config.data_folder_path):
                return self.config.data_folder_path

        # Tìm trong các đường dẫn mặc định
        for path in self.DEFAULT_DATA_PATHS:
            if self.file_service.folder_exists(path):
                return path

        return None

    def get_projects(self, include_trash: bool = False) -> List[Project]:
        """
        Lấy danh sách các project CapCut.

        Đọc từ thư mục data và parse metadata của từng project.

        Args:
            include_trash: Có bao gồm project trong thùng rác không

        Returns:
            Danh sách Project objects
        """
        projects = []

        # Tìm thư mục data
        data_folder = self.find_data_folder()
        if not data_folder:
            return projects

        # Liệt kê các folder con (mỗi folder là một project)
        project_folders = self.file_service.list_folders(data_folder)

        for folder_path in project_folders:
            project = Project.from_folder(folder_path)
            if project:
                # Lọc bỏ project trong thùng rác nếu cần
                if include_trash or not project.is_trash:
                    projects.append(project)

        # Sắp xếp theo ngày chỉnh sửa (mới nhất trước)
        projects.sort(
            key=lambda p: p.modified_date or p.created_date,
            reverse=True
        )

        return projects

    def get_project_by_id(self, project_id: str) -> Optional[Project]:
        """
        Lấy project theo ID.

        Args:
            project_id: ID của project

        Returns:
            Project object nếu tìm thấy, None nếu không
        """
        data_folder = self.find_data_folder()
        if not data_folder:
            return None

        project_path = os.path.join(data_folder, project_id)
        if self.file_service.folder_exists(project_path):
            return Project.from_folder(project_path)

        return None

    def validate_project(self, project: Project) -> bool:
        """
        Kiểm tra project có hợp lệ không.

        Args:
            project: Project cần kiểm tra

        Returns:
            True nếu project hợp lệ và có thể xuất
        """
        if not project.exists():
            return False

        # Kiểm tra file draft_content.json tồn tại
        draft_path = project.get_draft_path()
        return self.file_service.file_exists(draft_path)

    def refresh_project(self, project: Project) -> Optional[Project]:
        """
        Làm mới thông tin project từ disk.

        Args:
            project: Project cần làm mới

        Returns:
            Project object mới với thông tin cập nhật
        """
        return Project.from_folder(project.path)

    def get_project_count(self, include_trash: bool = False) -> int:
        """
        Đếm số lượng project.

        Args:
            include_trash: Có bao gồm project trong thùng rác không

        Returns:
            Số lượng project
        """
        return len(self.get_projects(include_trash))

    def update_config(self, config: Config) -> None:
        """
        Cập nhật config.

        Args:
            config: Config mới
        """
        self.config = config

    def auto_detect(self) -> dict:
        """
        Tự động phát hiện các đường dẫn CapCut.

        Returns:
            Dictionary với kết quả phát hiện
        """
        return {
            'capcut_exe': self.find_capcut_exe(),
            'data_folder': self.find_data_folder()
        }
