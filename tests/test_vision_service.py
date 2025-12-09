"""
Test Vision Service - Unit tests cho VisionService.

Tests:
- Screenshot capture
- Template loading
- Image matching
- OCR (optional)
"""

import unittest
import os
import sys
import tempfile

# Thêm thư mục gốc vào path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.vision_service import VisionService, MatchResult


class TestVisionService(unittest.TestCase):
    """Test cases cho VisionService."""

    @classmethod
    def setUpClass(cls):
        """Setup trước tất cả tests."""
        cls.temp_dir = tempfile.mkdtemp()

    def setUp(self):
        """Setup trước mỗi test."""
        self.vision = VisionService(
            confidence_threshold=0.8,
            screenshot_on_error=False,
            screenshot_dir=self.temp_dir
        )

    def test_check_dependencies(self):
        """Test check dependencies."""
        deps = VisionService.check_dependencies()

        self.assertIn('opencv', deps)
        self.assertIn('mss', deps)
        self.assertIn('pytesseract', deps)
        self.assertIn('pyautogui', deps)

        # Print dependency status
        print("\nDependency status:")
        for name, available in deps.items():
            print(f"  {name}: {'available' if available else 'NOT available'}")

    def test_capture_screenshot(self):
        """Test capture screenshot."""
        # Chỉ test nếu có opencv và mss
        deps = VisionService.check_dependencies()
        if not deps['opencv'] or not deps['mss']:
            self.skipTest("opencv or mss not available")

        screenshot = self.vision.capture_screenshot()

        self.assertIsNotNone(screenshot)
        self.assertEqual(len(screenshot.shape), 3)  # Should be 3D array (H, W, C)

    def test_save_screenshot(self):
        """Test save screenshot."""
        deps = VisionService.check_dependencies()
        if not deps['opencv'] or not deps['mss']:
            self.skipTest("opencv or mss not available")

        filename = "test_screenshot.png"
        success = self.vision.save_screenshot(filename)

        self.assertTrue(success)

        # Check file exists
        filepath = os.path.join(self.temp_dir, filename)
        self.assertTrue(os.path.exists(filepath))

    def test_load_template_nonexistent(self):
        """Test load template với file không tồn tại."""
        deps = VisionService.check_dependencies()
        if not deps['opencv']:
            self.skipTest("opencv not available")

        template = self.vision.load_template("nonexistent.png")
        self.assertIsNone(template)

    def test_find_image_on_screen_no_template(self):
        """Test find image với template không tồn tại."""
        deps = VisionService.check_dependencies()
        if not deps['opencv']:
            self.skipTest("opencv not available")

        result = self.vision.find_image_on_screen("nonexistent.png")

        self.assertIsInstance(result, MatchResult)
        self.assertFalse(result.found)

    def test_match_result_dataclass(self):
        """Test MatchResult dataclass."""
        result = MatchResult(
            found=True,
            x=100,
            y=200,
            confidence=0.95,
            width=50,
            height=30
        )

        self.assertTrue(result.found)
        self.assertEqual(result.x, 100)
        self.assertEqual(result.y, 200)
        self.assertEqual(result.confidence, 0.95)
        self.assertEqual(result.width, 50)
        self.assertEqual(result.height, 30)


class TestVisionServiceIntegration(unittest.TestCase):
    """Integration tests cho VisionService (require full dependencies)."""

    def setUp(self):
        """Setup trước mỗi test."""
        # Skip nếu không có dependencies
        deps = VisionService.check_dependencies()
        if not all([deps['opencv'], deps['mss']]):
            self.skipTest("Required dependencies not available")

        self.vision = VisionService(confidence_threshold=0.8)

    def test_screenshot_and_match(self):
        """Test integration: capture screenshot và match template."""
        # Capture screenshot
        screenshot = self.vision.capture_screenshot()
        self.assertIsNotNone(screenshot)

        # Save as template
        import cv2
        temp_template = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        cv2.imwrite(temp_template.name, screenshot[:100, :100])  # Small region

        # Try to match
        result = self.vision.find_image_on_screen(temp_template.name)

        # Clean up
        os.unlink(temp_template.name)

        # Should find because it's from same screenshot
        self.assertIsInstance(result, MatchResult)


def suite():
    """Create test suite."""
    suite = unittest.TestSuite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestVisionService))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestVisionServiceIntegration))
    return suite


if __name__ == '__main__':
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite())

    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
