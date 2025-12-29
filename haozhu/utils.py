"""豪猪码 API 工具函数"""

import asyncio
import functools
import logging
from collections.abc import Awaitable, Callable
from typing import ParamSpec, TypeVar

from .config import settings

T = TypeVar("T")
P = ParamSpec("P")

# 配置日志
logger = logging.getLogger("haozhu")


def setup_logging(level: str | None = None) -> None:
    """配置日志"""
    log_level = level or settings.log_level
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def retry(
    max_attempts: int | None = None,
    delay: float | None = None,
    exceptions: tuple[type[Exception], ...] = (Exception,),
    exponential_backoff: bool = True,
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    """
    异步重试装饰器

    Args:
        max_attempts: 最大重试次数，默认使用配置
        delay: 基础延迟时间（秒），默认使用配置
        exceptions: 需要重试的异常类型
        exponential_backoff: 是否使用指数退避
    """
    _max_attempts = max_attempts or settings.max_retries
    _delay = delay or settings.retry_delay

    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            last_exception: Exception | None = None

            for attempt in range(1, _max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < _max_attempts:
                        wait_time = (
                            _delay * (2 ** (attempt - 1))
                            if exponential_backoff
                            else _delay
                        )
                        logger.warning(
                            f"请求失败 (尝试 {attempt}/{_max_attempts}): {e}. "
                            f"{wait_time:.1f}秒后重试..."
                        )
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(f"请求失败，已达最大重试次数: {e}")

            if last_exception is not None:
                raise last_exception
            raise RuntimeError("重试失败，但未捕获到异常")

        return wrapper

    return decorator
