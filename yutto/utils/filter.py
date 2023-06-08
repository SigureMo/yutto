from __future__ import annotations

import datetime
import re

from yutto.utils.console.logger import Logger


class Filter:
    batch_filter_start_time: datetime.datetime | None = None
    batch_filter_end_time: datetime.datetime | None = None

    @staticmethod
    def set_timer(key: str, user_input: str):
        """设置过滤器的时间"""
        timer: datetime.datetime | None = None
        if re.match(r"^\d{4}-\d{2}-\d{2}$", user_input):
            timer = datetime.datetime.strptime(user_input, "%Y-%m-%d")
        elif re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$", user_input):
            timer = datetime.datetime.strptime(user_input, "%Y-%m-%d %H:%M:%S")
        else:
            Logger.error(f"稿件过滤参数: {user_input} 看不懂呢┭┮﹏┭┮，不会生效哦")
            return
        setattr(Filter, key, timer)

    @staticmethod
    def verify_timer(datestr: str) -> bool:
        """验证过滤器"""
        if Filter.batch_filter_start_time is None and Filter.batch_filter_end_time is None:
            return True
        elif Filter.batch_filter_start_time is None and isinstance(Filter.batch_filter_end_time, datetime.datetime):
            return datetime.datetime.strptime(datestr, "%Y-%m-%d %H:%M:%S") <= Filter.batch_filter_end_time
        elif isinstance(Filter.batch_filter_start_time, datetime.datetime) and Filter.batch_filter_end_time is None:
            return datetime.datetime.strptime(datestr, "%Y-%m-%d %H:%M:%S") >= Filter.batch_filter_start_time
        else:
            assert isinstance(Filter.batch_filter_start_time, datetime.datetime)
            assert isinstance(Filter.batch_filter_end_time, datetime.datetime)
            return (
                Filter.batch_filter_start_time
                <= datetime.datetime.strptime(datestr, "%Y-%m-%d %H:%M:%S")
                <= Filter.batch_filter_end_time
            )
