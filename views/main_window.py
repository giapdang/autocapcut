"""
Main Window - Cửa sổ chính của ứng dụng AutoCapCut.

Module này chứa giao diện chính với:
- Header: Tiêu đề và logo
- Phần cấu hình: Input đường dẫn CapCut
- Danh sách Projects
- Phần điều khiển: Export, progress
- Log area
"""

from typing import List

try:
    import customtkinter as ctk
    CTK_AVAILABLE = True
except ImportError:
    CTK_AVAILABLE = False
    import tkinter as tk
    from tkinter import ttk, messagebox

from models.project import Project
from views.components import (
    ProjectItem, LogWidget, ProgressWidget, PathInputWidget
)


if CTK_AVAILABLE:
    # Cấu hình CustomTkinter
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")


    class MainWindow(ctk.CTk):
        """
        Cửa sổ chính của ứng dụng AutoCapCut.

        Giao diện hiện đại sử dụng CustomTkinter với:
        - Header với tiêu đề
        - Cấu hình đường dẫn CapCut
        - Danh sách projects có thể chọn
        - Progress bar và log area
        """

        # Kích thước cửa sổ
        WINDOW_WIDTH = 900
        WINDOW_HEIGHT = 700

        def __init__(self, controller=None):
            """
            Khởi tạo MainWindow.

            Args:
                controller: MainController instance
            """
            super().__init__()

            self.controller = controller
            self._project_items: List[ProjectItem] = []

            self._setup_window()
            self._setup_ui()

            # Kết nối với controller
            if self.controller:
                self.controller.set_view(self)

        def _setup_window(self) -> None:
            """Thiết lập cửa sổ."""
            self.title("AutoCapCut - Tự động xuất video CapCut")
            self.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
            self.minsize(800, 600)

            # Center window
            self.update_idletasks()
            x = (self.winfo_screenwidth() - self.WINDOW_WIDTH) // 2
            y = (self.winfo_screenheight() - self.WINDOW_HEIGHT) // 2
            self.geometry(f"+{x}+{y}")

            # Configure grid weights
            self.grid_columnconfigure(0, weight=1)
            self.grid_rowconfigure(2, weight=1)

        def _setup_ui(self) -> None:
            """Thiết lập giao diện."""
            self._create_header()
            self._create_config_section()
            self._create_project_list_section()
            self._create_control_section()
            self._create_log_section()

        def _create_header(self) -> None:
            """Tạo header với tiêu đề."""
            self.header_frame = ctk.CTkFrame(self, height=60)
            self.header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
            self.header_frame.grid_columnconfigure(0, weight=1)

            # Logo/Title
            self.title_label = ctk.CTkLabel(
                self.header_frame,
                text="🎬 AutoCapCut",
                font=ctk.CTkFont(size=24, weight="bold")
            )
            self.title_label.grid(row=0, column=0, sticky="w", padx=20, pady=10)

            # Subtitle
            self.subtitle_label = ctk.CTkLabel(
                self.header_frame,
                text="Công cụ tự động xuất video từ CapCut",
                font=ctk.CTkFont(size=12),
                text_color="gray"
            )
            self.subtitle_label.grid(row=0, column=1, sticky="e", padx=20, pady=10)

        def _create_config_section(self) -> None:
            """Tạo phần cấu hình."""
            self.config_frame = ctk.CTkFrame(self)
            self.config_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
            self.config_frame.grid_columnconfigure(0, weight=1)

            # CapCut.exe path
            self.capcut_path_input = PathInputWidget(
                self.config_frame,
                label_text="CapCut.exe:",
                placeholder="Chọn đường dẫn đến CapCut.exe",
                browse_type="file",
                on_change=self._on_capcut_path_change
            )
            self.capcut_path_input.grid(row=0, column=0, sticky="ew", pady=(5, 2))

            # Data folder path
            data_frame = ctk.CTkFrame(self.config_frame, fg_color="transparent")
            data_frame.grid(row=1, column=0, sticky="ew", pady=(2, 5))
            data_frame.grid_columnconfigure(1, weight=1)

            self.data_path_input = PathInputWidget(
                data_frame,
                label_text="Thư mục data:",
                placeholder="Chọn thư mục data CapCut",
                browse_type="folder",
                on_change=self._on_data_path_change
            )
            self.data_path_input.grid(row=0, column=0, columnspan=2, sticky="ew")

            # Auto-detect button
            self.auto_detect_btn = ctk.CTkButton(
                data_frame,
                text="Auto-detect",
                width=100,
                command=self._on_auto_detect
            )
            self.auto_detect_btn.grid(row=0, column=2, padx=(5, 10), pady=5)

            # Load Projects button
            self.load_btn = ctk.CTkButton(
                self.config_frame,
                text="📂 Load Projects",
                font=ctk.CTkFont(size=14, weight="bold"),
                height=36,
                command=self._on_load_projects
            )
            self.load_btn.grid(row=2, column=0, pady=10)

        def _create_project_list_section(self) -> None:
            """Tạo phần danh sách projects."""
            self.project_frame = ctk.CTkFrame(self)
            self.project_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
            self.project_frame.grid_columnconfigure(0, weight=1)
            self.project_frame.grid_rowconfigure(1, weight=1)

            # Header với buttons
            header = ctk.CTkFrame(self.project_frame, fg_color="transparent")
            header.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
            header.grid_columnconfigure(0, weight=1)

            # Label hiển thị số lượng project và ghi chú về lọc
            self.project_count_label = ctk.CTkLabel(
                header,
                text="Projects hiện tại (0) - không bao gồm thùng rác và cloud",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            self.project_count_label.grid(row=0, column=0, sticky="w")

            # Select All / Deselect All buttons
            btn_frame = ctk.CTkFrame(header, fg_color="transparent")
            btn_frame.grid(row=0, column=1, sticky="e")

            self.select_all_btn = ctk.CTkButton(
                btn_frame,
                text="Chọn tất cả",
                width=100,
                command=self._on_select_all
            )
            self.select_all_btn.pack(side="left", padx=2)

            self.deselect_all_btn = ctk.CTkButton(
                btn_frame,
                text="Bỏ chọn",
                width=100,
                command=self._on_deselect_all
            )
            self.deselect_all_btn.pack(side="left", padx=2)

            # Scrollable frame cho danh sách projects
            self.project_scroll = ctk.CTkScrollableFrame(
                self.project_frame,
                label_text=""
            )
            self.project_scroll.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
            self.project_scroll.grid_columnconfigure(0, weight=1)

        def _create_control_section(self) -> None:
            """Tạo phần điều khiển."""
            self.control_frame = ctk.CTkFrame(self)
            self.control_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=5)
            self.control_frame.grid_columnconfigure(0, weight=1)

            # Export button
            btn_frame = ctk.CTkFrame(self.control_frame, fg_color="transparent")
            btn_frame.grid(row=0, column=0, pady=5)

            self.export_btn = ctk.CTkButton(
                btn_frame,
                text="🚀 Export Selected",
                font=ctk.CTkFont(size=16, weight="bold"),
                width=200,
                height=40,
                fg_color="green",
                hover_color="darkgreen",
                command=self._on_export
            )
            self.export_btn.pack(side="left", padx=5)

            self.cancel_btn = ctk.CTkButton(
                btn_frame,
                text="❌ Cancel",
                font=ctk.CTkFont(size=14),
                width=100,
                height=40,
                fg_color="red",
                hover_color="darkred",
                command=self._on_cancel,
                state="disabled"
            )
            self.cancel_btn.pack(side="left", padx=5)

            # Progress widget
            self.progress_widget = ProgressWidget(self.control_frame)
            self.progress_widget.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

        def _create_log_section(self) -> None:
            """Tạo phần log."""
            self.log_frame = ctk.CTkFrame(self)
            self.log_frame.grid(row=4, column=0, sticky="ew", padx=10, pady=(5, 10))
            self.log_frame.grid_columnconfigure(0, weight=1)

            # Log header
            log_header = ctk.CTkFrame(self.log_frame, fg_color="transparent")
            log_header.grid(row=0, column=0, sticky="ew", padx=10, pady=5)

            ctk.CTkLabel(
                log_header,
                text="📋 Log",
                font=ctk.CTkFont(size=12, weight="bold")
            ).pack(side="left")

            ctk.CTkButton(
                log_header,
                text="Clear",
                width=60,
                height=24,
                command=self._on_clear_log
            ).pack(side="right")

            # Log widget
            self.log_widget = LogWidget(self.log_frame, height=120)
            self.log_widget.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 5))

        # ==================== Event Handlers ====================

        def _on_capcut_path_change(self, path: str) -> None:
            """Xử lý khi đường dẫn CapCut thay đổi."""
            if self.controller:
                self.controller.set_capcut_path(path)

        def _on_data_path_change(self, path: str) -> None:
            """Xử lý khi đường dẫn data thay đổi."""
            if self.controller:
                self.controller.set_data_path(path)

        def _on_auto_detect(self) -> None:
            """Xử lý khi click Auto-detect."""
            self.log("Đang tự động phát hiện đường dẫn CapCut...")
            if self.controller:
                result = self.controller.auto_detect_paths()
                if not result['capcut_exe'] and not result['data_folder']:
                    self.show_warning(
                        "Không tìm thấy CapCut!\n"
                        "Vui lòng chọn đường dẫn thủ công."
                    )

        def _on_load_projects(self) -> None:
            """Xử lý khi click Load Projects."""
            if self.controller:
                self.controller.load_projects()

        def _on_select_all(self) -> None:
            """Xử lý khi click Select All."""
            self.select_all_projects()

        def _on_deselect_all(self) -> None:
            """Xử lý khi click Deselect All."""
            self.deselect_all_projects()

        def _on_export(self) -> None:
            """Xử lý khi click Export."""
            # Lấy danh sách đã chọn
            selected = self._get_selected_projects()

            if not selected:
                self.show_warning("Vui lòng chọn ít nhất một project để xuất")
                return

            if self.controller:
                self.controller.set_selected_projects(selected)
                self.controller.start_export()

        def _on_cancel(self) -> None:
            """Xử lý khi click Cancel."""
            if self.controller:
                self.controller.cancel_export()

        def _on_clear_log(self) -> None:
            """Xử lý khi click Clear Log."""
            self.log_widget.clear()

        def _on_project_select(self, project: Project, selected: bool) -> None:
            """Xử lý khi chọn/bỏ chọn project."""
            if self.controller:
                self.controller.select_project(project, selected)

        # ==================== Public Methods ====================

        def log(self, message: str) -> None:
            """
            Thêm message vào log.

            Args:
                message: Nội dung log
            """
            # Đảm bảo chạy trên main thread
            self.after(0, lambda: self.log_widget.log(message))

        def update_project_list(self, projects: List[Project]) -> None:
            """
            Cập nhật danh sách projects.

            Args:
                projects: Danh sách Project objects
            """
            # Xóa các items cũ
            for item in self._project_items:
                item.destroy()
            self._project_items.clear()

            # Tạo items mới
            for i, project in enumerate(projects):
                item = ProjectItem(
                    self.project_scroll,
                    project=project,
                    on_select=self._on_project_select
                )
                item.grid(row=i, column=0, sticky="ew", padx=5, pady=2)
                self._project_items.append(item)

            # Cập nhật count label
            count = len(projects)
            label_text = f"Projects hiện tại ({count}) - không bao gồm thùng rác và cloud"
            self.project_count_label.configure(text=label_text)

        def select_all_projects(self) -> None:
            """Chọn tất cả projects."""
            for item in self._project_items:
                item.set_selected(True)

        def deselect_all_projects(self) -> None:
            """Bỏ chọn tất cả projects."""
            for item in self._project_items:
                item.set_selected(False)

        def _get_selected_projects(self) -> List[Project]:
            """
            Lấy danh sách projects đã chọn.

            Returns:
                Danh sách Project đã chọn
            """
            return [
                item.project for item in self._project_items
                if item.is_selected()
            ]

        def set_capcut_path(self, path: str) -> None:
            """
            Đặt đường dẫn CapCut.

            Args:
                path: Đường dẫn CapCut.exe
            """
            self.capcut_path_input.set_value(path)

        def set_data_path(self, path: str) -> None:
            """
            Đặt đường dẫn data.

            Args:
                path: Đường dẫn thư mục data
            """
            self.data_path_input.set_value(path)

        def update_progress(self, current: int, total: int, project_name: str = "") -> None:
            """
            Cập nhật tiến trình.

            Args:
                current: Số lượng hiện tại
                total: Tổng số
                project_name: Tên project đang xuất
            """
            status = f"Đang xuất: {project_name}" if project_name else ""
            self.after(0, lambda: self.progress_widget.update_progress(current, total, status))

        def update_status(self, status: str) -> None:
            """
            Cập nhật trạng thái.

            Args:
                status: Nội dung trạng thái
            """
            self.after(0, lambda: self.progress_widget.set_status(status))

        def set_exporting_state(self, exporting: bool) -> None:
            """
            Đặt trạng thái đang xuất.

            Args:
                exporting: True nếu đang xuất
            """
            if exporting:
                self.export_btn.configure(state="disabled")
                self.cancel_btn.configure(state="normal")
                self.load_btn.configure(state="disabled")
            else:
                self.export_btn.configure(state="normal")
                self.cancel_btn.configure(state="disabled")
                self.load_btn.configure(state="normal")
                self.progress_widget.reset()

        def show_info(self, message: str) -> None:
            """Hiển thị thông báo info."""
            from tkinter import messagebox
            messagebox.showinfo("Thông báo", message)

        def show_warning(self, message: str) -> None:
            """Hiển thị cảnh báo."""
            from tkinter import messagebox
            messagebox.showwarning("Cảnh báo", message)

        def show_error(self, message: str) -> None:
            """Hiển thị lỗi."""
            from tkinter import messagebox
            messagebox.showerror("Lỗi", message)

        def run(self) -> None:
            """Chạy ứng dụng."""
            self.mainloop()


else:
    # Fallback class khi không có customtkinter
    class MainWindow(tk.Tk):
        """Fallback MainWindow using tkinter."""

        WINDOW_WIDTH = 900
        WINDOW_HEIGHT = 700

        def __init__(self, controller=None):
            super().__init__()

            self.controller = controller
            self._project_items = []

            self.title("AutoCapCut - Tự động xuất video CapCut")
            self.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")

            self._setup_ui()

            if self.controller:
                self.controller.set_view(self)

        def _setup_ui(self):
            # Simple fallback UI
            ttk.Label(self, text="AutoCapCut", font=("Arial", 20, "bold")).pack(pady=10)
            ttk.Label(self, text="Vui lòng cài đặt customtkinter để có giao diện đẹp hơn").pack()

            self.log_text = tk.Text(self, height=10, state="disabled")
            self.log_text.pack(fill="both", expand=True, padx=10, pady=10)

        def log(self, message: str):
            self.log_text.configure(state="normal")
            self.log_text.insert("end", message + "\n")
            self.log_text.see("end")
            self.log_text.configure(state="disabled")

        def update_project_list(self, projects):
            pass

        def select_all_projects(self):
            pass

        def deselect_all_projects(self):
            pass

        def set_capcut_path(self, path: str):
            pass

        def set_data_path(self, path: str):
            pass

        def update_progress(self, current: int, total: int, project_name: str = ""):
            pass

        def update_status(self, status: str):
            pass

        def set_exporting_state(self, exporting: bool):
            pass

        def show_info(self, message: str):
            messagebox.showinfo("Info", message)

        def show_warning(self, message: str):
            messagebox.showwarning("Warning", message)

        def show_error(self, message: str):
            messagebox.showerror("Error", message)

        def run(self):
            self.mainloop()
