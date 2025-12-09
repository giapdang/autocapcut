"""
Error Handler - Xử lý lỗi thông minh với screenshots và retry logic.

Module này cung cấp:
- Screenshot tự động khi có lỗi
- Auto-retry với fallback strategies
- Logging chi tiết với stack trace
- Notification khi cần can thiệp thủ công
"""

import os
import traceback
import logging
from typing import Optional, Callable, Any, Dict
from datetime import datetime
from enum import Enum
from dataclasses import dataclass


class ErrorSeverity(Enum):
    """Mức độ nghiêm trọng của lỗi."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ErrorInfo:
    """
    Thông tin về lỗi.

    Attributes:
        timestamp: Thời gian xảy ra lỗi
        severity: Mức độ nghiêm trọng
        message: Thông điệp lỗi
        exception: Exception object
        stack_trace: Stack trace
        screenshot_path: Đường dẫn screenshot (nếu có)
        context: Context bổ sung
    """
    timestamp: datetime
    severity: ErrorSeverity
    message: str
    exception: Optional[Exception] = None
    stack_trace: Optional[str] = None
    screenshot_path: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Initialize mutable defaults."""
        if self.context is None:
            self.context = {}

    def to_dict(self) -> Dict[str, Any]:
        """Chuyển đổi thành dictionary."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'severity': self.severity.value,
            'message': self.message,
            'exception': str(self.exception) if self.exception else None,
            'stack_trace': self.stack_trace,
            'screenshot_path': self.screenshot_path,
            'context': self.context
        }


class ErrorHandler:
    """
    Xử lý lỗi thông minh với screenshots và retry.

    Class này cung cấp:
    - Capture screenshots khi có lỗi
    - Retry tự động với exponential backoff
    - Logging chi tiết
    - Notification cho user
    """

    def __init__(
        self,
        screenshot_on_error: bool = True,
        screenshot_dir: str = "./screenshots/errors",
        log_dir: str = "./logs",
        notification_callback: Optional[Callable[[ErrorInfo], None]] = None
    ):
        """
        Khởi tạo ErrorHandler.

        Args:
            screenshot_on_error: Có chụp screenshot khi lỗi không
            screenshot_dir: Thư mục lưu screenshots
            log_dir: Thư mục lưu logs
            notification_callback: Callback để thông báo lỗi
        """
        self.screenshot_on_error = screenshot_on_error
        self.screenshot_dir = screenshot_dir
        self.log_dir = log_dir
        self.notification_callback = notification_callback

        # Tạo thư mục nếu chưa tồn tại
        if screenshot_on_error:
            os.makedirs(screenshot_dir, exist_ok=True)

        if log_dir:
            os.makedirs(log_dir, exist_ok=True)

        # Setup logging
        self._setup_logging()

        # Statistics
        self.error_count = 0
        self.errors_by_severity = {
            ErrorSeverity.INFO: 0,
            ErrorSeverity.WARNING: 0,
            ErrorSeverity.ERROR: 0,
            ErrorSeverity.CRITICAL: 0
        }

    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        log_file = os.path.join(self.log_dir, 'errors.log')

        # Create logger
        self.logger = logging.getLogger('ErrorHandler')
        self.logger.setLevel(logging.DEBUG)

        # File handler
        fh = logging.FileHandler(log_file, encoding='utf-8')
        fh.setLevel(logging.DEBUG)

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.WARNING)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # Add handlers
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def handle_error(
        self,
        exception: Exception,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        context: Optional[Dict[str, Any]] = None,
        take_screenshot: bool = True
    ) -> ErrorInfo:
        """
        Xử lý lỗi.

        Args:
            exception: Exception object
            message: Thông điệp lỗi
            severity: Mức độ nghiêm trọng
            context: Context bổ sung
            take_screenshot: Có chụp screenshot không

        Returns:
            ErrorInfo object
        """
        self.error_count += 1
        self.errors_by_severity[severity] += 1

        # Lấy stack trace
        stack_trace = traceback.format_exc()

        # Chụp screenshot nếu cần
        screenshot_path = None
        if take_screenshot and self.screenshot_on_error:
            screenshot_path = self._take_error_screenshot()

        # Tạo ErrorInfo
        error_info = ErrorInfo(
            timestamp=datetime.now(),
            severity=severity,
            message=message,
            exception=exception,
            stack_trace=stack_trace,
            screenshot_path=screenshot_path,
            context=context
        )

        # Log lỗi
        self._log_error(error_info)

        # Thông báo nếu có callback
        if self.notification_callback:
            try:
                self.notification_callback(error_info)
            except Exception as e:
                self.logger.error(f"Lỗi gọi notification callback: {e}")

        return error_info

    def _take_error_screenshot(self) -> Optional[str]:
        """
        Chụp screenshot khi có lỗi.

        Returns:
            Đường dẫn đến file screenshot
        """
        try:
            # Import vision service để chụp màn hình
            from services.vision_service import VisionService

            vision = VisionService(screenshot_dir=self.screenshot_dir)

            # Tạo tên file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"error_{timestamp}_{self.error_count}.png"

            # Chụp màn hình
            if vision.save_screenshot(filename):
                screenshot_path = os.path.join(self.screenshot_dir, filename)
                self.logger.info(f"Đã chụp screenshot: {screenshot_path}")
                return screenshot_path

        except Exception as e:
            self.logger.error(f"Lỗi chụp screenshot: {e}")

        return None

    def _log_error(self, error_info: ErrorInfo) -> None:
        """
        Ghi log lỗi.

        Args:
            error_info: Thông tin lỗi
        """
        # Chọn log level dựa trên severity
        log_level = {
            ErrorSeverity.INFO: logging.INFO,
            ErrorSeverity.WARNING: logging.WARNING,
            ErrorSeverity.ERROR: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL
        }.get(error_info.severity, logging.ERROR)

        # Log message
        log_message = f"{error_info.message}"
        if error_info.exception:
            log_message += f" - Exception: {error_info.exception}"
        if error_info.context:
            log_message += f" - Context: {error_info.context}"
        if error_info.screenshot_path:
            log_message += f" - Screenshot: {error_info.screenshot_path}"

        self.logger.log(log_level, log_message)

        # Log stack trace nếu có
        if error_info.stack_trace:
            self.logger.debug(f"Stack trace:\n{error_info.stack_trace}")

    def retry_with_backoff(
        self,
        func: Callable,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        backoff_factor: float = 2.0,
        exceptions: tuple = (Exception,),
        on_retry: Optional[Callable[[int, Exception], None]] = None
    ) -> Any:
        """
        Thử lại function với exponential backoff.

        Args:
            func: Function cần thực thi
            max_attempts: Số lần thử tối đa
            initial_delay: Thời gian chờ ban đầu (giây)
            backoff_factor: Hệ số nhân cho mỗi lần retry
            exceptions: Tuple các exception cần retry
            on_retry: Callback khi retry (attempt_number, exception)

        Returns:
            Kết quả của function

        Raises:
            Exception cuối cùng nếu thất bại tất cả các lần thử
        """
        import time

        last_exception = None
        delay = initial_delay

        for attempt in range(1, max_attempts + 1):
            try:
                return func()

            except exceptions as e:
                last_exception = e

                # Log retry
                self.logger.warning(
                    f"Attempt {attempt}/{max_attempts} failed: {e}. "
                    f"Retrying in {delay}s..."
                )

                # Callback nếu có
                if on_retry:
                    try:
                        on_retry(attempt, e)
                    except Exception as callback_error:
                        self.logger.error(f"Lỗi on_retry callback: {callback_error}")

                # Chờ trước khi retry (trừ lần cuối)
                if attempt < max_attempts:
                    time.sleep(delay)
                    delay *= backoff_factor

        # Tất cả các lần thử đều thất bại
        self.handle_error(
            last_exception,
            f"Function thất bại sau {max_attempts} lần thử",
            severity=ErrorSeverity.ERROR,
            context={'function': func.__name__ if hasattr(func, '__name__') else str(func)}
        )

        raise last_exception

    def get_statistics(self) -> Dict[str, Any]:
        """
        Lấy thống kê lỗi.

        Returns:
            Dictionary chứa thống kê
        """
        return {
            'total_errors': self.error_count,
            'by_severity': {
                severity.value: count
                for severity, count in self.errors_by_severity.items()
            }
        }

    def reset_statistics(self) -> None:
        """Reset thống kê lỗi."""
        self.error_count = 0
        for severity in ErrorSeverity:
            self.errors_by_severity[severity] = 0


# Singleton instance
_error_handler_instance: Optional[ErrorHandler] = None


def get_error_handler() -> ErrorHandler:
    """
    Lấy singleton instance của ErrorHandler.

    Returns:
        ErrorHandler instance
    """
    global _error_handler_instance
    if _error_handler_instance is None:
        _error_handler_instance = ErrorHandler()
    return _error_handler_instance


def handle_error(
    exception: Exception,
    message: str,
    severity: ErrorSeverity = ErrorSeverity.ERROR,
    context: Optional[Dict[str, Any]] = None
) -> ErrorInfo:
    """
    Shortcut function để xử lý lỗi.

    Args:
        exception: Exception object
        message: Thông điệp lỗi
        severity: Mức độ nghiêm trọng
        context: Context bổ sung

    Returns:
        ErrorInfo object
    """
    handler = get_error_handler()
    return handler.handle_error(exception, message, severity, context)
