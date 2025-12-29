# 豪猪码 Python SDK

基于 aiohttp 的异步 API 客户端，支持豪猪码（豪猪接码）平台的所有主要接口。

## 安装

```bash
# 使用 uv
uv sync

# 或使用 pip
pip install -e .
```

## 快速开始

### 1. 配置认证信息

复制 `.env.example` 为 `.env` 并填入实际值：

```bash
cp .env.example .env
```

```ini
HAOZHU_USERNAME=your_username
HAOZHU_PASSWORD=your_password
```

### 2. 基本使用

```python
import asyncio
from haozhu import HaoZhuClient, MessageNotReadyError

async def main():
    async with HaoZhuClient() as client:
        # 获取账号信息
        info = await client.get_account_info()
        print(f"余额: {info.money} 元")

        # 获取号码
        phone = await client.get_phone(sid=123456)
        print(f"号码: {phone.phone}")

        # 等待验证码
        for _ in range(60):
            try:
                msg = await client.get_message(sid=123456, phone=phone.phone)
                print(f"验证码: {msg.yzm}")
                break
            except MessageNotReadyError:
                await asyncio.sleep(2)

        # 释放号码
        await client.release_phone(sid=123456, phone=phone.phone)

asyncio.run(main())
```

## API 方法

| 方法 | 说明 |
|------|------|
| `login()` | 登录获取 token |
| `get_account_info()` | 获取账号余额、配额 |
| `get_phone(sid, ...)` | 获取号码（支持筛选条件） |
| `get_phone_specific(sid, phone)` | 占用指定号码 |
| `get_message(sid, phone)` | 获取短信验证码 |
| `release_phone(sid, phone)` | 释放单个号码 |
| `release_all()` | 释放所有号码 |
| `blacklist_phone(sid, phone)` | 拉黑号码 |

## 筛选条件

获取号码时支持以下筛选条件：

```python
from haozhu import HaoZhuClient, Carrier, PhoneType, PROVINCE_CODES

async with HaoZhuClient() as client:
    phone = await client.get_phone(
        sid=123456,
        carrier=Carrier.CHINA_MOBILE,      # 运营商：移动
        phone_type=PhoneType.REAL,         # 类型：实卡
        province=PROVINCE_CODES["广东"],    # 省份：广东
        prefix="1380|1381",                # 号段：1380 或 1381
        exclude_prefix="1389",             # 排除号段
    )
```

### 运营商代码

| 运营商 | 代码 | 枚举值 |
|--------|------|--------|
| 中国移动 | 1 | `Carrier.CHINA_MOBILE` |
| 中国联通 | 5 | `Carrier.CHINA_UNICOM` |
| 中国电信 | 9 | `Carrier.CHINA_TELECOM` |
| 中国广电 | 14 | `Carrier.CHINA_BROADCAST` |
| 虚拟运营商 | 16 | `Carrier.VIRTUAL` |

### 号码类型

| 类型 | 代码 | 枚举值 |
|------|------|--------|
| 虚拟卡 | 0 | `PhoneType.VIRTUAL` |
| 实卡 | 1 | `PhoneType.REAL` |

## 配置项

通过环境变量配置：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `HAOZHU_USERNAME` | 用户名 | - |
| `HAOZHU_PASSWORD` | 密码 | - |
| `HAOZHU_TOKEN` | 令牌（可跳过登录） | - |
| `HAOZHU_SERVER` | 服务器地址 | `https://api.haozhuma.com` |
| `HAOZHU_TIMEOUT` | 请求超时（秒） | `30` |
| `HAOZHU_MAX_RETRIES` | 最大重试次数 | `3` |
| `HAOZHU_LOG_LEVEL` | 日志级别 | `INFO` |
| `HAOZHU_LOG_REQUESTS` | 记录请求详情 | `false` |

## 异常处理

```python
from haozhu import (
    HaoZhuError,           # 基础异常
    AuthenticationError,   # 认证失败
    APIError,              # API 调用错误
    PhoneNotAvailableError,# 无可用号码
    MessageNotReadyError,  # 验证码未就绪
    InsufficientBalanceError,  # 余额不足
)

try:
    phone = await client.get_phone(sid=123456)
except PhoneNotAvailableError:
    print("无可用号码")
except InsufficientBalanceError:
    print("余额不足")
except HaoZhuError as e:
    print(f"API 错误: {e.message}, 代码: {e.code}")
```

## 开发

```bash
# 安装开发依赖
uv sync --dev

# 代码检查
uv run ruff check haozhu/
uv run ruff format haozhu/
uv run pyright haozhu/
```

## License

MIT
