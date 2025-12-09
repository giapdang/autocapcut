#!/usr/bin/env python3
"""
Basic Usage Example - Ví dụ sử dụng cơ bản AutoCapCut với computer vision.

Ví dụ này minh họa:
- Load config và auto-detect paths
- Load projects từ data folder
- Xuất batch projects với vision detection
"""

import sys
import os

# Thêm thư mục gốc vào path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.config import Config
from models.project import Project
from controllers.export_controller import ExportController
from services.file_service import FileService


def main():
    """Hàm main."""
    print("=" * 60)
    print("  AutoCapCut - Basic Usage Example")
    print("=" * 60)
    print()

    # 1. Load config
    print("1. Loading config...")
    config = Config.load()

    # Auto-detect paths nếu chưa có
    if not config.capcut_exe_path or not config.data_folder_path:
        print("   Auto-detecting CapCut paths...")
        if config.auto_detect_paths():
            print(f"   ✓ CapCut.exe: {config.capcut_exe_path}")
            print(f"   ✓ Data folder: {config.data_folder_path}")
            config.save()
        else:
            print("   ✗ Could not auto-detect paths")
            print("   Please configure paths manually in config/settings.json")
            return

    # 2. Load projects
    print("\n2. Loading projects...")
    file_service = FileService(config.data_folder_path)
    projects = file_service.load_projects()

    if not projects:
        print("   ✗ No projects found")
        return

    print(f"   ✓ Found {len(projects)} projects:")
    for i, project in enumerate(projects[:5], 1):  # Show first 5
        print(f"     {i}. {project.name}")
    if len(projects) > 5:
        print(f"     ... and {len(projects) - 5} more")

    # 3. Setup export controller với vision
    print("\n3. Setting up export controller...")

    def log_callback(message: str):
        """Log callback."""
        print(f"   [LOG] {message}")

    def progress_callback(current: int, total: int, name: str):
        """Progress callback."""
        print(f"   [PROGRESS] {current}/{total} - {name}")

    controller = ExportController(
        config=config,
        log_callback=log_callback,
        progress_callback=progress_callback,
        use_database=True
    )

    print("   ✓ Export controller ready")
    print(f"   ✓ Vision detection: {config.automation_settings.use_vision_detection}")
    print(f"   ✓ Database logging: enabled")

    # 4. Select projects to export (first 2 for demo)
    print("\n4. Selecting projects to export...")
    projects_to_export = projects[:2]
    print(f"   Selected {len(projects_to_export)} projects for export")

    # 5. Start export
    print("\n5. Starting export...")
    print("   Note: This is a demo - actual export requires CapCut to be configured")
    print()

    # Trong production, bỏ comment dòng dưới để thực hiện export
    # success = controller.batch_export_with_vision(projects_to_export)
    # if success:
    #     print("\n✓ Export started successfully!")
    # else:
    #     print("\n✗ Failed to start export")

    print("   (Export not started in demo mode)")

    # 6. Show statistics
    print("\n6. Export statistics:")
    stats = controller.get_export_statistics()
    print(f"   Current session:")
    print(f"     - Total: {stats['current_session']['total']}")
    print(f"     - Completed: {stats['current_session']['completed']}")
    print(f"     - Failed: {stats['current_session']['failed']}")

    if 'all_time' in stats:
        print(f"   All time:")
        print(f"     - Total exports: {stats['all_time']['total_exports']}")
        print(f"     - Success rate: {stats['all_time']['success_rate']:.1f}%")
        print(f"     - Average duration: {stats['all_time']['average_duration']:.1f}s")

    print("\n" + "=" * 60)
    print("  Demo completed!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
