"""
Vision Service - Service xử lý computer vision với OpenCV.

Service này cung cấp các chức năng:
- Tìm button/icon trên màn hình bằng template matching
- Đợi hình ảnh xuất hiện với timeout
- Click vào hình ảnh tìm được
- OCR đọc text từ vùng màn hình (optional với pytesseract)
"""

import os
import time
from typing import Optional, Tuple, List
from dataclasses import dataclass

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    import mss
    MSS_AVAILABLE = True
except ImportError:
    MSS_AVAILABLE = False

try:
    import pytesseract
    from PIL import Image
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False


@dataclass
class MatchResult:
    """
    Kết quả tìm kiếm hình ảnh.

    Attributes:
        found: Có tìm thấy hay không
        x: Tọa độ x của vị trí tìm thấy (tâm)
        y: Tọa độ y của vị trí tìm thấy (tâm)
        confidence: Độ tin cậy (0.0 - 1.0)
        width: Chiều rộng của template
        height: Chiều cao của template
    """
    found: bool
    x: int = 0
    y: int = 0
    confidence: float = 0.0
    width: int = 0
    height: int = 0


class VisionService:
    """
    Service xử lý computer vision với OpenCV.

    Class này cung cấp các phương thức để:
    - Tìm kiếm hình ảnh trên màn hình
    - Template matching với multi-scale
    - OCR đọc text
    - Click vào vị trí tìm được
    """

    def __init__(
        self,
        confidence_threshold: float = 0.8,
        screenshot_on_error: bool = True,
        screenshot_dir: str = "./screenshots"
    ):
        """
        Khởi tạo VisionService.

        Args:
            confidence_threshold: Ngưỡng độ tin cậy mặc định (0.0 - 1.0)
            screenshot_on_error: Có chụp screenshot khi lỗi không
            screenshot_dir: Thư mục lưu screenshots
        """
        self.confidence_threshold = confidence_threshold
        self.screenshot_on_error = screenshot_on_error
        self.screenshot_dir = screenshot_dir

        # Tạo thư mục screenshots nếu cần
        if screenshot_on_error and not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir, exist_ok=True)

        # Kiểm tra dependencies
        self._check_dependencies()

    def _check_dependencies(self) -> None:
        """Kiểm tra các thư viện phụ thuộc."""
        if not CV2_AVAILABLE:
            print("Warning: opencv-python không khả dụng")
        if not MSS_AVAILABLE:
            print("Warning: mss không khả dụng")
        if not PYTESSERACT_AVAILABLE:
            print("Warning: pytesseract không khả dụng (OCR sẽ không hoạt động)")
        if not PYAUTOGUI_AVAILABLE:
            print("Warning: pyautogui không khả dụng")

    def capture_screenshot(self, region: Optional[Tuple[int, int, int, int]] = None) -> Optional[np.ndarray]:
        """
        Chụp màn hình bằng mss (nhanh hơn PIL).

        Args:
            region: Vùng chụp (x, y, width, height). None = toàn màn hình

        Returns:
            Numpy array của ảnh (BGR format) hoặc None nếu thất bại
        """
        if not MSS_AVAILABLE or not CV2_AVAILABLE:
            return None

        try:
            with mss.mss() as sct:
                if region:
                    x, y, width, height = region
                    monitor = {
                        "top": y,
                        "left": x,
                        "width": width,
                        "height": height
                    }
                else:
                    monitor = sct.monitors[1]  # Primary monitor

                # Chụp màn hình
                screenshot = sct.grab(monitor)

                # Chuyển đổi sang numpy array (BGRA -> BGR)
                img = np.array(screenshot)
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

                return img
        except Exception as e:
            print(f"Lỗi chụp màn hình: {e}")
            return None

    def save_screenshot(self, filename: str, region: Optional[Tuple[int, int, int, int]] = None) -> bool:
        """
        Chụp và lưu screenshot.

        Args:
            filename: Tên file lưu (sẽ được lưu trong screenshot_dir)
            region: Vùng chụp (x, y, width, height)

        Returns:
            True nếu thành công
        """
        img = self.capture_screenshot(region)
        if img is None:
            return False

        try:
            filepath = os.path.join(self.screenshot_dir, filename)
            cv2.imwrite(filepath, img)
            return True
        except Exception as e:
            print(f"Lỗi lưu screenshot: {e}")
            return False

    def load_template(self, template_path: str) -> Optional[np.ndarray]:
        """
        Load template image từ file.

        Args:
            template_path: Đường dẫn đến file template

        Returns:
            Numpy array của template hoặc None nếu thất bại
        """
        if not CV2_AVAILABLE:
            return None

        if not os.path.exists(template_path):
            print(f"Template không tồn tại: {template_path}")
            return None

        try:
            template = cv2.imread(template_path)
            if template is None:
                print(f"Không thể load template: {template_path}")
                return None
            return template
        except Exception as e:
            print(f"Lỗi load template: {e}")
            return None

    def find_image_on_screen(
        self,
        template_path: str,
        confidence: Optional[float] = None,
        region: Optional[Tuple[int, int, int, int]] = None,
        grayscale: bool = True
    ) -> MatchResult:
        """
        Tìm hình ảnh trên màn hình bằng template matching.

        Args:
            template_path: Đường dẫn đến template image
            confidence: Ngưỡng độ tin cậy (None = dùng mặc định)
            region: Vùng tìm kiếm (x, y, width, height)
            grayscale: Có chuyển sang grayscale không (nhanh hơn)

        Returns:
            MatchResult với thông tin tìm kiếm
        """
        if not CV2_AVAILABLE:
            return MatchResult(found=False)

        confidence = confidence or self.confidence_threshold

        # Load template
        template = self.load_template(template_path)
        if template is None:
            return MatchResult(found=False)

        # Chụp màn hình
        screenshot = self.capture_screenshot(region)
        if screenshot is None:
            return MatchResult(found=False)

        try:
            # Chuyển sang grayscale nếu cần
            if grayscale:
                template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
                screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            else:
                template_gray = template
                screenshot_gray = screenshot

            # Template matching
            result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            # Kiểm tra confidence
            if max_val >= confidence:
                h, w = template_gray.shape[:2]
                # Tọa độ tâm
                center_x = max_loc[0] + w // 2
                center_y = max_loc[1] + h // 2

                # Nếu có region offset, cộng thêm
                if region:
                    center_x += region[0]
                    center_y += region[1]

                return MatchResult(
                    found=True,
                    x=center_x,
                    y=center_y,
                    confidence=max_val,
                    width=w,
                    height=h
                )
            else:
                return MatchResult(found=False, confidence=max_val)

        except Exception as e:
            print(f"Lỗi tìm kiếm hình ảnh: {e}")
            if self.screenshot_on_error:
                self.save_screenshot(f"error_{int(time.time())}.png")
            return MatchResult(found=False)

    def find_all_images_on_screen(
        self,
        template_path: str,
        confidence: Optional[float] = None,
        region: Optional[Tuple[int, int, int, int]] = None
    ) -> List[MatchResult]:
        """
        Tìm tất cả vị trí của hình ảnh trên màn hình.

        Args:
            template_path: Đường dẫn đến template image
            confidence: Ngưỡng độ tin cậy
            region: Vùng tìm kiếm

        Returns:
            Danh sách MatchResult
        """
        if not CV2_AVAILABLE:
            return []

        confidence = confidence or self.confidence_threshold
        template = self.load_template(template_path)
        if template is None:
            return []

        screenshot = self.capture_screenshot(region)
        if screenshot is None:
            return []

        try:
            template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

            result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
            h, w = template_gray.shape[:2]

            # Tìm tất cả vị trí có confidence >= threshold
            locations = np.where(result >= confidence)
            matches = []

            for pt in zip(*locations[::-1]):
                center_x = pt[0] + w // 2
                center_y = pt[1] + h // 2

                if region:
                    center_x += region[0]
                    center_y += region[1]

                matches.append(MatchResult(
                    found=True,
                    x=center_x,
                    y=center_y,
                    confidence=result[pt[1], pt[0]],
                    width=w,
                    height=h
                ))

            return matches

        except Exception as e:
            print(f"Lỗi tìm kiếm tất cả hình ảnh: {e}")
            return []

    def wait_for_image(
        self,
        template_path: str,
        timeout: float = 30,
        check_interval: float = 0.5,
        confidence: Optional[float] = None
    ) -> MatchResult:
        """
        Đợi hình ảnh xuất hiện trên màn hình.

        Args:
            template_path: Đường dẫn đến template image
            timeout: Thời gian chờ tối đa (giây)
            check_interval: Thời gian giữa các lần kiểm tra (giây)
            confidence: Ngưỡng độ tin cậy

        Returns:
            MatchResult nếu tìm thấy trong timeout
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            result = self.find_image_on_screen(template_path, confidence)
            if result.found:
                return result

            time.sleep(check_interval)

        # Timeout - chụp screenshot để debug
        if self.screenshot_on_error:
            self.save_screenshot(f"timeout_{os.path.basename(template_path)}_{int(time.time())}.png")

        return MatchResult(found=False)

    def click_on_image(
        self,
        template_path: str,
        confidence: Optional[float] = None,
        timeout: float = 10,
        click_offset: Tuple[int, int] = (0, 0)
    ) -> bool:
        """
        Tìm và click vào hình ảnh.

        Args:
            template_path: Đường dẫn đến template image
            confidence: Ngưỡng độ tin cậy
            timeout: Thời gian chờ tìm image (giây)
            click_offset: Offset (dx, dy) từ tâm để click

        Returns:
            True nếu click thành công
        """
        if not PYAUTOGUI_AVAILABLE:
            print("pyautogui không khả dụng")
            return False

        # Tìm hình ảnh
        result = self.wait_for_image(template_path, timeout, confidence=confidence)

        if not result.found:
            print(f"Không tìm thấy hình ảnh: {template_path}")
            return False

        try:
            # Click vào vị trí tìm được (với offset nếu có)
            click_x = result.x + click_offset[0]
            click_y = result.y + click_offset[1]

            pyautogui.click(click_x, click_y)
            print(f"Đã click vào ({click_x}, {click_y}) - confidence: {result.confidence:.2f}")
            return True

        except Exception as e:
            print(f"Lỗi click: {e}")
            if self.screenshot_on_error:
                self.save_screenshot(f"click_error_{int(time.time())}.png")
            return False

    def read_text_region(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        lang: str = 'eng'
    ) -> Optional[str]:
        """
        Đọc text từ vùng màn hình bằng OCR (pytesseract).

        Args:
            x: Tọa độ x
            y: Tọa độ y
            width: Chiều rộng vùng
            height: Chiều cao vùng
            lang: Ngôn ngữ OCR (eng, vie, etc.)

        Returns:
            Text đọc được hoặc None nếu thất bại
        """
        if not PYTESSERACT_AVAILABLE:
            print("pytesseract không khả dụng")
            return None

        # Chụp vùng màn hình
        screenshot = self.capture_screenshot((x, y, width, height))
        if screenshot is None:
            return None

        try:
            # Chuyển sang PIL Image để OCR
            img_rgb = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(img_rgb)

            # OCR
            text = pytesseract.image_to_string(pil_img, lang=lang)
            return text.strip()

        except Exception as e:
            print(f"Lỗi OCR: {e}")
            return None

    def wait_for_text(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        expected_text: str,
        timeout: float = 30,
        check_interval: float = 1.0,
        partial_match: bool = True
    ) -> bool:
        """
        Đợi text xuất hiện trong vùng màn hình.

        Args:
            x: Tọa độ x
            y: Tọa độ y
            width: Chiều rộng vùng
            height: Chiều cao vùng
            expected_text: Text cần đợi
            timeout: Thời gian chờ tối đa (giây)
            check_interval: Thời gian giữa các lần kiểm tra (giây)
            partial_match: Cho phép khớp một phần text

        Returns:
            True nếu tìm thấy text trong timeout
        """
        if not PYTESSERACT_AVAILABLE:
            return False

        start_time = time.time()

        while time.time() - start_time < timeout:
            text = self.read_text_region(x, y, width, height)

            if text:
                if partial_match:
                    if expected_text.lower() in text.lower():
                        return True
                else:
                    if expected_text.lower() == text.lower():
                        return True

            time.sleep(check_interval)

        return False

    @staticmethod
    def check_dependencies() -> dict:
        """
        Kiểm tra các thư viện phụ thuộc.

        Returns:
            Dictionary với trạng thái các thư viện
        """
        return {
            'opencv': CV2_AVAILABLE,
            'mss': MSS_AVAILABLE,
            'pytesseract': PYTESSERACT_AVAILABLE,
            'pyautogui': PYAUTOGUI_AVAILABLE
        }
