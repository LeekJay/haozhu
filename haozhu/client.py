"""豪猪码 API 异步客户端"""

import aiohttp

from .config import HaoZhuSettings, settings
from .constants import Carrier, PhoneType
from .exceptions import (
    APIError,
    AuthenticationError,
    InsufficientBalanceError,
    MessageNotReadyError,
    PhoneNotAvailableError,
)
from .models import AccountInfo, Message, PhoneNumber
from .utils import logger, retry


class HaoZhuClient:
    """豪猪码 API 异步客户端"""

    def __init__(
        self,
        username: str | None = None,
        password: str | None = None,
        token: str | None = None,
        server: str | None = None,
        config: HaoZhuSettings | None = None,
    ):
        """
        初始化客户端

        Args:
            username: 用户名，优先级高于配置
            password: 密码，优先级高于配置
            token: 令牌，如果提供则跳过登录
            server: 服务器地址，优先级高于配置
            config: 自定义配置对象
        """
        self._config = config or settings
        self._username = username or self._config.username
        self._password = password or self._config.password
        self._token = token or self._config.token
        self._server = (server or self._config.server).rstrip("/")
        self._session: aiohttp.ClientSession | None = None

    async def __aenter__(self) -> "HaoZhuClient":
        """进入上下文管理器"""
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """退出上下文管理器"""
        await self.close()

    async def _ensure_session(self) -> aiohttp.ClientSession:
        """确保 session 已创建"""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self._config.timeout)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session

    async def close(self) -> None:
        """关闭客户端连接"""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    def _build_url(self, api: str, **params) -> str:
        """构建 API URL"""
        query_parts = [f"api={api}"]
        for key, value in params.items():
            if value is not None:
                query_parts.append(f"{key}={value}")
        query_string = "&".join(query_parts)
        return f"{self._server}/sms/?{query_string}"

    @retry(exceptions=(aiohttp.ClientError, TimeoutError))
    async def _request(self, api: str, **params) -> dict:
        """
        发送 API 请求

        Args:
            api: API 名称
            **params: 请求参数

        Returns:
            API 响应数据
        """
        session = await self._ensure_session()
        url = self._build_url(api, **params)

        if self._config.log_requests:
            logger.debug(f"请求: {url}")

        async with session.get(url) as response:
            response.raise_for_status()
            # 忽略 content-type 检查，有些服务器返回 text/html
            data = await response.json(content_type=None)

            if self._config.log_requests:
                logger.debug(f"响应: {data}")

            return data

    def _check_response(self, data: dict, context: str = "") -> None:
        """
        检查 API 响应状态

        Args:
            data: 响应数据
            context: 上下文信息（用于错误消息）
        """
        code = str(data.get("code", "-1"))
        msg = data.get("msg", "未知错误")

        if code in ("0", "200"):
            return

        # 根据错误消息判断异常类型
        error_msg = f"{context}: {msg}" if context else msg

        if "token" in msg.lower() or "登录" in msg or "密码" in msg:
            raise AuthenticationError(error_msg, code)
        elif "余额" in msg or "扣费" in msg:
            raise InsufficientBalanceError(error_msg, code)
        elif "号码" in msg and ("无" in msg or "没有" in msg or "不足" in msg):
            raise PhoneNotAvailableError(error_msg, code)
        elif "等待" in msg or ("短信" in msg and ("无" in msg or "没有" in msg)):
            raise MessageNotReadyError(error_msg, code)
        else:
            raise APIError(error_msg, code)

    async def _ensure_token(self) -> str:
        """确保已获取 token"""
        if not self._token:
            await self.login()
        return self._token

    # ==================== API 方法 ====================

    @retry(exceptions=(aiohttp.ClientError, TimeoutError))
    async def login(self) -> str:
        """
        登录获取 token

        Returns:
            登录令牌

        Raises:
            AuthenticationError: 登录失败
        """
        if not self._username or not self._password:
            raise AuthenticationError("用户名和密码不能为空")

        # 注意：pass 是 Python 保留字，需要手动构建 URL
        session = await self._ensure_session()
        url = (
            f"{self._server}/sms/?api=login&user={self._username}&pass={self._password}"
        )

        if self._config.log_requests:
            logger.debug(f"请求: {url}")

        async with session.get(url) as response:
            response.raise_for_status()
            # 忽略 content-type 检查，有些服务器返回 text/html
            data = await response.json(content_type=None)

        if self._config.log_requests:
            logger.debug(f"响应: {data}")

        self._check_response(data, "登录")
        self._token = data.get("token", "")

        if not self._token:
            raise AuthenticationError("登录成功但未返回 token")

        logger.info("登录成功")
        return self._token

    async def get_account_info(self) -> AccountInfo:
        """
        获取账号信息

        Returns:
            账号信息（余额、配额等）
        """
        token = await self._ensure_token()
        data = await self._request("getSummary", token=token)
        self._check_response(data, "获取账号信息")

        return AccountInfo(
            money=data.get("money", "0"),
            num=data.get("num", 0),
        )

    async def get_phone(
        self,
        sid: int,
        *,
        carrier: Carrier | int | None = None,
        province: int | None = None,
        phone_type: PhoneType | int | None = None,
        prefix: str | None = None,
        exclude_prefix: str | None = None,
        uid: str | None = None,
        author: str | None = None,
    ) -> PhoneNumber:
        """
        获取手机号码

        Args:
            sid: 项目ID
            carrier: 运营商代码
            province: 省份代码
            phone_type: 号码类型（虚拟卡/实卡）
            prefix: 只取号段，多个用 | 分隔，如 "1380|1580"
            exclude_prefix: 排除号段，多个用 | 分隔
            uid: 对接码ID，用于多对接码场景
            author: 开发者账号（用于消费分成）

        Returns:
            手机号码信息

        Raises:
            PhoneNotAvailableError: 无可用号码
        """
        token = await self._ensure_token()

        params = {
            "token": token,
            "sid": sid,
        }

        if carrier is not None:
            params["operator"] = int(carrier)
        if province is not None:
            params["province"] = province
        if phone_type is not None:
            params["phone_type"] = int(phone_type)
        if prefix:
            params["prefix"] = prefix
        if exclude_prefix:
            params["exclude_prefix"] = exclude_prefix
        if uid:
            params["uid"] = uid
        if author:
            params["author"] = author

        data = await self._request("getPhone", **params)
        self._check_response(data, "获取号码")

        return PhoneNumber(
            phone=data.get("phone", ""),
            sid=data.get("sid", sid),
            country_name=data.get("country_name", "中国"),
            country_code=data.get("country_code", "CN"),
            country_qu=data.get("country_qu", "86"),
            sp=data.get("sp", ""),
            phone_gsd=data.get("phone_gsd", ""),
        )

    async def get_phone_specific(
        self,
        sid: int,
        phone: str,
        *,
        author: str | None = None,
    ) -> PhoneNumber:
        """
        指定号码（占用特定号码）

        Args:
            sid: 项目ID
            phone: 目标手机号码
            author: 开发者账号（用于消费分成）

        Returns:
            手机号码信息

        Raises:
            PhoneNotAvailableError: 号码不可用
        """
        token = await self._ensure_token()

        params = {
            "token": token,
            "sid": sid,
            "phone": phone,
        }
        if author:
            params["author"] = author

        data = await self._request("getPhone", **params)
        self._check_response(data, "指定号码")

        return PhoneNumber(
            phone=data.get("phone", phone),
            sid=data.get("sid", sid),
            country_name=data.get("country_name", "中国"),
            country_code=data.get("country_code", "CN"),
            country_qu=data.get("country_qu", "86"),
            sp=data.get("sp", ""),
            phone_gsd=data.get("phone_gsd", ""),
        )

    async def get_message(
        self,
        sid: int,
        phone: str,
    ) -> Message:
        """
        获取验证码/短信

        Args:
            sid: 项目ID
            phone: 手机号码

        Returns:
            短信消息（包含完整内容和提取的验证码）

        Raises:
            MessageNotReadyError: 短信尚未收到
        """
        token = await self._ensure_token()

        data = await self._request("getMessage", token=token, sid=sid, phone=phone)
        self._check_response(data, "获取验证码")

        return Message(
            sms=data.get("sms", ""),
            yzm=data.get("yzm", ""),
            phone=phone,
            sid=sid,
        )

    async def release_phone(
        self,
        sid: int,
        phone: str,
    ) -> bool:
        """
        释放号码

        Args:
            sid: 项目ID
            phone: 手机号码

        Returns:
            是否成功
        """
        token = await self._ensure_token()

        data = await self._request("cancelRecv", token=token, sid=sid, phone=phone)
        self._check_response(data, "释放号码")

        logger.info(f"号码 {phone} 已释放")
        return True

    async def release_all(self) -> bool:
        """
        释放所有号码

        Returns:
            是否成功
        """
        token = await self._ensure_token()

        data = await self._request("cancelAllRecv", token=token)
        self._check_response(data, "释放所有号码")

        logger.info("所有号码已释放")
        return True

    async def blacklist_phone(
        self,
        sid: int,
        phone: str,
    ) -> bool:
        """
        拉黑号码

        Args:
            sid: 项目ID
            phone: 手机号码

        Returns:
            是否成功
        """
        token = await self._ensure_token()

        data = await self._request("addBlacklist", token=token, sid=sid, phone=phone)
        self._check_response(data, "拉黑号码")

        logger.info(f"号码 {phone} 已拉黑")
        return True
