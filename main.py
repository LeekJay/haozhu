"""豪猪码 API 使用示例"""

import asyncio

from haozhu import HaoZhuClient, MessageNotReadyError, settings, setup_logging


async def main():
    """示例：完整的接码流程"""
    # 配置日志
    setup_logging("INFO")

    # 方式1: 通过参数传入认证信息
    # async with HaoZhuClient(username="your_user", password="your_pass") as client:

    # 方式2: 通过 .env 文件配置（推荐）
    # 复制 .env.example 为 .env 并填入实际值
    async with HaoZhuClient() as client:
        # 1. 登录（如果未配置 token）
        token = await client.login()
        print(f"登录成功，Token: {token[:16]}...")

        # 2. 获取账号信息
        info = await client.get_account_info()
        print(f"账户余额: {info.money} 元")
        print(f"最大区号: {info.num}")

        # 3. 获取号码（通过 HAOZHU_SID 环境变量配置）
        sid = settings.sid
        try:
            phone = await client.get_phone(sid=sid)
            print(f"获取号码: {phone.phone}")
            print(f"运营商: {phone.sp}")
            print(f"归属地: {phone.phone_gsd}")

            # 4. 等待并获取验证码
            print("等待验证码...")
            for i in range(240):  # 最多等待240次
                try:
                    msg = await client.get_message(sid=sid, phone=phone.phone)
                    print(f"短信内容: {msg.sms}")
                    print(f"验证码: {msg.yzm}")
                    break
                except MessageNotReadyError:
                    print(f"  等待中... ({i + 1}/240)")
                    await asyncio.sleep(2)
            else:
                print("获取验证码超时")

            # 5. 释放号码
            await client.release_phone(sid=sid, phone=phone.phone)
            print("号码已释放")

        except Exception as e:
            print(f"操作失败: {e}")


async def example_with_filters():
    """示例：使用筛选条件获取号码"""
    from haozhu import Carrier, PhoneType, PROVINCE_CODES

    async with HaoZhuClient() as client:
        # 获取移动实卡，限定广东省
        phone = await client.get_phone(
            sid=123,
            carrier=Carrier.CHINA_MOBILE,
            phone_type=PhoneType.REAL,
            province=PROVINCE_CODES["广东"],
            prefix="1380|1381",  # 只取 1380/1381 号段
        )
        print(f"号码: {phone.phone}")


async def example_specific_phone():
    """示例：指定号码"""
    async with HaoZhuClient() as client:
        # 占用指定号码（用于重复接收短信场景）
        phone = await client.get_phone_specific(
            sid=123,
            phone="13800138000",
        )
        print(f"已占用号码: {phone.phone}")


if __name__ == "__main__":
    asyncio.run(main())
