"""
文件: test_products.py
描述: FakeStoreAPI 商品模块接口测试脚本
包含: 商品查询、创建、更新、删除等核心功能的测试用例
作者: [您的姓名]
日期: 2025-03-20
"""

import pytest
import requests
import json
from typing import Dict, Any, List

# 基础配置
BASE_URL = "https://fakestoreapi.com"
PRODUCTS_ENDPOINT = f"{BASE_URL}/products"

# 测试数据
# 用于创建新商品的有效数据
VALID_PRODUCT_DATA = {
    "title": "Test Product - Automated",
    "price": 29.99,
    "description": "This is a test product created by automated test script",
    "category": "electronics",
    "image": "https://via.placeholder.com/300"
}

# 用于更新商品的测试数据
UPDATE_PRODUCT_DATA = {
    "title": "Updated Product Title",
    "price": 39.99,
    "description": "This product has been updated by test script"
}

# 用于边界值测试的数据
BOUNDARY_TEST_CASES = [
    {"title": "T", "price": 0, "category": "test"},  # 价格边界: 0
    {"title": "T", "price": -1, "category": "test"},  # 价格边界: 负数
    {"title": "A" * 500, "price": 10.0, "category": "test"},  # 标题超长
    {"price": 19.99, "category": "test"},  # 缺少必填字段 title
]


class TestProductsModule:
    """商品模块测试类"""
    
    def setup_method(self):
        """每个测试方法执行前的准备工作"""
        self.session = requests.Session()
        self.created_product_ids = []  # 用于跟踪测试中创建的商品ID，便于清理
        
    def teardown_method(self):
        """每个测试方法执行后的清理工作"""
        # 清理测试中创建的商品
        for product_id in self.created_product_ids:
            try:
                self.session.delete(f"{PRODUCTS_ENDPOINT}/{product_id}")
            except:
                pass  # 忽略清理错误
        self.session.close()
    
    # ==================== 查询功能测试 ====================
    
    def test_tc_p01_get_all_products(self):
        """TC-P01: 获取所有商品列表"""
        response = self.session.get(PRODUCTS_ENDPOINT)
        
        # 验证状态码
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # 验证响应结构
        products = response.json()
        assert isinstance(products, list), "Response should be a list"
        assert len(products) > 0, "Product list should not be empty"
        
        # 验证商品数据结构
        first_product = products[0]
        required_fields = ["id", "title", "price", "category"]
        for field in required_fields:
            assert field in first_product, f"Missing required field: {field}"
        
        print(f"✓ TC-P01 passed: Retrieved {len(products)} products")
    
    def test_tc_p02_get_product_by_valid_id(self):
        """TC-P02: 根据有效ID获取商品详情"""
        # 先获取一个存在的商品ID
        all_products = self.session.get(PRODUCTS_ENDPOINT).json()
        valid_product_id = all_products[0]["id"]
        
        response = self.session.get(f"{PRODUCTS_ENDPOINT}/{valid_product_id}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        product = response.json()
        assert product["id"] == valid_product_id, f"Product ID mismatch"
        
        print(f"✓ TC-P02 passed: Retrieved product ID {valid_product_id}")
    
    def test_tc_p03_get_product_by_invalid_id(self):
        """TC-P03: 根据不存在的ID获取商品详情"""
        invalid_product_id = 99999  # 假设不存在的ID
        
        response = self.session.get(f"{PRODUCTS_ENDPOINT}/{invalid_product_id}")
        
        # 根据文档，不存在的商品应返回404
        assert response.status_code == 404, f"Expected 404 for non-existent product, got {response.status_code}"
        
        print(f"✓ TC-P03 passed: Correctly handled invalid product ID")
    
    def test_tc_p04_get_products_by_valid_category(self):
        """TC-P04: 根据有效分类获取商品列表"""
        valid_category = "electronics"
        
        response = self.session.get(f"{PRODUCTS_ENDPOINT}/category/{valid_category}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        products = response.json()
        if len(products) > 0:
            # 验证所有返回的商品都属于指定分类
            for product in products:
                assert product["category"] == valid_category, \
                    f"Product category mismatch: expected {valid_category}, got {product['category']}"
        
        print(f"✓ TC-P04 passed: Retrieved {len(products)} products in category '{valid_category}'")
    
    def test_tc_p05_get_products_by_invalid_category(self):
        """TC-P05: 根据无效分类获取商品列表"""
        invalid_category = "non_existent_category_123"
        
        response = self.session.get(f"{PRODUCTS_ENDPOINT}/category/{invalid_category}")
        
        # 根据文档，无效分类应返回200和空数组
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        products = response.json()
        assert products == [], f"Expected empty array for invalid category, got {products}"
        
        print(f"✓ TC-P05 passed: Correctly returned empty array for invalid category")
    
    def test_tc_p06_get_products_with_limit(self):
        """TC-P06: 使用有效limit参数进行限制查询"""
        limit = 5
        
        response = self.session.get(f"{PRODUCTS_ENDPOINT}?limit={limit}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        products = response.json()
        assert len(products) <= limit, f"Expected at most {limit} products, got {len(products)}"
        
        print(f"✓ TC-P06 passed: Limit parameter works correctly")
    
    def test_tc_p07_get_products_with_limit_zero(self):
        """TC-P07: 使用边界值limit=0进行查询"""
        response = self.session.get(f"{PRODUCTS_ENDPOINT}?limit=0")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        products = response.json()
        # limit=0 可能返回空数组或所有商品，取决于API实现
        print(f"  Note: Limit=0 returned {len(products)} products")
        
        print(f"✓ TC-P07 passed: Limit=0 handled")
    
    # ==================== 创建功能测试 ====================
    
    def test_tc_p09_create_product_with_valid_data(self):
        """TC-P09: 使用完整有效数据创建新商品"""
        response = self.session.post(PRODUCTS_ENDPOINT, json=VALID_PRODUCT_DATA)
        
        # 根据文档，创建成功应返回200或201
        assert response.status_code in [200, 201], \
            f"Expected 200/201, got {response.status_code}"
        
        created_product = response.json()
        
        # 验证返回的数据
        assert "id" in created_product, "Response should contain product ID"
        
        # 记录创建的ID以便清理
        self.created_product_ids.append(created_product["id"])
        
        # 验证数据一致性：比较请求数据和响应数据（排除自动生成的字段）
        for key in VALID_PRODUCT_DATA:
            if key in created_product:
                assert created_product[key] == VALID_PRODUCT_DATA[key], \
                    f"Data mismatch for field '{key}': expected {VALID_PRODUCT_DATA[key]}, got {created_product[key]}"
        
        print(f"✓ TC-P09 passed: Created product ID {created_product['id']}")
    
    def test_tc_p10_create_product_missing_required_field(self):
        """TC-P10: 创建商品时缺少必填字段(title)"""
        # 创建缺少title的数据
        invalid_data = VALID_PRODUCT_DATA.copy()
        del invalid_data["title"]
        
        response = self.session.post(PRODUCTS_ENDPOINT, json=invalid_data)
        
        # 根据文档，缺少必填字段应返回400
        assert response.status_code == 400, \
            f"Expected 400 for missing required field, got {response.status_code}"
        
        print(f"✓ TC-P10 passed: Correctly rejected product with missing title")
    
    @pytest.mark.parametrize("test_data,test_name", [
        (BOUNDARY_TEST_CASES[0], "price_zero"),
        (BOUNDARY_TEST_CASES[1], "price_negative"),
        (BOUNDARY_TEST_CASES[2], "title_too_long"),
    ])
    def test_create_product_boundary_values(self, test_data, test_name):
        """参数化测试：创建商品时的各种边界值"""
        response = self.session.post(PRODUCTS_ENDPOINT, json=test_data)
        
        # 边界值测试：可能返回400（校验失败）或201（API接受）
        # 这里我们主要验证API不会崩溃，有合理的响应
        assert response.status_code in [200, 201, 400], \
            f"Unexpected status code: {response.status_code}"
        
        if response.status_code in [200, 201]:
            # 如果创建成功，记录ID以便清理
            product = response.json()
            if "id" in product:
                self.created_product_ids.append(product["id"])
        
        print(f"✓ Boundary test '{test_name}' completed with status {response.status_code}")
    
    # ==================== 更新功能测试 ====================
    
    def test_tc_p11_update_existing_product(self):
        """TC-P11: 使用有效数据更新存在的商品"""
        # 先创建一个测试商品
        create_response = self.session.post(PRODUCTS_ENDPOINT, json=VALID_PRODUCT_DATA)
        assert create_response.status_code in [200, 201]
        product_id = create_response.json()["id"]
        self.created_product_ids.append(product_id)
        
        # 更新这个商品
        update_url = f"{PRODUCTS_ENDPOINT}/{product_id}"
        response = self.session.put(update_url, json=UPDATE_PRODUCT_DATA)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        updated_product = response.json()
        
        # 验证更新后的数据
        for key in UPDATE_PRODUCT_DATA:
            if key in updated_product:
                assert updated_product[key] == UPDATE_PRODUCT_DATA[key], \
                    f"Update failed for field '{key}'"
        
        print(f"✓ TC-P11 passed: Updated product ID {product_id}")
    
    def test_tc_p12_update_non_existent_product(self):
        """TC-P12: 更新不存在的商品"""
        non_existent_id = 99999
        update_url = f"{PRODUCTS_ENDPOINT}/{non_existent_id}"
        
        response = self.session.put(update_url, json=UPDATE_PRODUCT_DATA)
        
        # 根据文档，更新不存在的商品应返回404
        assert response.status_code == 404, \
            f"Expected 404 for non-existent product, got {response.status_code}"
        
        print(f"✓ TC-P12 passed: Correctly handled update for non-existent product")
    
    # ==================== 删除功能测试 ====================
    
    def test_tc_p13_delete_existing_product(self):
        """TC-P13: 删除存在的商品"""
        # 先创建一个测试商品
        create_response = self.session.post(PRODUCTS_ENDPOINT, json=VALID_PRODUCT_DATA)
        product_id = create_response.json()["id"]
        # 不添加到created_product_ids，因为我们要删除它
        
        # 删除这个商品
        delete_url = f"{PRODUCTS_ENDPOINT}/{product_id}"
        response = self.session.delete(delete_url)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # 验证商品已被删除
        get_response = self.session.get(delete_url)
        assert get_response.status_code == 404, \
            f"Product should not exist after deletion, but got {get_response.status_code}"
        
        print(f"✓ TC-P13 passed: Deleted product ID {product_id}")
    
    def test_tc_p14_delete_non_existent_product(self):
        """TC-P14: 删除不存在的商品"""
        non_existent_id = 99999
        delete_url = f"{PRODUCTS_ENDPOINT}/{non_existent_id}"
        
        response = self.session.delete(delete_url)
        
        # 根据文档，删除不存在的商品应返回404
        assert response.status_code == 404, \
            f"Expected 404 for non-existent product, got {response.status_code}"
        
        print(f"✓ TC-P14 passed: Correctly handled delete for non-existent product")
    
    # ==================== 额外测试：排序功能 ====================
    
    def test_get_products_sorted_by_price_desc(self):
        """额外测试：获取按价格降序排列的商品列表"""
        # 此测试对应文档中的设计点4：分页与排序
        response = self.session.get(f"{PRODUCTS_ENDPOINT}?sort=desc")
        
        if response.status_code == 200:
            products = response.json()
            if len(products) > 1:
                # 验证价格是否降序排列
                prices = [p["price"] for p in products if "price" in p]
                is_descending = all(prices[i] >= prices[i+1] for i in range(len(prices)-1))
                assert is_descending, "Products are not sorted in descending order by price"
                
                print(f"✓ Additional test passed: Products sorted by price (descending)")
        else:
            # 如果API不支持sort参数，跳过此断言
            print(f"  Note: Sort parameter may not be supported (status: {response.status_code})")


if __name__ == "__main__":
    """主函数：直接运行此脚本时执行测试"""
    import sys
    
    # 使用pytest运行测试
    test_class = TestProductsModule()
    
    print("=" * 60)
    print("Starting FakeStoreAPI Products Module Tests")
    print("=" * 60)
    
    # 按顺序执行一些关键测试
    key_tests = [
        ("获取所有商品", test_class.test_tc_p01_get_all_products),
        ("按ID查询商品", test_class.test_tc_p02_get_product_by_valid_id),
        ("创建商品", test_class.test_tc_p09_create_product_with_valid_data),
    ]
    
    for test_name, test_method in key_tests:
        try:
            # 执行setup
            test_class.setup_method()
            # 执行测试
            test_method()
            print()
        except AssertionError as e:
            print(f"✗ {test_name} failed: {e}")
        except Exception as e:
            print(f"✗ {test_name} error: {e}")
        finally:
            # 执行teardown
            test_class.teardown_method()
    
    print("=" * 60)
    print("Manual test execution completed")
    print("=" * 60)
    print("\nFor full test execution with detailed report, run:")
    print("  pytest test_products.py -v")
    print("Or with HTML report:")
    print("  pytest test_products.py -v --html=report.html")