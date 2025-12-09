#!/usr/bin/env python3
"""
Vision Debugging Example - Ví dụ debug và test computer vision features.

Ví dụ này minh họa:
- Test vision service
- Capture và manage templates
- Debug template matching
"""

import sys
import os
import time

# Thêm thư mục gốc vào path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.vision_service import VisionService
from services.template_manager import TemplateManager


def test_vision_service():
    """Test vision service."""
    print("\n" + "=" * 60)
    print("  Testing Vision Service")
    print("=" * 60)

    # Kiểm tra dependencies
    deps = VisionService.check_dependencies()
    print("\nDependencies:")
    for name, available in deps.items():
        status = "✓" if available else "✗"
        print(f"  {status} {name}: {'available' if available else 'NOT available'}")

    if not deps['opencv'] or not deps['mss']:
        print("\n⚠️  Missing required dependencies!")
        print("   Install with: pip install opencv-python mss")
        return

    # Khởi tạo vision service
    vision = VisionService(
        confidence_threshold=0.8,
        screenshot_on_error=True
    )

    # Test screenshot
    print("\n1. Testing screenshot capture...")
    screenshot = vision.capture_screenshot()
    if screenshot is not None:
        print(f"   ✓ Screenshot captured: {screenshot.shape}")

        # Save screenshot
        if vision.save_screenshot("test_screenshot.png"):
            print("   ✓ Screenshot saved to: screenshots/test_screenshot.png")
    else:
        print("   ✗ Failed to capture screenshot")

    # Test template loading
    print("\n2. Testing template loading...")
    template_manager = TemplateManager()
    templates = template_manager.list_templates()
    print(f"   Found {len(templates)} templates:")
    for template in templates[:5]:
        print(f"     - {template.name} ({template.category}/{template.version})")

    # Test template matching (if templates exist)
    if templates:
        print("\n3. Testing template matching...")
        template = templates[0]
        print(f"   Searching for: {template.name}")

        result = vision.find_image_on_screen(
            template.path,
            confidence=0.8
        )

        if result.found:
            print(f"   ✓ Template found at ({result.x}, {result.y})")
            print(f"   ✓ Confidence: {result.confidence:.2f}")
        else:
            print(f"   ✗ Template not found (confidence: {result.confidence:.2f})")

    print("\n" + "=" * 60)


def test_template_manager():
    """Test template manager."""
    print("\n" + "=" * 60)
    print("  Testing Template Manager")
    print("=" * 60)

    manager = TemplateManager()

    # List templates
    print("\n1. Listing templates...")
    templates = manager.list_templates()
    print(f"   Total templates: {len(templates)}")

    # List by category
    categories = manager.get_all_categories()
    print(f"\n2. Templates by category:")
    for category in categories:
        cat_templates = manager.list_templates(category=category)
        print(f"   - {category}: {len(cat_templates)} template(s)")

    # Validate templates
    print("\n3. Validating templates...")
    for template in templates[:3]:  # Validate first 3
        validation = manager.validate_template(
            template.name,
            template.category,
            template.version
        )
        status = "✓" if validation['valid_size'] else "✗"
        print(f"   {status} {template.name}: ", end="")
        if validation['errors']:
            print(", ".join(validation['errors']))
        else:
            print(f"{validation['width']}x{validation['height']}")

    print("\n" + "=" * 60)


def demo_capture_template():
    """Demo capture template từ màn hình."""
    print("\n" + "=" * 60)
    print("  Demo: Capture Template")
    print("=" * 60)

    print("\nNote: Để capture template trong production:")
    print("1. Mở CapCut và navigate đến button cần capture")
    print("2. Dùng tool capture hoặc code như sau:")
    print()
    print("```python")
    print("from services.template_manager import TemplateManager")
    print()
    print("manager = TemplateManager()")
    print()
    print("# Capture button tại vị trí (x, y, width, height)")
    print("success = manager.capture_template(")
    print("    name='my_button',")
    print("    region=(100, 100, 200, 50),  # Adjust coordinates")
    print("    category='buttons',")
    print("    description='Description of the button'")
    print(")")
    print("```")
    print()
    print("3. Template sẽ được lưu vào templates/buttons/")

    print("\n" + "=" * 60)


def demo_advanced_matching():
    """Demo advanced template matching."""
    print("\n" + "=" * 60)
    print("  Demo: Advanced Template Matching")
    print("=" * 60)

    vision = VisionService(confidence_threshold=0.8)
    template_manager = TemplateManager()

    templates = template_manager.list_templates()
    if not templates:
        print("\n⚠️  No templates found. Please add some templates first.")
        return

    template = templates[0]
    print(f"\nSearching for: {template.name}")

    # Wait for image với timeout
    print("\n1. Wait for image (5s timeout)...")
    start = time.time()
    result = vision.wait_for_image(
        template.path,
        timeout=5,
        check_interval=0.5
    )
    elapsed = time.time() - start

    if result.found:
        print(f"   ✓ Found in {elapsed:.1f}s at ({result.x}, {result.y})")
    else:
        print(f"   ✗ Not found after {elapsed:.1f}s")

    # Find all instances
    print("\n2. Find all instances...")
    results = vision.find_all_images_on_screen(
        template.path,
        confidence=0.7
    )
    print(f"   Found {len(results)} instance(s)")
    for i, r in enumerate(results[:3], 1):
        print(f"     {i}. Position: ({r.x}, {r.y}), Confidence: {r.confidence:.2f}")

    print("\n" + "=" * 60)


def main():
    """Hàm main."""
    print("=" * 60)
    print("  AutoCapCut - Vision Debugging Tool")
    print("=" * 60)

    while True:
        print("\nSelect an option:")
        print("  1. Test Vision Service")
        print("  2. Test Template Manager")
        print("  3. Demo: Capture Template")
        print("  4. Demo: Advanced Matching")
        print("  5. Run All Tests")
        print("  0. Exit")
        print()

        try:
            choice = input("Enter choice: ").strip()

            if choice == "1":
                test_vision_service()
            elif choice == "2":
                test_template_manager()
            elif choice == "3":
                demo_capture_template()
            elif choice == "4":
                demo_advanced_matching()
            elif choice == "5":
                test_vision_service()
                test_template_manager()
                demo_capture_template()
                demo_advanced_matching()
            elif choice == "0":
                print("\nGoodbye!")
                break
            else:
                print("\n⚠️  Invalid choice. Please try again.")

        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n✗ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
