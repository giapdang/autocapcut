"""
Project Model - Model đại diện cho một project CapCut.

Model này chứa thông tin về project bao gồm:
- ID, tên, đường dẫn
- Ngày tạo, ngày chỉnh sửa
- Trạng thái (có trong thùng rác hay không)
"""

import os
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass, field

# Setup logger
logger = logging.getLogger(__name__)


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
        is_cloud: Project có phải là cloud project không
        thumbnail_path: Đường dẫn đến thumbnail (nếu có)
        metadata: Dictionary chứa metadata từ file draft
    """
    id: str
    name: str
    path: str
    created_date: Optional[datetime] = None
    modified_date: Optional[datetime] = None
    is_trash: bool = False
    is_cloud: bool = False
    thumbnail_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_folder(cls, folder_path: str) -> Optional['Project']:
        """
        Tạo Project từ thư mục project.

        Đọc metadata từ draft_content.json, draft_info.json, project.json,
        hoặc metadata.json để lấy thông tin về project.

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
        is_cloud = False
        thumbnail_path = None
        metadata = {}

        # Thử đọc các file metadata với thứ tự ưu tiên
        metadata_files = [
            'draft_info.json',
            'draft_content.json',
            'project.json',
            'metadata.json'
        ]

        for metadata_file in metadata_files:
            metadata_path = os.path.join(folder_path, metadata_file)
            if os.path.exists(metadata_path):
                try:
                    with open(metadata_path, 'r', encoding='utf-8') as f:
                        info = json.load(f)
                        
                        # Lấy tên project
                        name = info.get('draft_name') or info.get('name') or name

                        # Parse ngày tạo (timestamp milliseconds)
                        if 'tm_draft_create' in info:
                            created_date = datetime.fromtimestamp(
                                info['tm_draft_create'] / 1000
                            )
                        elif 'created_time' in info:
                            created_date = datetime.fromtimestamp(
                                info['created_time'] / 1000
                            )

                        # Parse ngày chỉnh sửa
                        if 'tm_draft_modified' in info:
                            modified_date = datetime.fromtimestamp(
                                info['tm_draft_modified'] / 1000
                            )
                        elif 'modified_time' in info or 'last_modified' in info:
                            mod_time = info.get('modified_time') or info.get('last_modified')
                            modified_date = datetime.fromtimestamp(mod_time / 1000)

                        # Kiểm tra trạng thái trash - nhiều tên trường khác nhau
                        is_trash = (
                            info.get('draft_is_deleted', False) or
                            info.get('is_trash', False) or
                            info.get('is_deleted', False) or
                            info.get('trashed', False) or
                            info.get('archived', False)
                        )

                        # Kiểm tra cloud project - lọc bỏ project online
                        is_cloud = (
                            info.get('is_cloud', False) or
                            info.get('is_online', False) or
                            info.get('online', False) or
                            info.get('cloud_synced', False)
                        )

                        # Lấy thumbnail nếu có
                        if 'cover_path' in info:
                            thumb = os.path.join(folder_path, info['cover_path'])
                            if os.path.exists(thumb):
                                thumbnail_path = thumb
                        elif 'thumbnail' in info:
                            thumb = os.path.join(folder_path, info['thumbnail'])
                            if os.path.exists(thumb):
                                thumbnail_path = thumb

                        metadata = info
                        break  # Đã tìm thấy metadata, dừng tìm kiếm

                except (json.JSONDecodeError, OSError, KeyError) as e:
                    # Log lỗi nhưng vẫn tiếp tục thử file khác
                    logger.warning(f"Lỗi đọc metadata từ {metadata_path}: {e}")
                    continue

        # Nếu không có metadata, sử dụng thời gian file system
        if created_date is None or modified_date is None:
            try:
                stat = os.stat(folder_path)
                if created_date is None:
                    created_date = datetime.fromtimestamp(stat.st_ctime)
                if modified_date is None:
                    modified_date = datetime.fromtimestamp(stat.st_mtime)
            except OSError:
                created_date = created_date or datetime.now()
                modified_date = modified_date or datetime.now()

        # Tìm thumbnail trong các vị trí phổ biến nếu chưa có
        if thumbnail_path is None:
            possible_thumbs = [
                'cover.jpg', 'cover.png', 'thumbnail.jpg', 
                'thumbnail.png', 'preview.jpg', 'preview.png'
            ]
            for thumb_name in possible_thumbs:
                thumb = os.path.join(folder_path, thumb_name)
                if os.path.exists(thumb):
                    thumbnail_path = thumb
                    break

        return cls(
            id=project_id,
            name=name,
            path=folder_path,
            created_date=created_date,
            modified_date=modified_date,
            is_trash=is_trash,
            is_cloud=is_cloud,
            thumbnail_path=thumbnail_path,
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
            'is_cloud': self.is_cloud,
            'thumbnail_path': self.thumbnail_path,
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
