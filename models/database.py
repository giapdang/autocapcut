"""
Database Model - SQLite database để lưu trữ lịch sử và metrics.

Module này cung cấp:
- Export history tracking
- Error logs với screenshots
- Performance metrics
- Template versions
"""

import os
import sqlite3
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from contextlib import contextmanager


@dataclass
class ExportHistory:
    """
    Lịch sử xuất video.

    Attributes:
        id: ID duy nhất
        project_id: ID của project
        project_name: Tên project
        started_at: Thời gian bắt đầu
        completed_at: Thời gian hoàn thành
        duration: Thời gian xuất (giây)
        status: Trạng thái (success, failed, cancelled)
        error_message: Thông điệp lỗi (nếu có)
        screenshot_path: Đường dẫn screenshot (nếu có)
        metadata: Metadata bổ sung
    """
    id: Optional[int] = None
    project_id: str = ""
    project_name: str = ""
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration: float = 0.0
    status: str = "pending"
    error_message: Optional[str] = None
    screenshot_path: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Chuyển đổi thành dictionary."""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'project_name': self.project_name,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration': self.duration,
            'status': self.status,
            'error_message': self.error_message,
            'screenshot_path': self.screenshot_path,
            'metadata': self.metadata
        }


@dataclass
class PerformanceMetric:
    """
    Metrics hiệu suất.

    Attributes:
        id: ID duy nhất
        metric_name: Tên metric
        metric_value: Giá trị
        recorded_at: Thời gian ghi nhận
        context: Context bổ sung
    """
    id: Optional[int] = None
    metric_name: str = ""
    metric_value: float = 0.0
    recorded_at: Optional[datetime] = None
    context: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Chuyển đổi thành dictionary."""
        return {
            'id': self.id,
            'metric_name': self.metric_name,
            'metric_value': self.metric_value,
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None,
            'context': self.context
        }


class Database:
    """
    SQLite database để lưu trữ dữ liệu.

    Class này quản lý:
    - Export history
    - Error logs
    - Performance metrics
    - Template versions
    """

    DEFAULT_DB_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'autocapcut.db'
    )

    def __init__(self, db_path: Optional[str] = None):
        """
        Khởi tạo Database.

        Args:
            db_path: Đường dẫn đến database file
        """
        self.db_path = db_path or self.DEFAULT_DB_PATH
        self._init_database()

    @contextmanager
    def _get_connection(self):
        """
        Context manager để lấy database connection.

        Yields:
            sqlite3.Connection
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_database(self) -> None:
        """Khởi tạo database schema."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Bảng export_history
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS export_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT NOT NULL,
                    project_name TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    completed_at TEXT,
                    duration REAL DEFAULT 0.0,
                    status TEXT NOT NULL,
                    error_message TEXT,
                    screenshot_path TEXT,
                    metadata TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Bảng error_logs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS error_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    exception TEXT,
                    stack_trace TEXT,
                    screenshot_path TEXT,
                    context TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Bảng performance_metrics
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    recorded_at TEXT NOT NULL,
                    context TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Bảng template_versions
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS template_versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    template_name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    version TEXT NOT NULL,
                    path TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(template_name, category, version)
                )
            ''')

            # Tạo indexes
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_export_history_project_id 
                ON export_history(project_id)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_export_history_status 
                ON export_history(status)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_error_logs_severity 
                ON error_logs(severity)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_performance_metrics_name 
                ON performance_metrics(metric_name)
            ''')

    # ==================== Export History ====================

    def add_export_history(self, history: ExportHistory) -> int:
        """
        Thêm lịch sử xuất.

        Args:
            history: ExportHistory object

        Returns:
            ID của record đã thêm
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO export_history 
                (project_id, project_name, started_at, completed_at, duration, 
                 status, error_message, screenshot_path, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                history.project_id,
                history.project_name,
                history.started_at.isoformat() if history.started_at else None,
                history.completed_at.isoformat() if history.completed_at else None,
                history.duration,
                history.status,
                history.error_message,
                history.screenshot_path,
                json.dumps(history.metadata) if history.metadata else None
            ))

            return cursor.lastrowid

    def update_export_history(self, history_id: int, **kwargs) -> bool:
        """
        Cập nhật lịch sử xuất.

        Args:
            history_id: ID của record
            **kwargs: Các trường cần cập nhật

        Returns:
            True nếu cập nhật thành công
        """
        if not kwargs:
            return False

        # Whitelist allowed columns
        allowed_columns = {
            'project_id', 'project_name', 'started_at', 'completed_at',
            'duration', 'status', 'error_message', 'screenshot_path', 'metadata'
        }

        # Filter to only allowed columns
        filtered_kwargs = {k: v for k, v in kwargs.items() if k in allowed_columns}

        if not filtered_kwargs:
            return False

        # Xây dựng câu query an toàn
        set_clause = ', '.join([f"{key} = ?" for key in filtered_kwargs.keys()])
        values = list(filtered_kwargs.values())
        values.append(history_id)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE export_history SET {set_clause} WHERE id = ?",
                values
            )
            return cursor.rowcount > 0

    def get_export_history(
        self,
        limit: int = 100,
        offset: int = 0,
        status: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> List[ExportHistory]:
        """
        Lấy lịch sử xuất.

        Args:
            limit: Số lượng records tối đa
            offset: Offset cho pagination
            status: Lọc theo trạng thái
            project_id: Lọc theo project ID

        Returns:
            Danh sách ExportHistory
        """
        query = "SELECT * FROM export_history WHERE 1=1"
        params = []

        if status:
            query += " AND status = ?"
            params.append(status)

        if project_id:
            query += " AND project_id = ?"
            params.append(project_id)

        query += " ORDER BY started_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)

            histories = []
            for row in cursor.fetchall():
                history = ExportHistory(
                    id=row['id'],
                    project_id=row['project_id'],
                    project_name=row['project_name'],
                    started_at=datetime.fromisoformat(row['started_at']) if row['started_at'] else None,
                    completed_at=datetime.fromisoformat(row['completed_at']) if row['completed_at'] else None,
                    duration=row['duration'],
                    status=row['status'],
                    error_message=row['error_message'],
                    screenshot_path=row['screenshot_path'],
                    metadata=json.loads(row['metadata']) if row['metadata'] else None
                )
                histories.append(history)

            return histories

    def get_export_statistics(self) -> Dict[str, Any]:
        """
        Lấy thống kê xuất video.

        Returns:
            Dictionary chứa thống kê
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Tổng số exports
            cursor.execute("SELECT COUNT(*) as total FROM export_history")
            total = cursor.fetchone()['total']

            # Theo trạng thái
            cursor.execute("""
                SELECT status, COUNT(*) as count 
                FROM export_history 
                GROUP BY status
            """)
            by_status = {row['status']: row['count'] for row in cursor.fetchall()}

            # Thời gian xuất trung bình
            cursor.execute("""
                SELECT AVG(duration) as avg_duration 
                FROM export_history 
                WHERE status = 'success' AND duration > 0
            """)
            avg_duration = cursor.fetchone()['avg_duration'] or 0

            # Success rate
            success_count = by_status.get('success', 0)
            success_rate = (success_count / total * 100) if total > 0 else 0

            return {
                'total_exports': total,
                'by_status': by_status,
                'average_duration': avg_duration,
                'success_rate': success_rate
            }

    # ==================== Error Logs ====================

    def add_error_log(
        self,
        timestamp: datetime,
        severity: str,
        message: str,
        exception: Optional[str] = None,
        stack_trace: Optional[str] = None,
        screenshot_path: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Thêm error log.

        Args:
            timestamp: Thời gian lỗi
            severity: Mức độ nghiêm trọng
            message: Thông điệp lỗi
            exception: Exception text
            stack_trace: Stack trace
            screenshot_path: Đường dẫn screenshot
            context: Context bổ sung

        Returns:
            ID của record đã thêm
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO error_logs 
                (timestamp, severity, message, exception, stack_trace, 
                 screenshot_path, context)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp.isoformat(),
                severity,
                message,
                exception,
                stack_trace,
                screenshot_path,
                json.dumps(context) if context else None
            ))

            return cursor.lastrowid

    def get_error_logs(
        self,
        limit: int = 100,
        severity: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Lấy error logs.

        Args:
            limit: Số lượng records tối đa
            severity: Lọc theo severity

        Returns:
            Danh sách error logs
        """
        query = "SELECT * FROM error_logs WHERE 1=1"
        params = []

        if severity:
            query += " AND severity = ?"
            params.append(severity)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)

            logs = []
            for row in cursor.fetchall():
                log = {
                    'id': row['id'],
                    'timestamp': row['timestamp'],
                    'severity': row['severity'],
                    'message': row['message'],
                    'exception': row['exception'],
                    'stack_trace': row['stack_trace'],
                    'screenshot_path': row['screenshot_path'],
                    'context': json.loads(row['context']) if row['context'] else None
                }
                logs.append(log)

            return logs

    # ==================== Performance Metrics ====================

    def add_performance_metric(self, metric: PerformanceMetric) -> int:
        """
        Thêm performance metric.

        Args:
            metric: PerformanceMetric object

        Returns:
            ID của record đã thêm
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO performance_metrics 
                (metric_name, metric_value, recorded_at, context)
                VALUES (?, ?, ?, ?)
            ''', (
                metric.metric_name,
                metric.metric_value,
                metric.recorded_at.isoformat() if metric.recorded_at else datetime.now().isoformat(),
                json.dumps(metric.context) if metric.context else None
            ))

            return cursor.lastrowid

    def get_performance_metrics(
        self,
        metric_name: Optional[str] = None,
        limit: int = 100
    ) -> List[PerformanceMetric]:
        """
        Lấy performance metrics.

        Args:
            metric_name: Lọc theo tên metric
            limit: Số lượng records tối đa

        Returns:
            Danh sách PerformanceMetric
        """
        query = "SELECT * FROM performance_metrics WHERE 1=1"
        params = []

        if metric_name:
            query += " AND metric_name = ?"
            params.append(metric_name)

        query += " ORDER BY recorded_at DESC LIMIT ?"
        params.append(limit)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)

            metrics = []
            for row in cursor.fetchall():
                metric = PerformanceMetric(
                    id=row['id'],
                    metric_name=row['metric_name'],
                    metric_value=row['metric_value'],
                    recorded_at=datetime.fromisoformat(row['recorded_at']),
                    context=json.loads(row['context']) if row['context'] else None
                )
                metrics.append(metric)

            return metrics

    # ==================== Cleanup ====================

    def cleanup_old_records(self, days: int = 30) -> Dict[str, int]:
        """
        Xóa các records cũ.

        Args:
            days: Xóa records cũ hơn số ngày này

        Returns:
            Dictionary với số lượng records đã xóa
        """
        cutoff_date = datetime.now().timestamp() - (days * 24 * 3600)
        cutoff_iso = datetime.fromtimestamp(cutoff_date).isoformat()

        deleted = {}

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Xóa export history
            cursor.execute(
                "DELETE FROM export_history WHERE started_at < ?",
                (cutoff_iso,)
            )
            deleted['export_history'] = cursor.rowcount

            # Xóa error logs
            cursor.execute(
                "DELETE FROM error_logs WHERE timestamp < ?",
                (cutoff_iso,)
            )
            deleted['error_logs'] = cursor.rowcount

            # Xóa performance metrics
            cursor.execute(
                "DELETE FROM performance_metrics WHERE recorded_at < ?",
                (cutoff_iso,)
            )
            deleted['performance_metrics'] = cursor.rowcount

        return deleted
