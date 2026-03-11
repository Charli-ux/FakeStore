# 存放全局配置，API域名，测试账号登
class Config:
    # API 基础域名
    BASE_URL = "https://fakestoreapi.com"

    # 测试账号信息
    # 注意：FakeStore 的测试账号密码是公开的，实际项目请使用环境变量管理敏感信息
    TEST_USER = {
        "username": "mor_2314",
        "password": "83r5^_"
    }

    # 请求超时时间
    TIMEOUT = 10