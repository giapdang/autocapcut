"""
CapCut Service - Service tương tác với CapCut.

Service này cung cấp các chức năng:
- Tìm đường dẫn CapCut.exe tự động
- Tìm thư mục data CapCut
- Đọc danh sách projects
- Parse metadata từ draft files
"""

import os
import logging
from typing import Optional, List
from models.project import Project
from models.config import Config
from services.file_service import FileService

# Setup logger
logger = logging.getLogger(__name__)


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

    # Các thư mục data có thể có - quét nhiều cấu trúc
    DEFAULT_DATA_PATHS = [
        os.path.expanduser(
            r"~\AppData\Local\JianyingPro\User Data\Projects\com.lveditor.draft"
        ),
        os.path.expanduser(
            r"~\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft"
        ),
        # Thêm các đường dẫn khác
        os.path.expanduser(r"~\AppData\Local\JianyingPro\User Data\Projects"),
        os.path.expanduser(r"~\AppData\Local\CapCut\User Data\Projects"),
        os.path.expanduser(r"~\AppData\Local\JianyingPro\Projects"),
        os.path.expanduser(r"~\AppData\Local\CapCut\Projects"),
        os.path.expanduser(r"~\AppData\Local\JianyingPro\AutoSave"),
        os.path.expanduser(r"~\AppData\Local\CapCut\AutoSave"),
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

    def get_projects(self, include_trash: bool = False, include_cloud: bool = False) -> List[Project]:
        """
        Lấy danh sách các project CapCut.

        Đọc từ thư mục data và parse metadata của từng project.
        Quét nhiều cấu trúc thư mục và lọc theo các tiêu chí.

        Args:
            include_trash: Có bao gồm project trong thùng rác không
            include_cloud: Có bao gồm cloud project không

        Returns:
            Danh sách Project objects
        """
        projects = []
        scanned_paths = set()  # Tránh quét trùng lặp

        # Tìm thư mục data
        data_folder = self.find_data_folder()
        if not data_folder:
            logger.warning("Không tìm thấy thư mục data CapCut")
            return projects

        # Danh sách các thư mục cần quét
        folders_to_scan = [data_folder]
        
        # Thêm các thư mục con phổ biến nếu tồn tại
        parent_folder = os.path.dirname(data_folder)
        possible_subfolders = [
            os.path.join(parent_folder, 'Projects'),
            os.path.join(parent_folder, 'AutoSave'),
            os.path.join(parent_folder, 'com.lveditor.draft'),
        ]
        
        for subfolder in possible_subfolders:
            if os.path.isdir(subfolder) and subfolder not in folders_to_scan:
                folders_to_scan.append(subfolder)

        logger.info(f"Quét {len(folders_to_scan)} thư mục để tìm projects...")

        # Quét từng thư mục
        for scan_folder in folders_to_scan:
            if not os.path.isdir(scan_folder):
                continue
                
            logger.debug(f"Đang quét: {scan_folder}")
            
            # Liệt kê các folder con (mỗi folder là một project)
            project_folders = self.file_service.list_folders(scan_folder)
            
            for folder_path in project_folders:
                # Tránh quét trùng
                if folder_path in scanned_paths:
                    continue
                scanned_paths.add(folder_path)
                
                # Kiểm tra xem folder có chứa metadata không
                has_metadata = self._has_project_metadata(folder_path)
                if not has_metadata:
                    logger.debug(f"Bỏ qua {folder_path}: không tìm thấy metadata")
                    continue
                
                project = Project.from_folder(folder_path)
                if project:
                    # Lọc theo các tiêu chí
                    if not include_trash and project.is_trash:
                        logger.info(f"Bỏ qua {project.name}: project trong thùng rác")
                        continue
                    
                    if not include_cloud and project.is_cloud:
                        logger.info(f"Bỏ qua {project.name}: cloud project")
                        continue
                    
                    # Kiểm tra file draft_content.json tồn tại (bắt buộc để export)
                    draft_path = project.get_draft_path()
                    if not os.path.exists(draft_path):
                        logger.info(f"Bỏ qua {project.name}: thiếu file draft_content.json")
                        continue
                    
                    logger.info(f"Tìm thấy project: {project.name}")
                    projects.append(project)
                else:
                    logger.warning(f"Không thể tạo project từ {folder_path}")

        # Sắp xếp theo ngày chỉnh sửa (mới nhất trước)
        projects.sort(
            key=lambda p: p.modified_date or p.created_date,
            reverse=True
        )

        logger.info(f"Tổng cộng tìm thấy {len(projects)} project hợp lệ")
        return projects

    def _has_project_metadata(self, folder_path: str) -> bool:
        """
        Kiểm tra folder có chứa file metadata của project không.
        
        Args:
            folder_path: Đường dẫn đến folder
            
        Returns:
            True nếu có ít nhất một file metadata
        """
        metadata_files = [
            'draft_info.json',
            'draft_content.json',
            'project.json',
            'metadata.json'
        ]
        
        for metadata_file in metadata_files:
            if os.path.exists(os.path.join(folder_path, metadata_file)):
                return True
        
        return False

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
