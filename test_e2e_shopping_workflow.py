"""
文件: test_e2e_shopping_workflow.py
描述: FakeStoreAPI 端到端购物全流程测试脚本
场景: 用户登录 -> 浏览商品 -> 添加购物车 -> 验证总价 -> 创建订单 -> 验证订单
"""

import pytest
import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API配置
BASE_URL = "https://fakestoreapi.com"

# 测试数据
TEST_USER = {
    "username": "mor_2314",  # FakeStoreAPI提供的测试用户
    "password": "83r5^_"
}

# 测试商品数据
TEST_PRODUCT_ID = 1  # 使用商品ID=1进行测试
TEST_PRODUCT_QUANTITY = 2  # 购买数量

# 购物车测试数据
TEST_CART_DATA = {
    "userId": 1,
    "date": None,  # 动态生成
    "products": []
}

# 订单测试数据
TEST_ORDER_DATA = {
    "userId": 1,
    "date": None,  # 动态生成
    "products": []
}


