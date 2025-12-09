"""
Export Controller - Controller quản lý việc xuất video.

Controller này điều khiển:
- Queue các projects cần xuất
- Thực hiện xuất từng project
- Cập nhật tiến trình lên View
- Ghi lịch sử vào database
"""

import threading
import queue
from typing import List, Optional, Callable
from enum import Enum
from datetime import datetime

from models.project import Project
from models.config import Config
from models.database import Database, ExportHistory
from services.automation_service import AutomationService, ExportStatus
from utils.error_handler import ErrorHandler, ErrorSeverity


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
        completion_callback: Optional[Callable[[bool, str], None]] = None,
        use_database: bool = True
    ):
        """
        Khởi tạo ExportController.

        Args:
            config: Cấu hình ứng dụng
            log_callback: Callback ghi log (message)
            progress_callback: Callback cập nhật tiến trình (current, total, name)
            status_callback: Callback cập nhật trạng thái (status, message)
            completion_callback: Callback khi hoàn thành (success, message)
            use_database: Có sử dụng database không
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

        # Database and error handling
        self.use_database = use_database
        self.database: Optional[Database] = None
        self.error_handler: Optional[ErrorHandler] = None

        if use_database:
            try:
                self.database = Database()
                self.error_handler = ErrorHandler(
                    screenshot_on_error=config.vision_settings.screenshot_on_error,
                    screenshot_dir=config.vision_settings.screenshot_dir
                )
                self._log("Database và error handler đã được kích hoạt")
            except Exception as e:
                self._log(f"Lỗi khởi tạo database: {e}")
                self.use_database = False

        # Current export history ID
        self._current_export_history_id: Optional[int] = None

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
            status_callback=self._update_status,
            use_vision=self.config.automation_settings.use_vision_detection,
            vision_settings=self.config.vision_settings.to_dict()
        )

        # Cập nhật retry settings
        self._automation_service.retry_attempts = self.config.automation_settings.retry_attempts
        self._automation_service.retry_delay = self.config.automation_settings.retry_delay

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

                # Bắt đầu tracking trong database
                start_time = datetime.now()
                if self.use_database and self.database:
                    history = ExportHistory(
                        project_id=project.id,
                        project_name=project.name,
                        started_at=start_time,
                        status='running'
                    )
                    self._current_export_history_id = self.database.add_export_history(history)

                # Thực hiện xuất
                success = self._automation_service.export_project(project.path)

                # Tính thời gian
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()

                if success:
                    self._completed_count += 1
                    self._log(f"✓ Xuất thành công: {project.name} ({duration:.1f}s)")

                    # Cập nhật database
                    if self.use_database and self.database and self._current_export_history_id:
                        self.database.update_export_history(
                            self._current_export_history_id,
                            completed_at=end_time.isoformat(),
                            duration=duration,
                            status='success'
                        )
                else:
                    self._failed_count += 1
                    self._failed_projects.append(project)
                    self._log(f"✗ Xuất thất bại: {project.name}")

                    # Cập nhật database
                    if self.use_database and self.database and self._current_export_history_id:
                        self.database.update_export_history(
                            self._current_export_history_id,
                            completed_at=end_time.isoformat(),
                            duration=duration,
                            status='failed',
                            error_message='Export thất bại'
                        )

                self._export_queue.task_done()

            except queue.Empty:
                break
            except Exception as e:
                self._log(f"Lỗi không mong đợi: {e}")
                self._failed_count += 1
                if self._current_project:
                    self._failed_projects.append(self._current_project)

                # Xử lý lỗi với error handler
                if self.error_handler:
                    self.error_handler.handle_error(
                        e,
                        f"Lỗi xuất project: {self._current_project.name if self._current_project else 'Unknown'}",
                        severity=ErrorSeverity.ERROR,
                        context={'project': self._current_project.to_dict() if self._current_project else None}
                    )

                # Cập nhật database
                if self.use_database and self.database and self._current_export_history_id:
                    self.database.update_export_history(
                        self._current_export_history_id,
                        completed_at=datetime.now().isoformat(),
                        status='failed',
                        error_message=str(e)
                    )

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

    def batch_export_with_vision(
        self,
        projects: List[Project],
        auto_retry_failed: bool = True
    ) -> bool:
        """
        Xuất hàng loạt với vision detection.

        Args:
            projects: Danh sách projects cần xuất
            auto_retry_failed: Có tự động retry các project thất bại không

        Returns:
            True nếu bắt đầu thành công
        """
        # Đảm bảo vision detection được bật
        if self._automation_service:
            self._automation_service.use_vision = True

        # Bắt đầu export
        success = self.start_export(projects)

        # TODO: Implement auto-retry logic nếu cần
        # if auto_retry_failed:
        #     # Retry các project thất bại sau khi hoàn thành

        return success

    def get_export_statistics(self) -> dict:
        """
        Lấy thống kê xuất video.

        Returns:
            Dictionary chứa thống kê
        """
        stats = {
            'current_session': {
                'total': self._total_projects,
                'completed': self._completed_count,
                'failed': self._failed_count,
                'remaining': self._export_queue.qsize(),
                'state': self._state.value
            }
        }

        # Thêm thống kê từ database nếu có
        if self.use_database and self.database:
            try:
                stats['all_time'] = self.database.get_export_statistics()
            except Exception as e:
                self._log(f"Lỗi lấy thống kê từ database: {e}")

        # Thêm thống kê lỗi nếu có
        if self.error_handler:
            stats['errors'] = self.error_handler.get_statistics()

        return stats
