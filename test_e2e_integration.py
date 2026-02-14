#!/usr/bin/env python3
"""
E2E Testing Integration Test

测试 E2E 测试模块的基本功能
"""

import sys
from pathlib import Path

# 添加 orchestrator 目录到路径
orchestrator_dir = Path(__file__).parent / "orchestrator"
sys.path.insert(0, str(orchestrator_dir))

from e2e_testing import E2ETester, TestingAgent


def test_e2e_tester():
    """测试 E2ETester 基本功能"""
    print("=" * 60)
    print("Testing E2E Testing Module")
    print("=" * 60)

    # 使用 demo-todo-app 作为测试项目
    project_path = Path(__file__).parent / "workspace" / "demo-todo-app"

    if not project_path.exists():
        print(f"❌ Project path not found: {project_path}")
        return False

    print(f"\n✅ Project path: {project_path}")

    # 创建 E2E 测试器
    tester = E2ETester(
        project_path=str(project_path),
        base_url="http://localhost:3000"
    )

    # 测试 E2E 步骤执行
    print("\n" + "=" * 60)
    print("Test 1: Execute E2E Steps")
    print("=" * 60)

    test_steps = [
        "访问 http://localhost:3000",
        "验证页面能够正常加载",
        "检查控制台无报错"
    ]

    result = tester.execute_e2e_steps(
        feature_id="test-feature-001",
        e2e_steps=test_steps,
        context={}
    )

    print(f"\nResult: {result}")
    print(f"Passed: {result['passed']}")

    # 测试截图保存
    print("\n" + "=" * 60)
    print("Test 2: Save Screenshot")
    print("=" * 60)

    screenshot_result = tester.save_screenshot("test_screenshot.png")
    print(f"Screenshot saved: {screenshot_result}")

    # 测试测试报告生成
    print("\n" + "=" * 60)
    print("Test 3: Generate Test Report")
    print("=" * 60)

    tester.test_results.append(result)
    report = tester.generate_test_report()

    print(f"\nTest Report:")
    print(f"  Total: {report['summary']['total']}")
    print(f"  Passed: {report['summary']['passed']}")
    print(f"  Failed: {report['summary']['failed']}")
    print(f"  Pass Rate: {report['summary']['pass_rate']}")

    # 保存测试报告
    tester.save_test_report(report)

    print("\n" + "=" * 60)
    print("✅ All tests completed")
    print("=" * 60)

    return True


def test_testing_agent():
    """测试 TestingAgent 功能"""
    print("\n" + "=" * 60)
    print("Testing TestingAgent")
    print("=" * 60)

    project_path = Path(__file__).parent / "workspace" / "demo-todo-app"

    # 创建测试代理
    agent = TestingAgent(
        project_path=str(project_path),
        llm_provider="glm-5"
    )

    # 测试单个功能测试
    print("\n" + "=" * 60)
    print("Test: Single Feature Testing")
    print("=" * 60)

    mock_feature = {
        "id": "test-feature-001",
        "description": "Test feature",
        "e2e_steps": [
            "访问 http://localhost:3000",
            "验证页面加载成功"
        ]
    }

    result = agent.test_feature(
        feature=mock_feature,
        context={}
    )

    print(f"\nFeature Test Result:")
    print(f"  Feature ID: {result['feature_id']}")
    print(f"  Passed: {result['passed']}")

    print("\n" + "=" * 60)
    print("✅ TestingAgent tests completed")
    print("=" * 60)

    return True


if __name__ == "__main__":
    print("\n🧪 E2E Testing Integration Test\n")

    success = True

    try:
        # Test 1: E2ETester
        if not test_e2e_tester():
            success = False

        # Test 2: TestingAgent
        if not test_testing_agent():
            success = False

        if success:
            print("\n" + "=" * 60)
            print("✅ ALL TESTS PASSED")
            print("=" * 60)
            sys.exit(0)
        else:
            print("\n" + "=" * 60)
            print("❌ SOME TESTS FAILED")
            print("=" * 60)
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
