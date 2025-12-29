"""豪猪码 API 自定义异常类"""


class HaoZhuError(Exception):
    """豪猪码 API 基础异常"""

    def __init__(self, message: str, code: int | str | None = None):
        self.message = message
        self.code = code
        super().__init__(message)


class AuthenticationError(HaoZhuError):
    """认证失败异常（用户名/密码错误、token 无效）"""

    pass


class APIError(HaoZhuError):
    """API 调用错误"""

    pass


class RateLimitError(HaoZhuError):
    """请求频率限制异常"""

    pass


class PhoneNotAvailableError(HaoZhuError):
    """号码不可用异常（无可用号码、号码已被占用）"""

    pass


class MessageNotReadyError(HaoZhuError):
    """验证码未就绪异常（短信尚未收到）"""

    pass


class InsufficientBalanceError(HaoZhuError):
    """余额不足异常"""

    pass
