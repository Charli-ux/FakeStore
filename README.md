# FakeStoreAPI 自动化测试项目

## 项目概述

本项目是针对 FakeStoreAPI 的完整自动化测试套件，覆盖电商核心业务功能，包括用户认证、商品管理、购物车操作和订单处理等模块。项目采用 Python + Pytest + Requests 技术栈，实现了完整的接口测试自动化流程。

**项目目标**：
1. 验证 FakeStoreAPI 各接口功能的正确性
2. 实践接口测试设计与自动化实现
3. 建立可复用的电商业务测试框架

**技术栈**：
- Python 3.8+
- Pytest 测试框架
- Requests HTTP客户端
- JSON 数据格式

## 项目结构

```
FakeStoreAPI-E2E-Test/
├── README.md                      # 项目说明文档
├── requirements.txt               # Python依赖包列表
├── conftest.py                   # Pytest共享配置
├── api_client.py                 # API客户端封装
├── settings.py                   # 项目配置文件
├── src/                           # 源代码目录
│   ├── test_auth_login.py        # 用户认证模块测试
│   ├── test_products.py          # 商品模块测试
│   ├── test_carts_orders.py      # 购物车与订单模块测试
│   └── test_e2e_shopping_workflow.py  # 端到端购物流程测试
├── test_cases/                    # 测试用例文档
│   ├── 功能测试用例集.xlsx       # Excel格式测试用例
│   ├── FakeStoreAPI接口测试用例汇总.xlsx
│   └── 接口测试用例概览.docx
├── reports/                       # 测试报告目录
│   ├── products_report.html      # 商品模块测试报告
│   ├── test_carts_orders_report.html  # 购物车订单模块测试报告
│   └── shopping_workflow_report.html  # 端到端流程测试报告
├── docs/                          # 项目文档
│   ├── fakestoreapi项目业务文档.docx
│   ├── fakestoreapi需求分析.docx
│   ├── fakestoreapi项目测试策略.docx
│   └── 购物车下单全流程.docx
└── .gitignore                    # Git忽略文件配置
```

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd FakeStoreAPI-E2E-Test

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 运行测试

```bash
# 运行所有测试
pytest src/ -v

# 运行特定模块测试
pytest src/test_products.py -v
pytest src/test_carts_orders.py -v
pytest src/test_auth_login.py -v

# 运行端到端测试
pytest src/test_e2e_shopping_workflow.py -v

# 生成HTML报告
pytest src/ -v --html=reports/full_test_report.html
```

## 模块详解

### 1. 用户认证模块 (test_auth_login.py)
- 用户正常登录流程验证
- 错误凭证登录测试
- 无凭证访问受保护资源测试

### 2. 商品模块 (test_products.py)
- 商品查询（所有商品、按ID、按分类）
- 商品创建、更新、删除
- 边界值和异常场景测试

### 3. 购物车与订单模块 (test_carts_orders.py)
- 购物车创建与管理
- 商品添加与总价计算
- 订单创建与查询
- 幂等性测试

### 4. 端到端购物流程 (test_e2e_shopping_workflow.py)
- 完整的用户购物流程验证
- 从登录到下单的全流程测试
- 跨模块数据一致性验证

## 测试数据管理

项目使用FakeStoreAPI提供的测试用户和真实商品数据：

**测试用户**：
- 用户名: `mor_2314`
- 密码: `83r5^_`

**测试商品**：
- 商品ID: 1, 2, 3 (API中真实存在的商品)

## 测试设计方法

### 测试策略
- 分层测试：单接口功能测试 + 业务流程端到端测试
- 边界值分析：针对数值参数进行边界测试
- 等价类划分：对输入参数进行分类测试

### 验证点
- 状态码验证
- 数据结构验证
- 业务逻辑验证
- 数据一致性验证

## 项目维护

### 版本历史
- v1.0.0 (2025-03-20): 初始版本，包含完整测试套件

### 贡献指南
1. Fork项目
2. 创建功能分支
3. 提交代码变更
4. 添加测试用例
5. 提交Pull Request

### 许可证
本项目遵循MIT开源协议

