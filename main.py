#!/usr/bin/env python3
"""
AutoCapCut - Công cụ tự động xuất video từ CapCut.

Ứng dụng này giúp tự động xuất nhiều project CapCut một cách tuần tự,
tiết kiệm thời gian và công sức.

Tác giả: AutoCapCut Team
Phiên bản: 1.0.0
"""

import sys
import os

# Thêm thư mục gốc vào path để import các module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from controllers.main_controller import MainController
from views.main_window import MainWindow


def main():
    """
    Hàm khởi chạy ứng dụng chính.

    Tạo controller và view, sau đó chạy main loop.
    """
    print("=" * 50)
    print("  AutoCapCut - Tự động xuất video CapCut")
    print("=" * 50)
    print()

    try:
        # Khởi tạo controller
        controller = MainController()

        # Khởi tạo view với controller
        window = MainWindow(controller)

        # Log khởi động
        window.log("AutoCapCut đã khởi động thành công!")
        window.log("Vui lòng cấu hình đường dẫn CapCut và load projects.")

        # Chạy ứng dụng
        window.run()

    except KeyboardInterrupt:
        print("\nĐã thoát ứng dụng.")
    except Exception as e:
        print(f"Lỗi khởi động ứng dụng: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
