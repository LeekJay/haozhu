"""
豪猪码 API Python SDK

基于 aiohttp 的异步 API 客户端，支持豪猪码（豪猪接码）平台的所有主要接口。

使用示例:
    ```python
    import asyncio
    from haozhu import HaoZhuClient

    async def main():
        async with HaoZhuClient(username="user", password="pass") as client:
            # 获取账号信息
            info = await client.get_account_info()
            print(f"余额: {info.money}")

            # 获取号码
            phone = await client.get_phone(sid=123)
            print(f"号码: {phone.phone}")

            # 获取验证码
            msg = await client.get_message(sid=123, phone=phone.phone)
            print(f"验证码: {msg.yzm}")

            # 释放号码
            await client.release_phone(sid=123, phone=phone.phone)

    asyncio.run(main())
    ```

环境变量配置:
    - HAOZHU_USERNAME: 用户名
    - HAOZHU_PASSWORD: 密码
    - HAOZHU_TOKEN: 令牌（可选，如果提供则跳过登录）
    - HAOZHU_SERVER: 服务器地址（默认 https://api.haozhuma.com）
"""

from .client import HaoZhuClient
from .config import HaoZhuSettings, settings
from .constants import CARRIER_NAMES, PROVINCE_CODES, PROVINCE_NAMES, Carrier, PhoneType
from .exceptions import (
    APIError,
    AuthenticationError,
    HaoZhuError,
    InsufficientBalanceError,
    MessageNotReadyError,
    PhoneNotAvailableError,
    RateLimitError,
)
from .models import AccountInfo, Message, PhoneNumber
from .utils import setup_logging

__version__ = "0.1.0"

__all__ = [
    # 客户端
    "HaoZhuClient",
    # 配置
    "HaoZhuSettings",
    "settings",
    # 常量
    "Carrier",
    "PhoneType",
    "PROVINCE_CODES",
    "PROVINCE_NAMES",
    "CARRIER_NAMES",
    # 模型
    "AccountInfo",
    "PhoneNumber",
    "Message",
    # 异常
    "HaoZhuError",
    "AuthenticationError",
    "APIError",
    "RateLimitError",
    "PhoneNotAvailableError",
    "MessageNotReadyError",
    "InsufficientBalanceError",
    # 工具
    "setup_logging",
]
