#核心部分，使用@pytest.mark.paremetrize 来实现数据驱动测试，实现数据域脚本分离，覆盖大量场景，
# tests/test_auth_login.py
import pytest
from utils.api_client import APIClient
from config.settings import Config

@pytest.fixture(scope="module")
def api_client():
    """创建 API 客户端实例"""
    # 修复5: 不要传 base_url，因为 __init__ 里没定义接收它，且 Config 里已经有
    client = APIClient() 
    yield client
    client.close()

class TestUserLogin:
    """登录接口测试集合"""

    LOGIN_TEST_DATA = [
        ("正常登录", "mor_2314", "83r5^_", 200, "token"),
        ("密码错误", "mor_2314", "wrong", 401, "error"),
    ]

    @pytest.mark.parametrize(
        "case_desc, username, password, expected_status, expected_key",
        LOGIN_TEST_DATA
    )
    def test_login_scenarios(self, api_client, case_desc, username, password, expected_status, expected_key):
        payload = {"username": username, "password": password}
        
        # 修复6: 调用时传入 json=payload
        response = api_client.post("/auth/login", json=payload) 

        resp_json = response.json()
        assert response.status_code == expected_status
        assert expected_key in resp_json

    def test_login_success_from_config(self, api_client):
        # 修复7: 调用时传入 json=login_data
        response = api_client.post("/auth/login", json=Config.TEST_USER) 
        assert response.status_code == 200
        assert "token" in response.json()
