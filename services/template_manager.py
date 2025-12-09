"""
Template Manager - Quản lý các template images cho vision recognition.

Service này cung cấp:
- Quản lý templates trong thư mục templates/
- Template versioning cho các phiên bản CapCut khác nhau
- Auto-capture templates từ CapCut UI
- Validation và caching templates
"""

import os
import json
import shutil
from typing import Optional, Dict, List, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False


@dataclass
class Template:
    """
    Model đại diện cho một template image.

    Attributes:
        name: Tên template
        path: Đường dẫn đến file image
        category: Loại template (buttons, icons, status)
        version: Phiên bản CapCut tương thích
        description: Mô tả template
        width: Chiều rộng template
        height: Chiều cao template
        created_at: Thời gian tạo
    """
    name: str
    path: str
    category: str = "buttons"
    version: str = "default"
    description: str = ""
    width: int = 0
    height: int = 0
    created_at: str = ""

    def to_dict(self) -> Dict:
        """Chuyển đổi thành dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'Template':
        """Tạo Template từ dictionary."""
        return cls(**data)


class TemplateManager:
    """
    Quản lý templates cho vision recognition.

    Class này cung cấp:
    - Load và cache templates
    - Versioning templates
    - Tự động capture templates từ UI
    - Validation templates
    """

    # Thư mục gốc chứa templates
    DEFAULT_TEMPLATE_DIR = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'templates'
    )

    # File metadata
    METADATA_FILE = "templates.json"

    def __init__(self, template_dir: Optional[str] = None):
        """
        Khởi tạo TemplateManager.

        Args:
            template_dir: Đường dẫn đến thư mục templates (tùy chọn)
        """
        self.template_dir = template_dir or self.DEFAULT_TEMPLATE_DIR
        self.metadata_path = os.path.join(self.template_dir, self.METADATA_FILE)

        # Cache templates đã load
        self._cache: Dict[str, Template] = {}

        # Đảm bảo thư mục tồn tại
        self._ensure_directories()

        # Load metadata
        self.metadata = self._load_metadata()

    def _ensure_directories(self) -> None:
        """Đảm bảo các thư mục con tồn tại."""
        categories = ['buttons', 'icons', 'status']
        for category in categories:
            path = os.path.join(self.template_dir, category)
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)

    def _load_metadata(self) -> Dict[str, Dict]:
        """
        Load metadata từ file JSON.

        Returns:
            Dictionary chứa metadata của templates
        """
        if not os.path.exists(self.metadata_path):
            return {}

        try:
            with open(self.metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"Lỗi load metadata: {e}")
            return {}

    def _save_metadata(self) -> bool:
        """
        Lưu metadata vào file JSON.

        Returns:
            True nếu lưu thành công
        """
        try:
            with open(self.metadata_path, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=4, ensure_ascii=False)
            return True
        except OSError as e:
            print(f"Lỗi lưu metadata: {e}")
            return False

    def get_template_path(
        self,
        name: str,
        category: str = "buttons",
        version: str = "default"
    ) -> Optional[str]:
        """
        Lấy đường dẫn đến template file.

        Args:
            name: Tên template (không có extension)
            category: Loại template (buttons, icons, status)
            version: Phiên bản (default, v1, v2, etc.)

        Returns:
            Đường dẫn đầy đủ đến template hoặc None nếu không tìm thấy
        """
        # Thử với version cụ thể trước
        if version != "default":
            filename = f"{name}_{version}.png"
            path = os.path.join(self.template_dir, category, filename)
            if os.path.exists(path):
                return path

        # Fallback sang default version
        filename = f"{name}.png"
        path = os.path.join(self.template_dir, category, filename)
        if os.path.exists(path):
            return path

        return None

    def get_template(
        self,
        name: str,
        category: str = "buttons",
        version: str = "default"
    ) -> Optional[Template]:
        """
        Lấy template object.

        Args:
            name: Tên template
            category: Loại template
            version: Phiên bản

        Returns:
            Template object hoặc None nếu không tìm thấy
        """
        cache_key = f"{category}/{name}_{version}"

        # Kiểm tra cache
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Lấy đường dẫn
        path = self.get_template_path(name, category, version)
        if not path:
            return None

        # Tạo Template object
        template = self._create_template_from_file(path, name, category, version)

        # Cache lại
        if template:
            self._cache[cache_key] = template

        return template

    def _create_template_from_file(
        self,
        path: str,
        name: str,
        category: str,
        version: str
    ) -> Optional[Template]:
        """
        Tạo Template object từ file.

        Args:
            path: Đường dẫn file
            name: Tên template
            category: Loại
            version: Phiên bản

        Returns:
            Template object hoặc None
        """
        if not CV2_AVAILABLE:
            return Template(name=name, path=path, category=category, version=version)

        try:
            # Đọc image để lấy kích thước
            img = cv2.imread(path)
            if img is None:
                return None

            h, w = img.shape[:2]

            # Lấy metadata từ file nếu có
            template_id = f"{category}/{name}_{version}"
            meta = self.metadata.get(template_id, {})

            return Template(
                name=name,
                path=path,
                category=category,
                version=version,
                description=meta.get('description', ''),
                width=w,
                height=h,
                created_at=meta.get('created_at', '')
            )

        except Exception as e:
            print(f"Lỗi tạo template từ file: {e}")
            return None

    def list_templates(
        self,
        category: Optional[str] = None,
        version: Optional[str] = None
    ) -> List[Template]:
        """
        Liệt kê các templates.

        Args:
            category: Lọc theo loại (None = tất cả)
            version: Lọc theo phiên bản (None = tất cả)

        Returns:
            Danh sách Template objects
        """
        templates = []
        categories = [category] if category else ['buttons', 'icons', 'status']

        for cat in categories:
            cat_path = os.path.join(self.template_dir, cat)
            if not os.path.exists(cat_path):
                continue

            # Liệt kê các file .png
            for filename in os.listdir(cat_path):
                if not filename.endswith('.png'):
                    continue

                # Parse tên và version
                name_parts = filename[:-4].split('_')
                if len(name_parts) > 1:
                    tpl_name = '_'.join(name_parts[:-1])
                    tpl_version = name_parts[-1]
                else:
                    tpl_name = name_parts[0]
                    tpl_version = 'default'

                # Lọc theo version nếu có
                if version and tpl_version != version:
                    continue

                # Lấy template
                template = self.get_template(tpl_name, cat, tpl_version)
                if template:
                    templates.append(template)

        return templates

    def add_template(
        self,
        source_path: str,
        name: str,
        category: str = "buttons",
        version: str = "default",
        description: str = ""
    ) -> bool:
        """
        Thêm template mới từ file image.

        Args:
            source_path: Đường dẫn file image nguồn
            name: Tên template
            category: Loại template
            version: Phiên bản
            description: Mô tả

        Returns:
            True nếu thêm thành công
        """
        if not os.path.exists(source_path):
            print(f"File nguồn không tồn tại: {source_path}")
            return False

        try:
            # Tạo tên file đích
            if version != "default":
                filename = f"{name}_{version}.png"
            else:
                filename = f"{name}.png"

            dest_path = os.path.join(self.template_dir, category, filename)

            # Copy file
            shutil.copy2(source_path, dest_path)

            # Lưu metadata
            template_id = f"{category}/{name}_{version}"
            self.metadata[template_id] = {
                'name': name,
                'category': category,
                'version': version,
                'description': description,
                'created_at': datetime.now().isoformat()
            }

            self._save_metadata()

            # Xóa cache nếu có
            cache_key = f"{category}/{name}_{version}"
            if cache_key in self._cache:
                del self._cache[cache_key]

            print(f"Đã thêm template: {name} ({category}/{version})")
            return True

        except Exception as e:
            print(f"Lỗi thêm template: {e}")
            return False

    def capture_template(
        self,
        name: str,
        region: Tuple[int, int, int, int],
        category: str = "buttons",
        version: str = "default",
        description: str = ""
    ) -> bool:
        """
        Chụp template từ vùng màn hình.

        Args:
            name: Tên template
            region: Vùng chụp (x, y, width, height)
            category: Loại template
            version: Phiên bản
            description: Mô tả

        Returns:
            True nếu capture thành công
        """
        if not CV2_AVAILABLE:
            print("opencv-python không khả dụng")
            return False

        try:
            # Import vision service để capture
            from services.vision_service import VisionService

            vision = VisionService()
            screenshot = vision.capture_screenshot(region)

            if screenshot is None:
                print("Không thể chụp màn hình")
                return False

            # Tạo tên file tạm
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                tmp_path = tmp.name

            # Lưu screenshot tạm
            cv2.imwrite(tmp_path, screenshot)

            # Thêm template
            result = self.add_template(tmp_path, name, category, version, description)

            # Xóa file tạm
            try:
                os.unlink(tmp_path)
            except:
                pass

            return result

        except Exception as e:
            print(f"Lỗi capture template: {e}")
            return False

    def delete_template(
        self,
        name: str,
        category: str = "buttons",
        version: str = "default"
    ) -> bool:
        """
        Xóa template.

        Args:
            name: Tên template
            category: Loại
            version: Phiên bản

        Returns:
            True nếu xóa thành công
        """
        path = self.get_template_path(name, category, version)
        if not path:
            print(f"Template không tồn tại: {name}")
            return False

        try:
            # Xóa file
            os.remove(path)

            # Xóa metadata
            template_id = f"{category}/{name}_{version}"
            if template_id in self.metadata:
                del self.metadata[template_id]
                self._save_metadata()

            # Xóa cache
            cache_key = f"{category}/{name}_{version}"
            if cache_key in self._cache:
                del self._cache[cache_key]

            print(f"Đã xóa template: {name}")
            return True

        except Exception as e:
            print(f"Lỗi xóa template: {e}")
            return False

    def validate_template(
        self,
        name: str,
        category: str = "buttons",
        version: str = "default"
    ) -> Dict[str, any]:
        """
        Validate template.

        Args:
            name: Tên template
            category: Loại
            version: Phiên bản

        Returns:
            Dictionary với kết quả validation
        """
        result = {
            'exists': False,
            'readable': False,
            'valid_size': False,
            'width': 0,
            'height': 0,
            'errors': []
        }

        # Kiểm tra file tồn tại
        path = self.get_template_path(name, category, version)
        if not path:
            result['errors'].append("Template file không tồn tại")
            return result

        result['exists'] = True

        if not CV2_AVAILABLE:
            result['errors'].append("opencv-python không khả dụng để validate")
            return result

        # Kiểm tra đọc được
        try:
            img = cv2.imread(path)
            if img is None:
                result['errors'].append("Không thể đọc template image")
                return result

            result['readable'] = True

            # Kiểm tra kích thước hợp lệ
            h, w = img.shape[:2]
            result['width'] = w
            result['height'] = h

            if w < 10 or h < 10:
                result['errors'].append(f"Template quá nhỏ ({w}x{h})")
            elif w > 1000 or h > 1000:
                result['errors'].append(f"Template quá lớn ({w}x{h})")
            else:
                result['valid_size'] = True

        except Exception as e:
            result['errors'].append(f"Lỗi validate: {e}")

        return result

    def get_all_categories(self) -> List[str]:
        """
        Lấy danh sách các categories có sẵn.

        Returns:
            Danh sách tên categories
        """
        categories = []
        for item in os.listdir(self.template_dir):
            item_path = os.path.join(self.template_dir, item)
            if os.path.isdir(item_path) and not item.startswith('.'):
                categories.append(item)
        return sorted(categories)

    def clear_cache(self) -> None:
        """Xóa cache templates."""
        self._cache.clear()

    @staticmethod
    def check_dependencies() -> dict:
        """
        Kiểm tra các thư viện phụ thuộc.

        Returns:
            Dictionary với trạng thái các thư viện
        """
        return {
            'opencv': CV2_AVAILABLE
        }
