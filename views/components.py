"""
Components - Các thành phần giao diện tái sử dụng.

Module này chứa các widget tùy chỉnh:
- ProjectItem: Hiển thị một project
- LogWidget: Hiển thị log
- ProgressWidget: Hiển thị tiến trình
"""

from typing import Optional, Callable
from datetime import datetime

try:
    import customtkinter as ctk
    CTK_AVAILABLE = True
except ImportError:
    CTK_AVAILABLE = False
    # Fallback to tkinter
    import tkinter as tk
    from tkinter import ttk

from models.project import Project
from utils.helpers import format_datetime, get_relative_time


if CTK_AVAILABLE:
    class ProjectItem(ctk.CTkFrame):
        """
        Widget hiển thị một project với checkbox.

        Hiển thị tên project, ngày tạo, ngày chỉnh sửa
        và checkbox để chọn.
        """

        def __init__(
            self,
            master,
            project: Project,
            on_select: Optional[Callable[[Project, bool], None]] = None,
            **kwargs
        ):
            """
            Khởi tạo ProjectItem.

            Args:
                master: Parent widget
                project: Project object
                on_select: Callback khi chọn/bỏ chọn (project, selected)
            """
            super().__init__(master, **kwargs)

            self.project = project
            self.on_select = on_select
            self.selected = ctk.BooleanVar(value=False)

            self._setup_ui()

        def _setup_ui(self) -> None:
            """Thiết lập giao diện."""
            # Configure grid
            self.grid_columnconfigure(1, weight=1)

            # Checkbox
            self.checkbox = ctk.CTkCheckBox(
                self,
                text="",
                variable=self.selected,
                command=self._on_checkbox_changed,
                width=30
            )
            self.checkbox.grid(row=0, column=0, rowspan=2, padx=(10, 5), pady=5)

            # Tên project
            self.name_label = ctk.CTkLabel(
                self,
                text=self.project.name,
                font=ctk.CTkFont(size=14, weight="bold"),
                anchor="w"
            )
            self.name_label.grid(row=0, column=1, sticky="w", padx=5, pady=(5, 0))

            # Thông tin ngày tháng
            date_info = self._format_date_info()
            self.date_label = ctk.CTkLabel(
                self,
                text=date_info,
                font=ctk.CTkFont(size=11),
                text_color="gray",
                anchor="w"
            )
            self.date_label.grid(row=1, column=1, sticky="w", padx=5, pady=(0, 5))

        def _format_date_info(self) -> str:
            """Format thông tin ngày tháng."""
            created = format_datetime(self.project.created_date, "%d/%m/%Y")
            modified = get_relative_time(self.project.modified_date)
            return f"Tạo: {created} | Sửa: {modified}"

        def _on_checkbox_changed(self) -> None:
            """Xử lý khi checkbox thay đổi."""
            if self.on_select:
                self.on_select(self.project, self.selected.get())

        def set_selected(self, selected: bool) -> None:
            """
            Đặt trạng thái chọn.

            Args:
                selected: True để chọn
            """
            self.selected.set(selected)

        def is_selected(self) -> bool:
            """
            Kiểm tra có được chọn không.

            Returns:
                True nếu được chọn
            """
            return self.selected.get()


    class LogWidget(ctk.CTkFrame):
        """
        Widget hiển thị log với auto-scroll.

        Text widget cho phép hiển thị log và tự động
        scroll xuống khi có log mới.
        """

        def __init__(self, master, height: int = 200, **kwargs):
            """
            Khởi tạo LogWidget.

            Args:
                master: Parent widget
                height: Chiều cao widget
            """
            super().__init__(master, **kwargs)

            self._setup_ui(height)

        def _setup_ui(self, height: int) -> None:
            """Thiết lập giao diện."""
            self.grid_columnconfigure(0, weight=1)
            self.grid_rowconfigure(0, weight=1)

            # Text widget
            self.text_box = ctk.CTkTextbox(
                self,
                height=height,
                font=ctk.CTkFont(family="Consolas", size=12),
                wrap="word"
            )
            self.text_box.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

            # Disable editing
            self.text_box.configure(state="disabled")

        def log(self, message: str, timestamp: bool = True) -> None:
            """
            Thêm message vào log.

            Args:
                message: Nội dung log
                timestamp: Có thêm timestamp không
            """
            self.text_box.configure(state="normal")

            if timestamp:
                time_str = datetime.now().strftime("%H:%M:%S")
                message = f"[{time_str}] {message}"

            self.text_box.insert("end", message + "\n")
            self.text_box.see("end")  # Auto scroll

            self.text_box.configure(state="disabled")

        def clear(self) -> None:
            """Xóa toàn bộ log."""
            self.text_box.configure(state="normal")
            self.text_box.delete("1.0", "end")
            self.text_box.configure(state="disabled")

        def get_content(self) -> str:
            """
            Lấy toàn bộ nội dung log.

            Returns:
                Nội dung log
            """
            return self.text_box.get("1.0", "end-1c")


    class ProgressWidget(ctk.CTkFrame):
        """
        Widget hiển thị tiến trình xuất.

        Bao gồm progress bar và label trạng thái.
        """

        def __init__(self, master, **kwargs):
            """
            Khởi tạo ProgressWidget.

            Args:
                master: Parent widget
            """
            super().__init__(master, **kwargs)

            self._setup_ui()

        def _setup_ui(self) -> None:
            """Thiết lập giao diện."""
            self.grid_columnconfigure(0, weight=1)

            # Status label
            self.status_label = ctk.CTkLabel(
                self,
                text="Sẵn sàng",
                font=ctk.CTkFont(size=12),
                anchor="w"
            )
            self.status_label.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))

            # Progress bar
            self.progress_bar = ctk.CTkProgressBar(self)
            self.progress_bar.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
            self.progress_bar.set(0)

            # Progress label
            self.progress_label = ctk.CTkLabel(
                self,
                text="0/0",
                font=ctk.CTkFont(size=11),
                text_color="gray"
            )
            self.progress_label.grid(row=2, column=0, sticky="e", padx=10, pady=(0, 10))

        def update_progress(self, current: int, total: int, status: str = "") -> None:
            """
            Cập nhật tiến trình.

            Args:
                current: Số lượng hiện tại
                total: Tổng số
                status: Trạng thái
            """
            if total > 0:
                progress = current / total
                self.progress_bar.set(progress)
            else:
                self.progress_bar.set(0)

            self.progress_label.configure(text=f"{current}/{total}")

            if status:
                self.status_label.configure(text=status)

        def set_status(self, status: str) -> None:
            """
            Đặt trạng thái.

            Args:
                status: Nội dung trạng thái
            """
            self.status_label.configure(text=status)

        def reset(self) -> None:
            """Reset về trạng thái ban đầu."""
            self.progress_bar.set(0)
            self.progress_label.configure(text="0/0")
            self.status_label.configure(text="Sẵn sàng")

        def set_indeterminate(self, enabled: bool = True) -> None:
            """
            Đặt chế độ indeterminate.

            Args:
                enabled: True để bật chế độ indeterminate
            """
            if enabled:
                self.progress_bar.configure(mode="indeterminate")
                self.progress_bar.start()
            else:
                self.progress_bar.stop()
                self.progress_bar.configure(mode="determinate")


    class PathInputWidget(ctk.CTkFrame):
        """
        Widget nhập đường dẫn với nút Browse.

        Bao gồm label, entry và nút browse.
        """

        def __init__(
            self,
            master,
            label_text: str = "Đường dẫn:",
            placeholder: str = "",
            browse_type: str = "file",
            on_change: Optional[Callable[[str], None]] = None,
            **kwargs
        ):
            """
            Khởi tạo PathInputWidget.

            Args:
                master: Parent widget
                label_text: Text của label
                placeholder: Placeholder text
                browse_type: "file" hoặc "folder"
                on_change: Callback khi giá trị thay đổi
            """
            super().__init__(master, **kwargs)

            self.browse_type = browse_type
            self.on_change = on_change

            self._setup_ui(label_text, placeholder)

        def _setup_ui(self, label_text: str, placeholder: str) -> None:
            """Thiết lập giao diện."""
            self.grid_columnconfigure(1, weight=1)

            # Label
            self.label = ctk.CTkLabel(
                self,
                text=label_text,
                font=ctk.CTkFont(size=12),
                width=120,
                anchor="w"
            )
            self.label.grid(row=0, column=0, sticky="w", padx=(10, 5), pady=5)

            # Entry
            self.entry = ctk.CTkEntry(
                self,
                placeholder_text=placeholder,
                font=ctk.CTkFont(size=12)
            )
            self.entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
            self.entry.bind("<FocusOut>", self._on_focus_out)

            # Browse button
            self.browse_button = ctk.CTkButton(
                self,
                text="Browse",
                width=80,
                command=self._on_browse
            )
            self.browse_button.grid(row=0, column=2, padx=(5, 10), pady=5)

        def _on_browse(self) -> None:
            """Xử lý khi click Browse."""
            from tkinter import filedialog

            if self.browse_type == "file":
                path = filedialog.askopenfilename(
                    title="Chọn file",
                    filetypes=[("Executable", "*.exe"), ("All files", "*.*")]
                )
            else:
                path = filedialog.askdirectory(title="Chọn thư mục")

            if path:
                self.set_value(path)
                if self.on_change:
                    self.on_change(path)

        def _on_focus_out(self, event=None) -> None:
            """Xử lý khi mất focus."""
            if self.on_change:
                self.on_change(self.get_value())

        def get_value(self) -> str:
            """
            Lấy giá trị đường dẫn.

            Returns:
                Đường dẫn đã nhập
            """
            return self.entry.get()

        def set_value(self, value: str) -> None:
            """
            Đặt giá trị đường dẫn.

            Args:
                value: Giá trị mới
            """
            self.entry.delete(0, "end")
            self.entry.insert(0, value)


else:
    # Fallback classes khi không có customtkinter
    class ProjectItem(ttk.Frame):
        """Fallback ProjectItem using tkinter."""

        def __init__(self, master, project: Project, on_select=None, **kwargs):
            super().__init__(master, **kwargs)
            self.project = project
            self.on_select = on_select
            self.selected = tk.BooleanVar(value=False)

            self.checkbox = ttk.Checkbutton(
                self, text=project.name, variable=self.selected,
                command=self._on_checkbox_changed
            )
            self.checkbox.pack(anchor="w", padx=10, pady=5)

        def _on_checkbox_changed(self):
            if self.on_select:
                self.on_select(self.project, self.selected.get())

        def set_selected(self, selected: bool):
            self.selected.set(selected)

        def is_selected(self) -> bool:
            return self.selected.get()


    class LogWidget(ttk.Frame):
        """Fallback LogWidget using tkinter."""

        def __init__(self, master, height=200, **kwargs):
            super().__init__(master, **kwargs)

            self.text_box = tk.Text(self, height=10, state="disabled")
            self.text_box.pack(fill="both", expand=True, padx=5, pady=5)

        def log(self, message: str, timestamp: bool = True):
            self.text_box.configure(state="normal")
            if timestamp:
                time_str = datetime.now().strftime("%H:%M:%S")
                message = f"[{time_str}] {message}"
            self.text_box.insert("end", message + "\n")
            self.text_box.see("end")
            self.text_box.configure(state="disabled")

        def clear(self):
            self.text_box.configure(state="normal")
            self.text_box.delete("1.0", "end")
            self.text_box.configure(state="disabled")

        def get_content(self) -> str:
            return self.text_box.get("1.0", "end-1c")


    class ProgressWidget(ttk.Frame):
        """Fallback ProgressWidget using tkinter."""

        def __init__(self, master, **kwargs):
            super().__init__(master, **kwargs)

            self.status_label = ttk.Label(self, text="Sẵn sàng")
            self.status_label.pack(anchor="w", padx=10, pady=5)

            self.progress_bar = ttk.Progressbar(self, mode="determinate")
            self.progress_bar.pack(fill="x", padx=10, pady=5)

        def update_progress(self, current: int, total: int, status: str = ""):
            if total > 0:
                self.progress_bar["value"] = (current / total) * 100
            if status:
                self.status_label.configure(text=status)

        def set_status(self, status: str):
            self.status_label.configure(text=status)

        def reset(self):
            self.progress_bar["value"] = 0
            self.status_label.configure(text="Sẵn sàng")

        def set_indeterminate(self, enabled: bool = True):
            if enabled:
                self.progress_bar.configure(mode="indeterminate")
                self.progress_bar.start()
            else:
                self.progress_bar.stop()
                self.progress_bar.configure(mode="determinate")


    class PathInputWidget(ttk.Frame):
        """Fallback PathInputWidget using tkinter."""

        def __init__(self, master, label_text="Đường dẫn:", placeholder="",
                     browse_type="file", on_change=None, **kwargs):
            super().__init__(master, **kwargs)
            self.browse_type = browse_type
            self.on_change = on_change

            ttk.Label(self, text=label_text).pack(side="left", padx=5)
            self.entry = ttk.Entry(self)
            self.entry.pack(side="left", fill="x", expand=True, padx=5)

            ttk.Button(self, text="Browse", command=self._on_browse).pack(side="right", padx=5)

        def _on_browse(self):
            from tkinter import filedialog
            if self.browse_type == "file":
                path = filedialog.askopenfilename()
            else:
                path = filedialog.askdirectory()
            if path:
                self.set_value(path)
                if self.on_change:
                    self.on_change(path)

        def get_value(self) -> str:
            return self.entry.get()

        def set_value(self, value: str):
            self.entry.delete(0, "end")
            self.entry.insert(0, value)
