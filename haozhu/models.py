"""豪猪码 API 数据模型"""

from decimal import Decimal

from pydantic import BaseModel, Field


class AccountInfo(BaseModel):
    """账号信息"""

    money: Decimal = Field(description="账户余额")
    num: int = Field(description="最大区号数量")


class PhoneNumber(BaseModel):
    """手机号码信息"""

    phone: str = Field(description="手机号码")
    sid: int = Field(description="项目ID")
    country_name: str = Field(default="中国", description="国家名称")
    country_code: str = Field(default="CN", description="国家代码")
    country_qu: str = Field(default="86", description="国家区号")
    sp: str = Field(default="", description="运营商")
    phone_gsd: str = Field(default="", description="号码归属地")


class Message(BaseModel):
    """短信消息"""

    sms: str = Field(description="完整短信内容")
    yzm: str = Field(default="", description="提取的验证码")
    phone: str = Field(default="", description="手机号码")
    sid: int = Field(default=0, description="项目ID")


class APIResponse(BaseModel):
    """API 通用响应"""

    code: int | str = Field(description="状态码，0 或 200 为成功")
    msg: str = Field(default="", description="响应消息")
    data: dict | list | str | None = Field(default=None, description="响应数据")

    @property
    def is_success(self) -> bool:
        """判断请求是否成功"""
        return str(self.code) in ("0", "200")
