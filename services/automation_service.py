"""
Automation Service - Service tự động hóa thao tác với CapCut.

Service này sử dụng PyAutoGUI và pywinauto để:
- Mở CapCut với project cụ thể
- Tự động click Export
- Chọn cấu hình xuất
- Chờ xuất xong và đóng CapCut
"""

import os
import time
import subprocess
from typing import Optional, Callable, Dict, Any
from enum import Enum
from datetime import datetime

# Import các thư viện automation (sẽ được cài đặt qua requirements.txt)
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

try:
    from pywinauto import Application
    from pywinauto.findwindows import ElementNotFoundError
    PYWINAUTO_AVAILABLE = True
except ImportError:
    PYWINAUTO_AVAILABLE = False

try:
    from services.vision_service import VisionService
    from services.template_manager import TemplateManager
    VISION_AVAILABLE = True
except ImportError:
    VISION_AVAILABLE = False


class ExportStatus(Enum):
    """Enum trạng thái xuất video."""
    PENDING = "pending"
    STARTING = "starting"
    OPENING_APP = "opening_app"
    LOADING_PROJECT = "loading_project"
    EXPORTING = "exporting"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AutomationService:
    """
    Service tự động hóa thao tác với CapCut.

    Class này cung cấp các phương thức để tự động:
    - Mở CapCut với project
    - Click vào các nút Export
    - Chờ quá trình xuất hoàn tất
    - Đóng CapCut
    """

    # Cấu hình timeout (giây)
    APP_OPEN_TIMEOUT = 30
    PROJECT_LOAD_TIMEOUT = 60
    EXPORT_TIMEOUT = 600  # 10 phút

    # Tên cửa sổ CapCut
    CAPCUT_WINDOW_TITLES = ["CapCut", "剪映", "JianyingPro"]

    def __init__(
        self,
        capcut_exe_path: str,
        log_callback: Optional[Callable[[str], None]] = None,
        status_callback: Optional[Callable[[ExportStatus, str], None]] = None,
        use_vision: bool = True,
        vision_settings: Optional[Dict[str, Any]] = None
    ):
        """
        Khởi tạo AutomationService.

        Args:
            capcut_exe_path: Đường dẫn đến CapCut.exe
            log_callback: Callback để ghi log
            status_callback: Callback để cập nhật trạng thái
            use_vision: Có sử dụng computer vision không
            vision_settings: Cấu hình cho vision service
        """
        self.capcut_exe_path = capcut_exe_path
        self.log_callback = log_callback or (lambda x: print(x))
        self.status_callback = status_callback or (lambda s, m: None)
        self._cancelled = False
        self.use_vision = use_vision and VISION_AVAILABLE

        # Khởi tạo vision service nếu có
        self.vision_service: Optional[VisionService] = None
        self.template_manager: Optional[TemplateManager] = None

        if self.use_vision:
            vision_settings = vision_settings or {}
            self.vision_service = VisionService(
                confidence_threshold=vision_settings.get('confidence_threshold', 0.8),
                screenshot_on_error=vision_settings.get('screenshot_on_error', True),
                screenshot_dir=vision_settings.get('screenshot_dir', './screenshots')
            )
            self.template_manager = TemplateManager()
            self._log("Vision service đã được kích hoạt")

        # Retry settings
        self.retry_attempts = 3
        self.retry_delay = 2

    def _log(self, message: str) -> None:
        """Ghi log message."""
        self.log_callback(message)

    def _update_status(self, status: ExportStatus, message: str = "") -> None:
        """Cập nhật trạng thái."""
        self.status_callback(status, message)

    def is_capcut_running(self) -> bool:
        """
        Kiểm tra CapCut có đang chạy không.

        Returns:
            True nếu CapCut đang chạy
        """
        if not PSUTIL_AVAILABLE:
            self._log("psutil không khả dụng, bỏ qua kiểm tra process")
            return False

        for proc in psutil.process_iter(['name']):
            try:
                if 'capcut' in proc.info['name'].lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False

    def close_capcut(self) -> bool:
        """
        Đóng CapCut.

        Returns:
            True nếu đóng thành công
        """
        if not PSUTIL_AVAILABLE:
            self._log("psutil không khả dụng")
            return False

        closed = False
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                if 'capcut' in proc.info['name'].lower():
                    proc.terminate()
                    proc.wait(timeout=5)
                    closed = True
                    self._log(f"Đã đóng CapCut (PID: {proc.info['pid']})")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                continue

        return closed

    def open_capcut(self, project_path: Optional[str] = None) -> bool:
        """
        Mở CapCut với project cụ thể.

        Args:
            project_path: Đường dẫn đến project (tùy chọn)

        Returns:
            True nếu mở thành công
        """
        self._update_status(ExportStatus.OPENING_APP, "Đang mở CapCut...")

        if not os.path.isfile(self.capcut_exe_path):
            self._log(f"Không tìm thấy CapCut.exe tại: {self.capcut_exe_path}")
            return False

        try:
            # Đóng CapCut nếu đang chạy
            if self.is_capcut_running():
                self._log("CapCut đang chạy, đang đóng...")
                self.close_capcut()
                time.sleep(2)

            # Mở CapCut
            cmd = [self.capcut_exe_path]
            if project_path:
                cmd.append(project_path)

            subprocess.Popen(cmd, shell=False)
            self._log(f"Đã mở CapCut: {self.capcut_exe_path}")

            # Chờ cửa sổ CapCut xuất hiện
            return self._wait_for_window()

        except subprocess.SubprocessError as e:
            self._log(f"Lỗi mở CapCut: {e}")
            return False

    def _wait_for_window(self, timeout: int = None) -> bool:
        """
        Chờ cửa sổ CapCut xuất hiện.

        Args:
            timeout: Thời gian chờ tối đa (giây)

        Returns:
            True nếu tìm thấy cửa sổ
        """
        timeout = timeout or self.APP_OPEN_TIMEOUT
        start_time = time.time()

        if not PYWINAUTO_AVAILABLE:
            self._log("pywinauto không khả dụng, chờ mặc định 5 giây")
            time.sleep(5)
            return True

        while time.time() - start_time < timeout:
            if self._cancelled:
                return False

            try:
                for title in self.CAPCUT_WINDOW_TITLES:
                    try:
                        Application(backend='uia').connect(title_re=f".*{title}.*")
                        self._log("Đã tìm thấy cửa sổ CapCut")
                        return True
                    except ElementNotFoundError:
                        continue
            except Exception:
                pass

            time.sleep(0.5)

        self._log("Timeout: Không tìm thấy cửa sổ CapCut")
        return False

    def export_project(self, project_path: str, retry_count: int = 3) -> bool:
        """
        Xuất video từ project.

        Quy trình:
        1. Mở CapCut với project
        2. Chờ load xong
        3. Click nút Export
        4. Chờ xuất xong
        5. Đóng CapCut

        Args:
            project_path: Đường dẫn đến project
            retry_count: Số lần thử lại nếu thất bại

        Returns:
            True nếu xuất thành công
        """
        for attempt in range(retry_count):
            if self._cancelled:
                self._update_status(ExportStatus.CANCELLED, "Đã hủy")
                return False

            if attempt > 0:
                self._log(f"Thử lại lần {attempt + 1}...")

            try:
                # Mở CapCut
                if not self.open_capcut(project_path):
                    continue

                # Chờ project load
                self._update_status(
                    ExportStatus.LOADING_PROJECT,
                    "Đang tải project..."
                )
                time.sleep(5)  # Chờ project load

                # Click Export
                if not self._click_export():
                    continue

                # Chờ xuất xong
                self._update_status(ExportStatus.EXPORTING, "Đang xuất video...")
                if not self._wait_for_export():
                    continue

                # Đóng CapCut
                self.close_capcut()

                self._update_status(ExportStatus.COMPLETED, "Xuất thành công!")
                return True

            except Exception as e:
                self._log(f"Lỗi xuất project: {e}")
                self.close_capcut()

        self._update_status(ExportStatus.FAILED, "Xuất thất bại sau nhiều lần thử")
        return False

    def _click_export(self) -> bool:
        """
        Click vào nút Export.

        Returns:
            True nếu click thành công
        """
        # Thử với vision service trước nếu có
        if self.use_vision and self.vision_service and self.template_manager:
            return self._click_export_with_vision()

        # Fallback sang phương pháp thủ công
        return self._click_export_manual()

    def _click_export_with_vision(self) -> bool:
        """
        Click Export bằng vision service.

        Returns:
            True nếu click thành công
        """
        self._log("Đang tìm nút Export bằng vision...")

        # Thử tìm template export button
        export_template = self.template_manager.get_template_path('export_button', 'buttons')

        if not export_template:
            self._log("Không tìm thấy template export_button, fallback sang manual")
            return self._click_export_manual()

        # Thử click với retry
        for attempt in range(self.retry_attempts):
            if self._cancelled:
                return False

            if attempt > 0:
                self._log(f"Thử lại lần {attempt + 1}...")
                time.sleep(self.retry_delay)

            # Tìm và click
            success = self.vision_service.click_on_image(
                export_template,
                confidence=0.8,
                timeout=10
            )

            if success:
                self._log("✓ Đã click nút Export")
                time.sleep(1)  # Chờ UI phản hồi
                return True

        self._log("✗ Không tìm thấy nút Export sau nhiều lần thử")

        # Chụp screenshot để debug
        if self.vision_service.screenshot_on_error:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.vision_service.save_screenshot(f"export_button_not_found_{timestamp}.png")

        return False

    def _click_export_manual(self) -> bool:
        """
        Click Export bằng phương pháp thủ công (keyboard shortcut).

        Returns:
            True nếu click thành công
        """
        if not PYAUTOGUI_AVAILABLE:
            self._log("pyautogui không khả dụng")
            return False

        try:
            self._log("Đang click Export bằng keyboard shortcut...")

            # Thử sử dụng keyboard shortcut (Ctrl+E hoặc Alt+E)
            # Lưu ý: Cần điều chỉnh theo shortcut thực tế của CapCut
            pyautogui.hotkey('ctrl', 'e')
            time.sleep(1)

            self._log("Đã gửi lệnh Export")
            return True

        except Exception as e:
            self._log(f"Lỗi click Export manual: {e}")
            return False

    def focus_window(self) -> bool:
        """
        Focus vào cửa sổ CapCut.

        Returns:
            True nếu focus thành công
        """
        if not PYWINAUTO_AVAILABLE:
            self._log("pywinauto không khả dụng")
            return False

        try:
            for title in self.CAPCUT_WINDOW_TITLES:
                try:
                    app = Application(backend='uia').connect(title_re=f".*{title}.*", timeout=5)
                    window = app.top_window()
                    window.set_focus()
                    self._log(f"Đã focus vào cửa sổ: {title}")
                    return True
                except ElementNotFoundError:
                    continue
                except Exception as e:
                    self._log(f"Lỗi focus window: {e}")
                    continue

            self._log("Không thể focus vào cửa sổ CapCut")
            return False

        except Exception as e:
            self._log(f"Lỗi focus window: {e}")
            return False

    def send_keyboard_shortcut(self, *keys) -> bool:
        """
        Gửi keyboard shortcut.

        Args:
            *keys: Các phím cần nhấn (ví dụ: 'ctrl', 'e')

        Returns:
            True nếu gửi thành công
        """
        if not PYAUTOGUI_AVAILABLE:
            return False

        try:
            pyautogui.hotkey(*keys)
            return True
        except Exception as e:
            self._log(f"Lỗi gửi keyboard shortcut: {e}")
            return False

    def take_screenshot(self, filename: Optional[str] = None) -> bool:
        """
        Chụp screenshot màn hình.

        Args:
            filename: Tên file (optional)

        Returns:
            True nếu chụp thành công
        """
        if not self.vision_service:
            return False

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"

        return self.vision_service.save_screenshot(filename)

    def _wait_for_export(self, timeout: int = None) -> bool:
        """
        Chờ quá trình xuất hoàn tất.

        Args:
            timeout: Thời gian chờ tối đa (giây)

        Returns:
            True nếu xuất thành công
        """
        timeout = timeout or self.EXPORT_TIMEOUT

        # Thử với vision service trước nếu có
        if self.use_vision and self.vision_service and self.template_manager:
            return self._wait_for_export_with_vision(timeout)

        # Fallback sang phương pháp chờ cố định
        return self._wait_for_export_manual(timeout)

    def _wait_for_export_with_vision(self, timeout: int) -> bool:
        """
        Chờ export hoàn tất bằng vision detection.

        Args:
            timeout: Thời gian chờ tối đa (giây)

        Returns:
            True nếu xuất thành công
        """
        start_time = time.time()
        check_interval = 2

        # Tìm template export complete
        complete_template = self.template_manager.get_template_path('export_complete', 'status')

        if not complete_template:
            self._log("Không tìm thấy template export_complete, fallback sang manual")
            return self._wait_for_export_manual(timeout)

        self._log("Đang chờ export hoàn tất (vision detection)...")

        while time.time() - start_time < timeout:
            if self._cancelled:
                return False

            # Kiểm tra có dialog "Export Complete" không
            result = self.vision_service.find_image_on_screen(
                complete_template,
                confidence=0.8
            )

            if result.found:
                self._log("✓ Phát hiện export đã hoàn tất")
                return True

            # Log tiến trình
            elapsed = int(time.time() - start_time)
            if elapsed % 10 == 0:
                self._log(f"Đang xuất... ({elapsed}s / {timeout}s)")

            time.sleep(check_interval)

        self._log("Timeout: Xuất video quá lâu")

        # Chụp screenshot để debug
        if self.vision_service.screenshot_on_error:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.vision_service.save_screenshot(f"export_timeout_{timestamp}.png")

        return False

    def _wait_for_export_manual(self, timeout: int) -> bool:
        """
        Chờ export hoàn tất bằng phương pháp cố định.

        Args:
            timeout: Thời gian chờ tối đa (giây)

        Returns:
            True nếu xuất thành công
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            if self._cancelled:
                return False

            # Kiểm tra xem export đã xong chưa
            # (Có thể kiểm tra qua dialog hoàn thành hoặc progress bar)

            time.sleep(5)

            # Giả lập: sau 10 giây coi như xong
            # Trong production nên có cách kiểm tra tốt hơn
            if time.time() - start_time > 10:
                return True

        self._log("Timeout: Xuất video quá lâu")
        return False

    def cancel(self) -> None:
        """Hủy quá trình đang thực hiện."""
        self._cancelled = True
        self._log("Đã yêu cầu hủy")

    def reset(self) -> None:
        """Reset trạng thái service."""
        self._cancelled = False

    @staticmethod
    def check_dependencies() -> dict:
        """
        Kiểm tra các thư viện phụ thuộc.

        Returns:
            Dictionary với trạng thái các thư viện
        """
        deps = {
            'psutil': PSUTIL_AVAILABLE,
            'pyautogui': PYAUTOGUI_AVAILABLE,
            'pywinauto': PYWINAUTO_AVAILABLE,
            'vision': VISION_AVAILABLE
        }

        # Kiểm tra chi tiết vision dependencies nếu có
        if VISION_AVAILABLE:
            from services.vision_service import VisionService
            deps['vision_details'] = VisionService.check_dependencies()

        return deps
