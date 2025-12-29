"""豪猪码 API 常量定义"""

from enum import IntEnum


class Carrier(IntEnum):
    """运营商代码"""

    CHINA_MOBILE = 1  # 中国移动
    CHINA_UNICOM = 5  # 中国联通
    CHINA_TELECOM = 9  # 中国电信
    CHINA_BROADCAST = 14  # 中国广电
    VIRTUAL = 16  # 虚拟运营商


class PhoneType(IntEnum):
    """号码类型"""

    VIRTUAL = 0  # 虚拟卡
    REAL = 1  # 实卡


# 省份代码映射表
PROVINCE_CODES: dict[str, int] = {
    # 华北地区 (10-19)
    "北京": 10,
    "天津": 11,
    "河北": 12,
    "山西": 13,
    "内蒙古": 14,
    # 东北地区 (20-29)
    "辽宁": 20,
    "吉林": 21,
    "黑龙江": 22,
    # 华东地区 (30-39)
    "上海": 30,
    "江苏": 31,
    "浙江": 32,
    "安徽": 33,
    "福建": 34,
    "江西": 35,
    "山东": 36,
    # 中南地区 (40-49)
    "河南": 40,
    "湖北": 41,
    "湖南": 42,
    "广东": 43,
    "广西": 44,
    "海南": 45,
    # 西南地区 (50-59)
    "重庆": 50,
    "四川": 51,
    "贵州": 52,
    "云南": 53,
    "西藏": 54,
    # 西北地区 (60-65)
    "陕西": 60,
    "甘肃": 61,
    "青海": 62,
    "宁夏": 63,
    "新疆": 64,
}

# 省份代码反向映射
PROVINCE_NAMES: dict[int, str] = {v: k for k, v in PROVINCE_CODES.items()}

# 运营商名称映射
CARRIER_NAMES: dict[int, str] = {
    1: "中国移动",
    5: "中国联通",
    9: "中国电信",
    14: "中国广电",
    16: "虚拟运营商",
}
