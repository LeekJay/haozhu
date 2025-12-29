"""豪猪码 API 配置管理"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class HaoZhuSettings(BaseSettings):
    """豪猪码配置，通过环境变量读取"""

    model_config = SettingsConfigDict(
        env_prefix="HAOZHU_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # 认证信息
    username: str = ""
    password: str = ""
    token: str = ""  # 可直接配置 token，跳过登录

    # 服务器配置
    server: str = "https://api.haozhuma.com"
    backup_server: str = "https://api.haozhuyun.com"

    # 请求配置
    timeout: int = 30  # 请求超时时间（秒）
    max_retries: int = 3  # 最大重试次数
    retry_delay: float = 1.0  # 重试基础延迟（秒）

    # 日志配置
    log_level: str = "INFO"
    log_requests: bool = False  # 是否记录请求详情

    # 项目配置
    sid: int = 0  # 默认项目ID
    author: str = ""  # 开发者账号（用于消费分成）


# 全局配置实例
settings = HaoZhuSettings()
