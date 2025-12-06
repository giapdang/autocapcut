"""
Main Controller - Controller chính điều phối ứng dụng.

Controller này quản lý:
- Khởi tạo và điều phối View và Model
- Xử lý sự kiện từ giao diện
- Gọi Service để thực hiện tác vụ
"""

from typing import List, Optional

from models.project import Project
from models.config import Config
from services.capcut_service import CapCutService
from services.file_service import FileService
from controllers.export_controller import ExportController
from services.automation_service import ExportStatus


class MainController:
    """
    Controller chính của ứng dụng.

    Class này điều phối toàn bộ luồng hoạt động của ứng dụng,
    kết nối View với Model và Services.
    """

    def __init__(self):
        """Khởi tạo MainController."""
        # Load config
        self.config = Config.load()

        # Khởi tạo services
        self.file_service = FileService()
        self.capcut_service = CapCutService(self.config)

        # Export controller (sẽ khởi tạo khi cần)
        self.export_controller: Optional[ExportController] = None

        # View reference (sẽ được set từ View)
        self.view = None

        # Danh sách projects
        self._projects: List[Project] = []
        self._selected_projects: List[Project] = []

    def set_view(self, view) -> None:
        """
        Đặt reference đến View.

        Args:
            view: MainWindow instance
        """
        self.view = view

        # Cập nhật View với config hiện tại
        if self.view:
            self.view.set_capcut_path(self.config.capcut_exe_path)
            self.view.set_data_path(self.config.data_folder_path)

    def auto_detect_paths(self) -> dict:
        """
        Tự động phát hiện đường dẫn CapCut.

        Returns:
            Dictionary với kết quả phát hiện
        """
        result = self.capcut_service.auto_detect()

        if result['capcut_exe']:
            self.config.capcut_exe_path = result['capcut_exe']
            if self.view:
                self.view.set_capcut_path(result['capcut_exe'])
                self.view.log(f"Tìm thấy CapCut.exe: {result['capcut_exe']}")

        if result['data_folder']:
            self.config.data_folder_path = result['data_folder']
            if self.view:
                self.view.set_data_path(result['data_folder'])
                self.view.log(f"Tìm thấy thư mục data: {result['data_folder']}")

        # Lưu config
        self.config.save()

        return result

    def set_capcut_path(self, path: str) -> bool:
        """
        Đặt đường dẫn CapCut.exe.

        Args:
            path: Đường dẫn đến CapCut.exe

        Returns:
            True nếu đường dẫn hợp lệ
        """
        if self.file_service.file_exists(path):
            self.config.capcut_exe_path = path
            self.config.save()
            self.capcut_service.update_config(self.config)

            if self.view:
                self.view.log(f"Đã cập nhật đường dẫn CapCut: {path}")
            return True
        else:
            if self.view:
                self.view.log(f"Đường dẫn không hợp lệ: {path}")
            return False

    def set_data_path(self, path: str) -> bool:
        """
        Đặt đường dẫn thư mục data CapCut.

        Args:
            path: Đường dẫn đến thư mục data

        Returns:
            True nếu đường dẫn hợp lệ
        """
        if self.file_service.folder_exists(path):
            self.config.data_folder_path = path
            self.config.save()
            self.capcut_service.update_config(self.config)

            if self.view:
                self.view.log(f"Đã cập nhật thư mục data: {path}")
            return True
        else:
            if self.view:
                self.view.log(f"Thư mục không hợp lệ: {path}")
            return False

    def load_projects(self) -> List[Project]:
        """
        Tải danh sách projects.

        Returns:
            Danh sách Project objects
        """
        if not self.config.data_folder_path:
            if self.view:
                self.view.log("Chưa cấu hình thư mục data CapCut")
                self.view.show_error("Vui lòng cấu hình thư mục data CapCut trước")
            return []

        if self.view:
            self.view.log("Đang tải danh sách projects...")

        # Tải projects (không bao gồm trash)
        self._projects = self.capcut_service.get_projects(include_trash=False)

        if self.view:
            self.view.log(f"Tìm thấy {len(self._projects)} project(s)")
            self.view.update_project_list(self._projects)

        return self._projects

    def get_projects(self) -> List[Project]:
        """
        Lấy danh sách projects đã load.

        Returns:
            Danh sách Project objects
        """
        return self._projects.copy()

    def select_project(self, project: Project, selected: bool = True) -> None:
        """
        Chọn/bỏ chọn project.

        Args:
            project: Project cần chọn
            selected: True để chọn, False để bỏ chọn
        """
        if selected and project not in self._selected_projects:
            self._selected_projects.append(project)
        elif not selected and project in self._selected_projects:
            self._selected_projects.remove(project)

    def select_all_projects(self) -> None:
        """Chọn tất cả projects."""
        self._selected_projects = self._projects.copy()
        if self.view:
            self.view.select_all_projects()

    def deselect_all_projects(self) -> None:
        """Bỏ chọn tất cả projects."""
        self._selected_projects = []
        if self.view:
            self.view.deselect_all_projects()

    def get_selected_projects(self) -> List[Project]:
        """
        Lấy danh sách projects đã chọn.

        Returns:
            Danh sách Project đã chọn
        """
        return self._selected_projects.copy()

    def set_selected_projects(self, projects: List[Project]) -> None:
        """
        Đặt danh sách projects đã chọn.

        Args:
            projects: Danh sách projects
        """
        self._selected_projects = projects.copy()

    def start_export(self) -> bool:
        """
        Bắt đầu xuất các project đã chọn.

        Returns:
            True nếu bắt đầu thành công
        """
        if not self._selected_projects:
            if self.view:
                self.view.show_warning("Vui lòng chọn ít nhất một project để xuất")
            return False

        if not self.config.capcut_exe_path:
            if self.view:
                self.view.show_error("Vui lòng cấu hình đường dẫn CapCut.exe")
            return False

        # Khởi tạo export controller
        self.export_controller = ExportController(
            config=self.config,
            log_callback=self._on_export_log,
            progress_callback=self._on_export_progress,
            status_callback=self._on_export_status,
            completion_callback=self._on_export_complete
        )

        # Bắt đầu xuất
        success = self.export_controller.start_export(self._selected_projects)

        if success and self.view:
            self.view.set_exporting_state(True)

        return success

    def cancel_export(self) -> None:
        """Hủy quá trình xuất."""
        if self.export_controller:
            self.export_controller.cancel_export()

            if self.view:
                self.view.set_exporting_state(False)

    def _on_export_log(self, message: str) -> None:
        """Callback khi có log từ export."""
        if self.view:
            self.view.log(message)

    def _on_export_progress(self, current: int, total: int, project_name: str) -> None:
        """Callback khi cập nhật tiến trình."""
        if self.view:
            self.view.update_progress(current, total, project_name)

    def _on_export_status(self, status: ExportStatus, message: str) -> None:
        """Callback khi cập nhật trạng thái."""
        if self.view:
            self.view.update_status(f"{status.value}: {message}")

    def _on_export_complete(self, success: bool, message: str) -> None:
        """Callback khi xuất hoàn thành."""
        if self.view:
            self.view.set_exporting_state(False)

            if success:
                self.view.show_info(message)
            else:
                self.view.show_warning(message)

    def is_exporting(self) -> bool:
        """
        Kiểm tra đang trong quá trình xuất không.

        Returns:
            True nếu đang xuất
        """
        if self.export_controller:
            return self.export_controller.is_running()
        return False

    def get_export_progress(self) -> dict:
        """
        Lấy thông tin tiến trình xuất.

        Returns:
            Dictionary chứa thông tin tiến trình
        """
        if self.export_controller:
            return self.export_controller.get_progress()
        return {}

    def validate_config(self) -> dict:
        """
        Kiểm tra cấu hình.

        Returns:
            Dictionary với kết quả kiểm tra
        """
        return self.config.validate()

    def save_config(self) -> bool:
        """
        Lưu cấu hình.

        Returns:
            True nếu lưu thành công
        """
        return self.config.save()

    def cleanup(self) -> None:
        """Dọn dẹp khi đóng ứng dụng."""
        # Hủy export nếu đang chạy
        if self.is_exporting():
            self.cancel_export()

        # Lưu config
        self.save_config()
