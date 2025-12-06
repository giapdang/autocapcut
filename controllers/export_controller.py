"""
Export Controller - Controller quản lý việc xuất video.

Controller này điều khiển:
- Queue các projects cần xuất
- Thực hiện xuất từng project
- Cập nhật tiến trình lên View
"""

import threading
import queue
from typing import List, Optional, Callable
from enum import Enum

from models.project import Project
from models.config import Config
from services.automation_service import AutomationService, ExportStatus


class ExportState(Enum):
    """Enum trạng thái của Export Controller."""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class ExportController:
    """
    Controller quản lý việc xuất video.

    Class này điều phối quá trình xuất nhiều project,
    quản lý queue và cập nhật trạng thái lên View.
    """

    def __init__(
        self,
        config: Config,
        log_callback: Optional[Callable[[str], None]] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        status_callback: Optional[Callable[[ExportStatus, str], None]] = None,
        completion_callback: Optional[Callable[[bool, str], None]] = None
    ):
        """
        Khởi tạo ExportController.

        Args:
            config: Cấu hình ứng dụng
            log_callback: Callback ghi log (message)
            progress_callback: Callback cập nhật tiến trình (current, total, name)
            status_callback: Callback cập nhật trạng thái (status, message)
            completion_callback: Callback khi hoàn thành (success, message)
        """
        self.config = config
        self.log_callback = log_callback or (lambda x: print(x))
        self.progress_callback = progress_callback or (lambda c, t, n: None)
        self.status_callback = status_callback or (lambda s, m: None)
        self.completion_callback = completion_callback or (lambda s, m: None)

        self._state = ExportState.IDLE
        self._export_queue: queue.Queue = queue.Queue()
        self._current_project: Optional[Project] = None
        self._export_thread: Optional[threading.Thread] = None
        self._automation_service: Optional[AutomationService] = None

        self._total_projects = 0
        self._completed_count = 0
        self._failed_count = 0
        self._failed_projects: List[Project] = []

    def _log(self, message: str) -> None:
        """Ghi log message."""
        self.log_callback(message)

    def _update_progress(self) -> None:
        """Cập nhật tiến trình."""
        project_name = self._current_project.name if self._current_project else ""
        self.progress_callback(
            self._completed_count + 1,
            self._total_projects,
            project_name
        )

    def _update_status(self, status: ExportStatus, message: str = "") -> None:
        """Cập nhật trạng thái."""
        self.status_callback(status, message)

    def start_export(self, projects: List[Project]) -> bool:
        """
        Bắt đầu xuất danh sách project.

        Args:
            projects: Danh sách project cần xuất

        Returns:
            True nếu bắt đầu thành công
        """
        if self._state == ExportState.RUNNING:
            self._log("Đang trong quá trình xuất, không thể bắt đầu mới")
            return False

        if not projects:
            self._log("Không có project nào để xuất")
            return False

        # Kiểm tra config
        if not self.config.capcut_exe_path:
            self._log("Chưa cấu hình đường dẫn CapCut.exe")
            return False

        # Reset state
        self._reset_state()

        # Thêm project vào queue
        self._total_projects = len(projects)
        for project in projects:
            self._export_queue.put(project)

        self._log(f"Bắt đầu xuất {self._total_projects} project(s)")

        # Khởi tạo automation service
        self._automation_service = AutomationService(
            capcut_exe_path=self.config.capcut_exe_path,
            log_callback=self._log,
            status_callback=self._update_status
        )

        # Bắt đầu thread xuất
        self._state = ExportState.RUNNING
        self._export_thread = threading.Thread(target=self._export_worker, daemon=True)
        self._export_thread.start()

        return True

    def _export_worker(self) -> None:
        """Worker thread thực hiện xuất video."""
        while not self._export_queue.empty() and self._state == ExportState.RUNNING:
            try:
                # Lấy project tiếp theo từ queue
                project = self._export_queue.get_nowait()
                self._current_project = project

                self._log(f"\n{'='*50}")
                self._log(f"Đang xuất: {project.name}")
                self._log(f"Project {self._completed_count + 1}/{self._total_projects}")
                self._log(f"{'='*50}")

                self._update_progress()
                self._update_status(ExportStatus.STARTING, f"Bắt đầu xuất: {project.name}")

                # Thực hiện xuất
                success = self._automation_service.export_project(project.path)

                if success:
                    self._completed_count += 1
                    self._log(f"✓ Xuất thành công: {project.name}")
                else:
                    self._failed_count += 1
                    self._failed_projects.append(project)
                    self._log(f"✗ Xuất thất bại: {project.name}")

                self._export_queue.task_done()

            except queue.Empty:
                break
            except Exception as e:
                self._log(f"Lỗi không mong đợi: {e}")
                self._failed_count += 1
                if self._current_project:
                    self._failed_projects.append(self._current_project)

        # Hoàn thành
        self._on_export_complete()

    def _on_export_complete(self) -> None:
        """Xử lý khi xuất hoàn thành."""
        self._state = ExportState.COMPLETED
        self._current_project = None

        # Tạo thông báo kết quả
        total = self._total_projects
        success = self._completed_count
        failed = self._failed_count

        if failed == 0:
            message = f"Hoàn thành! Đã xuất {success}/{total} project(s)"
            self._log(f"\n🎉 {message}")
            self.completion_callback(True, message)
        else:
            message = f"Hoàn thành với lỗi: {success} thành công, {failed} thất bại"
            self._log(f"\n⚠️ {message}")

            # Log các project thất bại
            if self._failed_projects:
                self._log("Projects thất bại:")
                for p in self._failed_projects:
                    self._log(f"  - {p.name}")

            self.completion_callback(False, message)

    def pause_export(self) -> None:
        """Tạm dừng quá trình xuất."""
        if self._state == ExportState.RUNNING:
            self._state = ExportState.PAUSED
            self._log("Đã tạm dừng xuất")

    def resume_export(self) -> None:
        """Tiếp tục quá trình xuất."""
        if self._state == ExportState.PAUSED:
            self._state = ExportState.RUNNING
            self._log("Tiếp tục xuất")

            # Khởi động lại worker thread
            self._export_thread = threading.Thread(target=self._export_worker, daemon=True)
            self._export_thread.start()

    def cancel_export(self) -> None:
        """Hủy quá trình xuất."""
        if self._state in [ExportState.RUNNING, ExportState.PAUSED]:
            self._state = ExportState.CANCELLED

            # Hủy automation service
            if self._automation_service:
                self._automation_service.cancel()
                self._automation_service.close_capcut()

            # Clear queue
            while not self._export_queue.empty():
                try:
                    self._export_queue.get_nowait()
                    self._export_queue.task_done()
                except queue.Empty:
                    break

            self._log("Đã hủy quá trình xuất")
            self.completion_callback(False, "Đã hủy xuất")

    def _reset_state(self) -> None:
        """Reset trạng thái controller."""
        self._state = ExportState.IDLE
        self._total_projects = 0
        self._completed_count = 0
        self._failed_count = 0
        self._failed_projects = []
        self._current_project = None

        # Clear queue
        while not self._export_queue.empty():
            try:
                self._export_queue.get_nowait()
            except queue.Empty:
                break

        if self._automation_service:
            self._automation_service.reset()

    def get_state(self) -> ExportState:
        """
        Lấy trạng thái hiện tại.

        Returns:
            ExportState hiện tại
        """
        return self._state

    def get_progress(self) -> dict:
        """
        Lấy thông tin tiến trình.

        Returns:
            Dictionary chứa thông tin tiến trình
        """
        return {
            'state': self._state.value,
            'total': self._total_projects,
            'completed': self._completed_count,
            'failed': self._failed_count,
            'remaining': self._export_queue.qsize(),
            'current_project': self._current_project.name if self._current_project else None
        }

    def is_running(self) -> bool:
        """
        Kiểm tra đang trong quá trình xuất không.

        Returns:
            True nếu đang xuất
        """
        return self._state == ExportState.RUNNING

    def get_failed_projects(self) -> List[Project]:
        """
        Lấy danh sách project xuất thất bại.

        Returns:
            Danh sách Project thất bại
        """
        return self._failed_projects.copy()
