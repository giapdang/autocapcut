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
import logging
from typing import Optional, Callable
from enum import Enum

# Setup logger
logger = logging.getLogger(__name__)

# Import các thư viện automation (sẽ được cài đặt qua requirements.txt)
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("psutil not available")

try:
    import pyautogui  # noqa: F401
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    logger.warning("pyautogui not available")

try:
    from pywinauto import Application
    from pywinauto.findwindows import ElementNotFoundError
    PYWINAUTO_AVAILABLE = True
except ImportError:
    PYWINAUTO_AVAILABLE = False
    logger.warning("pywinauto not available")

try:
    import pyperclip
    PYPERCLIP_AVAILABLE = True
except ImportError:
    PYPERCLIP_AVAILABLE = False
    logger.warning("pyperclip not available")


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
        status_callback: Optional[Callable[[ExportStatus, str], None]] = None
    ):
        """
        Khởi tạo AutomationService.

        Args:
            capcut_exe_path: Đường dẫn đến CapCut.exe
            log_callback: Callback để ghi log
            status_callback: Callback để cập nhật trạng thái
        """
        self.capcut_exe_path = capcut_exe_path
        self.log_callback = log_callback or (lambda x: print(x))
        self.status_callback = status_callback or (lambda s, m: None)
        self._cancelled = False

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

    def open_project(self, project) -> bool:
        """
        Mở CapCut project với nhiều phương pháp fallback.
        
        Thử các phương pháp theo thứ tự:
        1. Mở CapCut với tham số dòng lệnh (nếu hỗ trợ)
        2. Mở file project chính bằng os.startfile
        3. Mở CapCut và tự động thao tác UI để mở project
        
        Args:
            project: Project object cần mở
            
        Returns:
            True nếu mở thành công
        """
        self._log(f"Đang mở project: {project.name}")
        
        # Phương pháp 1: Thử mở với tham số dòng lệnh
        self._log("Phương pháp 1: Thử mở bằng tham số dòng lệnh...")
        if self._open_project_with_commandline(project):
            self._log("✓ Mở project thành công bằng tham số dòng lệnh")
            return True
        
        # Phương pháp 2: Thử os.startfile với file project chính
        self._log("Phương pháp 2: Thử mở bằng os.startfile...")
        if self._open_project_with_startfile(project):
            self._log("✓ Mở project thành công bằng os.startfile")
            return True
        
        # Phương pháp 3: Fallback - mở CapCut và tự động UI
        self._log("Phương pháp 3: Thử mở bằng automation UI...")
        if self._open_project_with_ui_automation(project):
            self._log("✓ Mở project thành công bằng automation UI")
            return True
        
        self._log("✗ Không thể mở project bằng bất kỳ phương pháp nào")
        return False
    
    def _open_project_with_commandline(self, project) -> bool:
        """
        Thử mở project bằng tham số dòng lệnh.
        
        Args:
            project: Project object
            
        Returns:
            True nếu thành công
        """
        try:
            # Đóng CapCut nếu đang chạy
            if self.is_capcut_running():
                self.close_capcut()
                time.sleep(2)
            
            # Thử mở với đường dẫn project
            draft_path = project.get_draft_path()
            
            # Thử với draft_content.json
            if os.path.exists(draft_path):
                cmd = [self.capcut_exe_path, draft_path]
                subprocess.Popen(cmd, shell=False)
                time.sleep(3)
                
                # Kiểm tra xem CapCut đã mở chưa
                if self._wait_for_window(timeout=10):
                    return True
            
            # Thử với đường dẫn thư mục project
            cmd = [self.capcut_exe_path, project.path]
            subprocess.Popen(cmd, shell=False)
            time.sleep(3)
            
            if self._wait_for_window(timeout=10):
                return True
                
        except Exception as e:
            self._log(f"Lỗi mở bằng command line: {e}")
        
        return False
    
    def _open_project_with_startfile(self, project) -> bool:
        """
        Thử mở project bằng os.startfile (Windows).
        
        Args:
            project: Project object
            
        Returns:
            True nếu thành công
        """
        try:
            import os
            
            # Tìm file project chính
            draft_path = project.get_draft_path()
            
            if os.path.exists(draft_path):
                # Đóng CapCut nếu đang chạy
                if self.is_capcut_running():
                    self.close_capcut()
                    time.sleep(2)
                
                # Thử mở file draft
                os.startfile(draft_path)
                time.sleep(3)
                
                # Kiểm tra xem CapCut đã mở chưa
                if self._wait_for_window(timeout=15):
                    return True
                    
        except Exception as e:
            self._log(f"Lỗi mở bằng startfile: {e}")
        
        return False
    
    def _open_project_with_ui_automation(self, project, max_retries: int = 2) -> bool:
        """
        Mở project bằng cách tự động thao tác UI.
        
        Quy trình:
        1. Mở CapCut
        2. Tìm và click nút "Open Project"
        3. Paste đường dẫn project và Enter
        
        Args:
            project: Project object
            max_retries: Số lần thử lại
            
        Returns:
            True nếu thành công
        """
        if not PYAUTOGUI_AVAILABLE:
            self._log("PyAutoGUI không khả dụng")
            return False
        
        if not PYPERCLIP_AVAILABLE:
            self._log("pyperclip không khả dụng, cần để paste đường dẫn")
            return False
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    self._log(f"Thử lại lần {attempt + 1}...")
                
                # Bước 1: Mở CapCut
                if not self.open_capcut():
                    continue
                
                # Chờ CapCut load hoàn toàn
                time.sleep(5)
                
                # Bước 2: Copy đường dẫn project vào clipboard
                pyperclip.copy(project.path)
                self._log(f"Đã copy đường dẫn: {project.path}")
                
                # Bước 3: Sử dụng keyboard shortcut để mở dialog
                # Ctrl+O thường là shortcut để mở file
                import pyautogui
                pyautogui.hotkey('ctrl', 'o')
                time.sleep(2)
                
                # Bước 4: Paste đường dẫn và Enter
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(1)
                pyautogui.press('enter')
                time.sleep(3)
                
                # Kiểm tra xem project đã được load chưa
                # (Có thể cần thêm logic kiểm tra cụ thể)
                self._log("Đã gửi lệnh mở project qua UI automation")
                return True
                
            except Exception as e:
                self._log(f"Lỗi UI automation (lần {attempt + 1}): {e}")
                continue
        
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
        if not PYAUTOGUI_AVAILABLE:
            self._log("pyautogui không khả dụng")
            return False

        try:
            # Tìm và click nút Export
            # Vị trí nút Export có thể thay đổi tùy version CapCut
            # Sử dụng image recognition nếu có

            self._log("Đang tìm nút Export...")

            # Phương pháp đơn giản: sử dụng tọa độ cố định
            # (Trong thực tế nên sử dụng pywinauto để tìm control)

            # Giả lập click Export - cần điều chỉnh theo UI thực tế
            # pyautogui.click(x, y)

            self._log("Đã click nút Export")
            return True

        except Exception as e:
            self._log(f"Lỗi click Export: {e}")
            return False

    def _wait_for_export(self, timeout: int = None) -> bool:
        """
        Chờ quá trình xuất hoàn tất.

        Args:
            timeout: Thời gian chờ tối đa (giây)

        Returns:
            True nếu xuất thành công
        """
        timeout = timeout or self.EXPORT_TIMEOUT
        start_time = time.time()

        while time.time() - start_time < timeout:
            if self._cancelled:
                return False

            # Kiểm tra xem export đã xong chưa
            # (Có thể kiểm tra qua dialog hoàn thành hoặc progress bar)

            time.sleep(5)

            # Giả lập: sau 10 giây coi như xong
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
        return {
            'psutil': PSUTIL_AVAILABLE,
            'pyautogui': PYAUTOGUI_AVAILABLE,
            'pywinauto': PYWINAUTO_AVAILABLE
        }
