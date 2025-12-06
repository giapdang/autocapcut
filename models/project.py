"""
Project Model - Model đại diện cho một project CapCut.

Model này chứa thông tin về project bao gồm:
- ID, tên, đường dẫn
- Ngày tạo, ngày chỉnh sửa
- Trạng thái (có trong thùng rác hay không)
"""

import os
import json
from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class Project:
    """
    Model đại diện cho một project CapCut.

    Attributes:
        id: ID duy nhất của project
        name: Tên project
        path: Đường dẫn đến thư mục project
        created_date: Ngày tạo project
        modified_date: Ngày chỉnh sửa cuối cùng
        is_trash: Project có trong thùng rác hay không
    """
    id: str
    name: str
    path: str
    created_date: Optional[datetime] = None
    modified_date: Optional[datetime] = None
    is_trash: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_folder(cls, folder_path: str) -> Optional['Project']:
        """
        Tạo Project từ thư mục project.

        Đọc metadata từ draft_content.json hoặc draft_info.json
        để lấy thông tin về project.

        Args:
            folder_path: Đường dẫn đến thư mục project

        Returns:
            Project object nếu thành công, None nếu thất bại
        """
        if not os.path.isdir(folder_path):
            return None

        # Lấy ID từ tên thư mục
        project_id = os.path.basename(folder_path)

        # Mặc định lấy tên từ tên thư mục
        name = project_id
        created_date = None
        modified_date = None
        is_trash = False
        metadata = {}

        # Thử đọc draft_info.json trước
        draft_info_path = os.path.join(folder_path, 'draft_info.json')
        draft_content_path = os.path.join(folder_path, 'draft_content.json')

        try:
            # Đọc draft_info.json nếu tồn tại
            if os.path.exists(draft_info_path):
                with open(draft_info_path, 'r', encoding='utf-8') as f:
                    info = json.load(f)
                    name = info.get('draft_name', name)

                    # Parse ngày tạo (timestamp milliseconds)
                    if 'tm_draft_create' in info:
                        created_date = datetime.fromtimestamp(
                            info['tm_draft_create'] / 1000
                        )

                    # Parse ngày chỉnh sửa
                    if 'tm_draft_modified' in info:
                        modified_date = datetime.fromtimestamp(
                            info['tm_draft_modified'] / 1000
                        )

                    # Kiểm tra trạng thái trash
                    is_trash = info.get('draft_is_deleted', False)

                    metadata = info

            # Nếu không có draft_info.json, thử đọc draft_content.json
            elif os.path.exists(draft_content_path):
                with open(draft_content_path, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                    name = content.get('name', name)
                    metadata = content

            # Nếu không có metadata, sử dụng thời gian file system
            if created_date is None:
                stat = os.stat(folder_path)
                created_date = datetime.fromtimestamp(stat.st_ctime)

            if modified_date is None:
                stat = os.stat(folder_path)
                modified_date = datetime.fromtimestamp(stat.st_mtime)

        except (json.JSONDecodeError, OSError, KeyError) as e:
            # Log lỗi nhưng vẫn tạo project với thông tin cơ bản
            print(f"Lỗi đọc metadata cho project {folder_path}: {e}")

            try:
                stat = os.stat(folder_path)
                created_date = datetime.fromtimestamp(stat.st_ctime)
                modified_date = datetime.fromtimestamp(stat.st_mtime)
            except OSError:
                created_date = datetime.now()
                modified_date = datetime.now()

        return cls(
            id=project_id,
            name=name,
            path=folder_path,
            created_date=created_date,
            modified_date=modified_date,
            is_trash=is_trash,
            metadata=metadata
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Chuyển đổi Project thành dictionary.

        Returns:
            Dictionary chứa thông tin project
        """
        return {
            'id': self.id,
            'name': self.name,
            'path': self.path,
            'created_date': self.created_date.isoformat() if self.created_date else None,
            'modified_date': self.modified_date.isoformat() if self.modified_date else None,
            'is_trash': self.is_trash,
            'metadata': self.metadata
        }

    def get_draft_path(self) -> str:
        """
        Lấy đường dẫn đến file draft chính.

        Returns:
            Đường dẫn đến draft_content.json
        """
        return os.path.join(self.path, 'draft_content.json')

    def exists(self) -> bool:
        """
        Kiểm tra project có tồn tại trên disk không.

        Returns:
            True nếu thư mục project tồn tại
        """
        return os.path.isdir(self.path)

    def __str__(self) -> str:
        """Biểu diễn string của project."""
        return f"Project({self.name}, created={self.created_date})"

    def __repr__(self) -> str:
        """Biểu diễn chi tiết của project."""
        return (f"Project(id='{self.id}', name='{self.name}', "
                f"path='{self.path}', is_trash={self.is_trash})")
