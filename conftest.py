# 配置pytest的日志输出格式
import logging

def pytest_configure(config):
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )