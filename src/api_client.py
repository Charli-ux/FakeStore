#这里是用来提升代码的复用率，封装request库，避免以后重复写requests.post，实现统一的请求处理和日志输出
# 
# utils/api_client.py
import requests
import logging
from config.settings import Config

class APIClient:
    def __init__(self): # 修复1: 补全双下划线
        self.base_url = Config.BASE_URL
        self.timeout = Config.TIMEOUT
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })

    def post(self, endpoint, json=None, params=None): # 修复2: 参数名改为 json，更符合 requests 规范
        url = f"{self.base_url}{endpoint}"
        try:
            # 修复3: 这里对应传入 json 参数
            response = self.session.post(
                url,
                json=json, # 注意这里
                params=params,
                timeout=self.timeout
            )
            logging.info(f"POST 请求: {url}")
            logging.info(f"请求数据: {json}")
            logging.info(f"响应状态码: {response.status_code}")
            # 修复4: 增加非200状态码的容错，防止日志报错中断
            try:
                logging.info(f"响应数据: {response.json()}")
            except:
                logging.info(f"响应非JSON: {response.text}")
            return response
        except requests.exceptions.Timeout:
            logging.error("请求超时")
            raise
        except requests.exceptions.RequestException as e:
            logging.error(f"请求出错: {e}")
            raise

    def close(self):
        self.session.close()
