"""
DateTime Utilities

提供日期时间处理工具函数。
"""
from datetime import datetime, timedelta
from typing import Optional, Tuple
from dateutil import parser as date_parser


def parse_datetime(dt_str: str) -> Optional[datetime]:
    """解析日期时间字符串

    Args:
        dt_str: 日期时间字符串

    Returns:
        datetime 对象，解析失败返回 None
    """
    try:
        return date_parser.parse(dt_str)
    except Exception:
        return None


def get_week_range(date: Optional[datetime] = None) -> Tuple[datetime, datetime]:
    """获取日期所在周的开始和结束时间

    Args:
        date: 目标日期，默认为今天

    Returns:
        (周一 00:00:00, 周日 23:59:59)
    """
    if date is None:
        date = datetime.now()

    # 获取周一（weekday() 返回 0 表示周一）
    monday = date - timedelta(days=date.weekday())
    start_of_week = monday.replace(hour=0, minute=0, second=0, microsecond=0)

    # 获取周日
    sunday = monday + timedelta(days=6)
    end_of_week = sunday.replace(hour=23, minute=59, second=59, microsecond=999999)

    return start_of_week, end_of_week


def get_month_range(date: Optional[datetime] = None) -> Tuple[datetime, datetime]:
    """获取日期所在月的开始和结束时间

    Args:
        date: 目标日期，默认为今天

    Returns:
        (月初 00:00:00, 月末 23:59:59)
    """
    if date is None:
        date = datetime.now()

    # 月初
    start_of_month = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # 月末
    if date.month == 12:
        next_month = date.replace(year=date.year + 1, month=1, day=1)
    else:
        next_month = date.replace(month=date.month + 1, day=1)

    end_of_month = next_month - timedelta(seconds=1)

    return start_of_month, end_of_month


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """格式化日期时间

    Args:
        dt: datetime 对象
        format_str: 格式化字符串

    Returns:
        格式化后的字符串
    """
    return dt.strftime(format_str)


def get_date_range(days: int, end_date: Optional[datetime] = None) -> Tuple[datetime, datetime]:
    """获取最近N天的日期范围

    Args:
        days: 天数
        end_date: 结束日期，默认为今天

    Returns:
        (开始日期 00:00:00, 结束日期 23:59:59)
    """
    if end_date is None:
        end_date = datetime.now()

    start_date = end_date - timedelta(days=days - 1)

    start_of_day = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)

    return start_of_day, end_of_day


def get_today_range() -> Tuple[datetime, datetime]:
    """获取今天的开始和结束时间

    Returns:
        (今天 00:00:00, 今天 23:59:59)
    """
    now = datetime.now()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    return start_of_day, end_of_day


def is_same_day(dt1: datetime, dt2: datetime) -> bool:
    """判断两个日期是否是同一天"""
    return dt1.date() == dt2.date()


def format_duration(seconds: float) -> str:
    """格式化时长

    Args:
        seconds: 秒数

    Returns:
        格式化后的时长字符串（如 "1h 23m 45s"）
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")

    return " ".join(parts)
