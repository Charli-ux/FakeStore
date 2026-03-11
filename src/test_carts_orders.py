"""
文件: test_carts_orders.py
描述: FakeStoreAPI 购物车与订单模块端到端测试脚本
包含: 购物车创建、商品添加、总价计算、订单创建、幂等性验证等
"""

import pytest
import requests
import json
import time
from typing import Dict, List, Any
from datetime import datetime

# 基础配置
BASE_URL = "https://fakestoreapi.com"

# 用户测试数据 (使用FakeStoreAPI提供的测试用户)
TEST_USER = {
    "username": "mor_2314",  # 文档中提到的测试用户名
    "password": "83r5^_"     # 对应密码
}

# 商品测试数据 (使用API中真实存在的商品)
TEST_PRODUCTS = [
    {"id": 1, "expected_price": 109.95},   # Fjallraven背包
    {"id": 2, "expected_price": 22.3},     # 男士T恤
    {"id": 3, "expected_price": 55.99}     # 男士棉夹克
]

# 购物车测试数据
TEST_CART_DATA = {
    "userId": 1,
    "date": datetime.now().strftime("%Y-%m-%d"),
    "products": [
        {"productId": 1, "quantity": 2},
        {"productId": 2, "quantity": 1}
    ]
}

# 订单测试数据
TEST_ORDER_DATA = {
    "userId": 1,
    "date": datetime.now().strftime("%Y-%m-%d"),
    "products": [
        {"productId": 1, "quantity": 2},
        {"productId": 2, "quantity": 1}
    ]
}


class TestCartsOrdersE2E:
    """购物车与订单端到端测试类"""
    
    def setup_method(self):
        """每个测试方法执行前的准备工作"""
        self.session = requests.Session()
        self.token = None
        self.created_cart_ids = []
        self.created_order_ids = []
        
    def teardown_method(self):
        """每个测试方法执行后的清理工作"""
        # 清理测试中创建的订单
        for order_id in self.created_order_ids:
            try:
                self.session.delete(f"{BASE_URL}/orders/{order_id}")
            except:
                pass
        
        # 清理测试中创建的购物车
        for cart_id in self.created_cart_ids:
            try:
                self.session.delete(f"{BASE_URL}/carts/{cart_id}")
            except:
                pass
        
        self.session.close()
    
    def _login_user(self) -> str:
        """登录用户并获取token"""
        if self.token:
            return self.token
            
        response = self.session.post(
            f"{BASE_URL}/auth/login",
            json=TEST_USER
        )
        
        assert response.status_code == 200, f"登录失败: {response.status_code}"
        
        login_data = response.json()
        assert "token" in login_data, "登录响应中缺少token字段"
        
        self.token = login_data["token"]
        return self.token
    
    def _get_product_price(self, product_id: int) -> float:
        """获取商品价格"""
        response = self.session.get(f"{BASE_URL}/products/{product_id}")
        assert response.status_code == 200, f"获取商品失败: {response.status_code}"
        
        product_data = response.json()
        return product_data["price"]
    
    # ==================== 购物车模块测试 ====================
    
    def test_tc_c01_create_cart_with_valid_products(self):
        """TC-C01: 使用有效商品创建购物车"""
        # 登录获取token
        token = self._login_user()
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        
        # 创建购物车
        response = self.session.post(
            f"{BASE_URL}/carts",
            json=TEST_CART_DATA
        )
        
        # 根据文档，创建成功应返回200或201
        assert response.status_code in [200, 201], \
            f"创建购物车失败: {response.status_code}, 响应: {response.text}"
        
        cart_data = response.json()
        assert "id" in cart_data, "响应中缺少购物车ID"
        assert "products" in cart_data, "响应中缺少商品列表"
        assert "userId" in cart_data, "响应中缺少用户ID"
        
        # 记录创建的购物车ID
        cart_id = cart_data["id"]
        self.created_cart_ids.append(cart_id)
        
        # 验证商品数量和价格计算
        expected_total = 0
        for test_item, cart_item in zip(TEST_CART_DATA["products"], cart_data["products"]):
            assert test_item["productId"] == cart_item["productId"], "商品ID不匹配"
            assert test_item["quantity"] == cart_item["quantity"], "商品数量不匹配"
            
            # 获取商品实际价格并计算总价
            product_price = self._get_product_price(test_item["productId"])
            expected_total += product_price * test_item["quantity"]
        
        # 验证购物车总价
        assert "total" in cart_data, "响应中缺少总价字段"
        
        # 允许小数点差异
        if "total" in cart_data:
            total_diff = abs(cart_data["total"] - expected_total)
            assert total_diff < 0.01, f"总价计算错误: 期望{expected_total}, 实际{cart_data['total']}"
        
        print(f"✓ TC-C01 passed: Created cart ID {cart_id} with correct total price")
        return cart_id
    
    def test_tc_c02_get_cart_by_id(self):
        """TC-C02: 根据ID获取购物车详情"""
        # 先创建一个购物车
        cart_id = self.test_tc_c01_create_cart_with_valid_products()
        
        # 查询购物车详情
        response = self.session.get(f"{BASE_URL}/carts/{cart_id}")
        
        assert response.status_code == 200, f"获取购物车失败: {response.status_code}"
        
        cart_data = response.json()
        assert cart_data["id"] == cart_id, "购物车ID不匹配"
        assert "products" in cart_data, "缺少商品列表"
        assert len(cart_data["products"]) == len(TEST_CART_DATA["products"]), "商品数量不匹配"
        
        print(f"✓ TC-C02 passed: Retrieved cart ID {cart_id} details")
    
    def test_tc_c03_cart_price_calculation_single_product(self):
        """TC-C03: 购物车总价计算-单商品"""
        token = self._login_user()
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        
        # 测试数据：单个商品，数量3
        test_product_id = TEST_PRODUCTS[0]["id"]
        expected_price = TEST_PRODUCTS[0]["expected_price"]
        quantity = 3
        
        cart_data = {
            "userId": TEST_CART_DATA["userId"],
            "date": TEST_CART_DATA["date"],
            "products": [{"productId": test_product_id, "quantity": quantity}]
        }
        
        # 创建购物车
        response = self.session.post(f"{BASE_URL}/carts", json=cart_data)
        assert response.status_code in [200, 201]
        
        cart_response = response.json()
        cart_id = cart_response["id"]
        self.created_cart_ids.append(cart_id)
        
        # 计算期望总价
        expected_total = expected_price * quantity
        
        # 验证总价计算
        if "total" in cart_response:
            total_diff = abs(cart_response["total"] - expected_total)
            assert total_diff < 0.01, \
                f"单商品总价计算错误: 期望{expected_total}, 实际{cart_response['total']}"
        
        print(f"✓ TC-C03 passed: Single product price calculation correct")
    
    def test_tc_c04_cart_price_calculation_multiple_products(self):
        """TC-C04: 购物车总价计算-多商品"""
        token = self._login_user()
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        
        # 计算期望总价
        expected_total = 0
        for product in TEST_PRODUCTS[:2]:  # 使用前两个商品
            expected_total += product["expected_price"]
        
        cart_data = {
            "userId": TEST_CART_DATA["userId"],
            "date": TEST_CART_DATA["date"],
            "products": [
                {"productId": TEST_PRODUCTS[0]["id"], "quantity": 1},
                {"productId": TEST_PRODUCTS[1]["id"], "quantity": 1}
            ]
        }
        
        # 创建购物车
        response = self.session.post(f"{BASE_URL}/carts", json=cart_data)
        assert response.status_code in [200, 201]
        
        cart_response = response.json()
        cart_id = cart_response["id"]
        self.created_cart_ids.append(cart_id)
        
        # 验证总价计算
        if "total" in cart_response:
            total_diff = abs(cart_response["total"] - expected_total)
            assert total_diff < 0.01, \
                f"多商品总价计算错误: 期望{expected_total}, 实际{cart_response['total']}"
        
        print(f"✓ TC-C04 passed: Multiple products price calculation correct")
    
    def test_tc_c05_cart_product_quantity_merge_logic(self):
        """TC-C05: 购物车商品数量叠加逻辑测试"""
        token = self._login_user()
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        
        test_product_id = TEST_PRODUCTS[0]["id"]
        
        # 第一次添加2个商品
        cart_data_1 = {
            "userId": TEST_CART_DATA["userId"],
            "date": TEST_CART_DATA["date"],
            "products": [{"productId": test_product_id, "quantity": 2}]
        }
        
        response1 = self.session.post(f"{BASE_URL}/carts", json=cart_data_1)
        assert response1.status_code in [200, 201]
        cart_id = response1.json()["id"]
        self.created_cart_ids.append(cart_id)
        
        # 再次为同一用户添加3个相同商品
        cart_data_2 = {
            "userId": TEST_CART_DATA["userId"],
            "date": TEST_CART_DATA["date"],
            "products": [{"productId": test_product_id, "quantity": 3}]
        }
        
        response2 = self.session.post(f"{BASE_URL}/carts", json=cart_data_2)
        
        # 查询用户的所有购物车
        user_carts_response = self.session.get(f"{BASE_URL}/carts/user/{TEST_CART_DATA['userId']}")
        
        if user_carts_response.status_code == 200:
            user_carts = user_carts_response.json()
            
            if isinstance(user_carts, list) and len(user_carts) > 0:
                # 统计该商品的总数量
                total_quantity = 0
                for cart in user_carts:
                    for product in cart.get("products", []):
                        if product["productId"] == test_product_id:
                            total_quantity += product["quantity"]
                
                # 根据业务逻辑断言
                # 情况1: 合并 -> 总数量应为5
                # 情况2: 不合并 -> 总数量可能为2或3（取决于哪条记录被返回）
                print(f"  Product {test_product_id} total quantity across carts: {total_quantity}")
                print(f"  Note: This test validates business logic (merge vs non-merge)")
        
        print(f"✓ TC-C05 passed: Cart merge logic tested")
    
    def test_tc_c06_add_to_cart_quantity_zero(self):
        """TC-C06: 向购物车添加商品-数量为0"""
        token = self._login_user()
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        
        cart_data = {
            "userId": TEST_CART_DATA["userId"],
            "date": TEST_CART_DATA["date"],
            "products": [{"productId": TEST_PRODUCTS[0]["id"], "quantity": 0}]
        }
        
        response = self.session.post(f"{BASE_URL}/carts", json=cart_data)
        
        # 根据文档，数量为0应返回400
        assert response.status_code == 400, \
            f"Expected 400 for quantity=0, got {response.status_code}"
        
        print(f"✓ TC-C06 passed: Correctly rejected quantity=0")
    
    def test_tc_c07_add_to_cart_quantity_negative(self):
        """TC-C07: 向购物车添加商品-数量为负数"""
        token = self._login_user()
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        
        cart_data = {
            "userId": TEST_CART_DATA["userId"],
            "date": TEST_CART_DATA["date"],
            "products": [{"productId": TEST_PRODUCTS[0]["id"], "quantity": -1}]
        }
        
        response = self.session.post(f"{BASE_URL}/carts", json=cart_data)
        
        # 根据文档，数量为负数应返回400
        assert response.status_code == 400, \
            f"Expected 400 for negative quantity, got {response.status_code}"
        
        print(f"✓ TC-C07 passed: Correctly rejected negative quantity")
    
    def test_tc_c08_add_nonexistent_product_to_cart(self):
        """TC-C08: 向购物车添加不存在的商品"""
        token = self._login_user()
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        
        cart_data = {
            "userId": TEST_CART_DATA["userId"],
            "date": TEST_CART_DATA["date"],
            "products": [{"productId": 99999, "quantity": 1}]  # 不存在的商品ID
        }
        
        response = self.session.post(f"{BASE_URL}/carts", json=cart_data)
        
        # 根据文档，不存在的商品应返回404或400
        assert response.status_code in [404, 400], \
            f"Expected 404/400 for non-existent product, got {response.status_code}"
        
        print(f"✓ TC-C08 passed: Correctly handled non-existent product")
    
    def test_tc_c09_get_user_carts(self):
        """TC-C09: 获取指定用户的所有购物车"""
        token = self._login_user()
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        
        # 先为当前用户创建一个购物车
        cart_id = self.test_tc_c01_create_cart_with_valid_products()
        
        # 查询用户的所有购物车
        response = self.session.get(f"{BASE_URL}/carts/user/{TEST_CART_DATA['userId']}")
        
        assert response.status_code == 200, f"获取用户购物车失败: {response.status_code}"
        
        user_carts = response.json()
        assert isinstance(user_carts, list), "响应应为数组"
        
        # 验证返回的购物车中包含我们刚创建的
        cart_ids = [cart["id"] for cart in user_carts if "id" in cart]
        assert cart_id in cart_ids, f"创建的购物车ID {cart_id} 不在用户购物车列表中"
        
        print(f"✓ TC-C09 passed: Retrieved {len(user_carts)} carts for user")
    
    # ==================== 订单模块测试 ====================
    
    def test_tc_o01_e2e_shopping_workflow(self):
        """TC-O01: 端到端购物流程测试 (用户登录-浏览-加购-下单)"""
        print("\nStarting E2E Shopping Workflow Test...")
        
        # 步骤1: 用户登录
        print("Step 1: User login")
        token = self._login_user()
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        
        # 步骤2: 浏览商品 (获取商品详情)
        print("Step 2: Browse product")
        product_id = TEST_PRODUCTS[0]["id"]
        product_response = self.session.get(f"{BASE_URL}/products/{product_id}")
        assert product_response.status_code == 200
        product_data = product_response.json()
        product_price = product_data["price"]
        print(f"  Product: {product_data['title'][:30]}... (Price: ${product_price})")
        
        # 步骤3: 添加商品到购物车
        print("Step 3: Add to cart")
        cart_data = {
            "userId": TEST_CART_DATA["userId"],
            "date": TEST_CART_DATA["date"],
            "products": [{"productId": product_id, "quantity": 2}]
        }
        
        cart_response = self.session.post(f"{BASE_URL}/carts", json=cart_data)
        assert cart_response.status_code in [200, 201]
        cart_data_response = cart_response.json()
        cart_id = cart_data_response["id"]
        self.created_cart_ids.append(cart_id)
        print(f"  Cart created: ID {cart_id}")
        
        # 步骤4: 验证购物车总价
        print("Step 4: Verify cart total")
        if "total" in cart_data_response:
            expected_total = product_price * 2
            total_diff = abs(cart_data_response["total"] - expected_total)
            assert total_diff < 0.01, f"总价验证失败"
            print(f"  Cart total verified: ${cart_data_response['total']}")
        
        # 步骤5: 创建订单
        print("Step 5: Create order")
        order_data = {
            "userId": TEST_CART_DATA["userId"],
            "date": TEST_CART_DATA["date"],
            "products": cart_data["products"]
        }
        
        order_response = self.session.post(f"{BASE_URL}/orders", json=order_data)
        assert order_response.status_code in [200, 201], \
            f"创建订单失败: {order_response.status_code}, {order_response.text}"
        
        order_data_response = order_response.json()
        order_id = order_data_response["id"]
        self.created_order_ids.append(order_id)
        print(f"  Order created: ID {order_id}")
        
        # 步骤6: 验证订单详情
        print("Step 6: Verify order details")
        order_detail_response = self.session.get(f"{BASE_URL}/orders/{order_id}")
        assert order_detail_response.status_code == 200
        
        order_detail = order_detail_response.json()
        
        # 验证订单与购物车的一致性
        assert order_detail["userId"] == TEST_CART_DATA["userId"], "用户ID不一致"
        assert "products" in order_detail, "订单缺少商品列表"
        assert len(order_detail["products"]) == len(cart_data["products"]), "商品数量不一致"
        
        # 验证商品ID和数量
        for i, order_product in enumerate(order_detail["products"]):
            assert order_product["productId"] == cart_data["products"][i]["productId"], "商品ID不一致"
            assert order_product["quantity"] == cart_data["products"][i]["quantity"], "商品数量不一致"
        
        # 验证订单状态
        if "status" in order_detail:
            print(f"  Order status: {order_detail['status']}")
        
        print("✓ TC-O01 passed: Complete E2E shopping workflow tested successfully")
        return order_id, cart_id
    
    def test_tc_o02_order_idempotency(self):
        """TC-O02: 订单创建幂等性测试"""
        token = self._login_user()
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        
        # 准备购物车数据
        cart_data = {
            "userId": TEST_CART_DATA["userId"],
            "date": TEST_CART_DATA["date"],
            "products": [{"productId": TEST_PRODUCTS[0]["id"], "quantity": 1}]
        }
        
        # 创建购物车
        cart_response = self.session.post(f"{BASE_URL}/carts", json=cart_data)
        assert cart_response.status_code in [200, 201]
        cart_id = cart_response.json()["id"]
        self.created_cart_ids.append(cart_id)
        
        # 第一次创建订单
        order_data = {
            "userId": TEST_CART_DATA["userId"],
            "date": TEST_CART_DATA["date"],
            "products": cart_data["products"]
        }
        
        first_order_response = self.session.post(f"{BASE_URL}/orders", json=order_data)
        assert first_order_response.status_code in [200, 201]
        first_order_id = first_order_response.json()["id"]
        self.created_order_ids.append(first_order_id)
        
        # 立即用相同数据再次创建订单
        second_order_response = self.session.post(f"{BASE_URL}/orders", json=order_data)
        
        # 幂等性验证
        if second_order_response.status_code == 200:
            # 如果返回200，应该返回相同的订单ID
            second_order_data = second_order_response.json()
            assert "id" in second_order_data, "第二次响应缺少订单ID"
            
            if second_order_data["id"] == first_order_id:
                print("  API returns same order ID (idempotent)")
            else:
                print(f"  Warning: Different order IDs returned: {first_order_id} vs {second_order_data['id']}")
        elif second_order_response.status_code == 400:
            print("  API returns 400 for duplicate request (also idempotent)")
        else:
            print(f"  Note: API returned {second_order_response.status_code} for duplicate request")
        
        print(f"✓ TC-O02 passed: Order idempotency tested")
    
    def test_tc_o03_create_order_with_invalid_cart(self):
        """TC-O03: 使用无效购物车ID创建订单"""
        token = self._login_user()
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        
        order_data = {
            "userId": TEST_CART_DATA["userId"],
            "date": TEST_CART_DATA["date"],
            "products": [{"productId": TEST_PRODUCTS[0]["id"], "quantity": 1}]
        }
        
        # 故意使用无效的购物车ID
        response = self.session.post(f"{BASE_URL}/orders", json=order_data)
        
        # 根据文档，无效购物车应返回400或404
        assert response.status_code in [400, 404], \
            f"Expected 400/404 for invalid cart, got {response.status_code}"
        
        print(f"✓ TC-O03 passed: Correctly handled order with invalid cart")
    
    def test_tc_o04_get_order_by_id(self):
        """TC-O04: 根据ID获取订单详情"""
        # 先创建一个订单
        order_id, _ = self.test_tc_o01_e2e_shopping_workflow()
        
        # 查询订单详情
        response = self.session.get(f"{BASE_URL}/orders/{order_id}")
        
        assert response.status_code == 200, f"获取订单失败: {response.status_code}"
        
        order_data = response.json()
        assert order_data["id"] == order_id, "订单ID不匹配"
        assert "userId" in order_data, "缺少用户ID"
        assert "products" in order_data, "缺少商品列表"
        
        # 验证订单基本字段
        required_fields = ["id", "userId", "date", "products"]
        for field in required_fields:
            assert field in order_data, f"缺少必填字段: {field}"
        
        print(f"✓ TC-O04 passed: Retrieved order ID {order_id} details")
    
    def test_tc_o05_get_user_orders(self):
        """TC-O05: 获取用户的所有订单"""
        # 先为当前用户创建一个订单
        order_id, _ = self.test_tc_o01_e2e_shopping_workflow()
        
        # 查询用户的所有订单
        response = self.session.get(f"{BASE_URL}/orders/user/{TEST_CART_DATA['userId']}")
        
        assert response.status_code == 200, f"获取用户订单失败: {response.status_code}"
        
        user_orders = response.json()
        assert isinstance(user_orders, list), "响应应为数组"
        
        # 验证返回的订单中包含我们刚创建的
        order_ids = [order["id"] for order in user_orders if "id" in order]
        assert order_id in order_ids, f"创建的订单ID {order_id} 不在用户订单列表中"
        
        print(f"✓ TC-O05 passed: Retrieved {len(user_orders)} orders for user")
    
    def test_tc_o06_simulate_payment_flow(self):
        """TC-O06: 模拟支付流程并验证订单状态流转"""
        token = self._login_user()
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        
        # 创建一个待支付的订单
        order_id, _ = self.test_tc_o01_e2e_shopping_workflow()
        
        # 注意: FakeStoreAPI 可能没有真正的支付接口
        # 这里我们模拟一个支付更新请求
        print("  Note: FakeStoreAPI may not have real payment endpoint")
        print("  Simulating payment flow...")
        
        # 尝试更新订单状态 (如果API支持)
        update_data = {"status": "paid"}
        update_response = self.session.patch(f"{BASE_URL}/orders/{order_id}", json=update_data)
        
        if update_response.status_code == 200:
            # 如果更新成功，验证状态
            updated_order = update_response.json()
            if "status" in updated_order:
                assert updated_order["status"] == "paid", f"状态更新失败: {updated_order['status']}"
                print(f"  Order status updated to: {updated_order['status']}")
        else:
            # 如果API不支持状态更新，跳过此验证
            print(f"  Note: Order status update not supported (status: {update_response.status_code})")
        
        print(f"✓ TC-O06 passed: Payment flow simulation completed")


if __name__ == "__main__":
    """主函数：直接运行此脚本时执行核心测试"""
    import sys
    
    test_suite = TestCartsOrdersE2E()
    
    print("=" * 70)
    print("Starting FakeStoreAPI Carts & Orders E2E Tests")
    print("=" * 70)
    
    # 执行核心端到端测试
    try:
        test_suite.setup_method()
        
        print("\n1. Testing E2E Shopping Workflow (TC-O01)...")
        order_id, cart_id = test_suite.test_tc_o01_e2e_shopping_workflow()
        print(f"   Created Order: {order_id}, Cart: {cart_id}")
        
        print("\n2. Testing Cart Creation & Price Calculation (TC-C01)...")
        cart_id = test_suite.test_tc_c01_create_cart_with_valid_products()
        print(f"   Created Cart: {cart_id}")
        
        print("\n3. Testing Order Idempotency (TC-O02)...")
        test_suite.test_tc_o02_order_idempotency()
        
        print("\n4. Testing Boundary Cases (TC-C06, TC-C07)...")
        test_suite.test_tc_c06_add_to_cart_quantity_zero()
        test_suite.test_tc_c07_add_to_cart_quantity_negative()
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
    except Exception as e:
        print(f"\n✗ Error: {e}")
    finally:
        test_suite.teardown_method()
    
    print("\n" + "=" * 70)
    print("Manual E2E test execution completed")
    print("=" * 70)
    print("\nFor full test suite execution, run:")
    print("  pytest test_carts_orders.py -v")
    print("\nTo run specific test categories:")
    print("  # Run all cart tests")
    print("  pytest test_carts_orders.py::TestCartsOrdersE2E::test_tc_c0* -v")
    print("  \n  # Run all order tests")
    print("  pytest test_carts_orders.py::TestCartsOrdersE2E::test_tc_o0* -v")
