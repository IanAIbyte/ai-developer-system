#!/usr/bin/env python3
"""
Testing Agent Test

测试专业化 Testing Agent 的功能
"""

import sys
from pathlib import Path

# Add orchestrator directory to path
orchestrator_dir = Path(__file__).parent / "orchestrator"
sys.path.insert(0, str(orchestrator_dir))

from testing_agent import TestingAgent, TestCaseGenerator, TestResultAnalyzer


def test_test_case_generator():
    """测试测试用例生成器"""
    print("=" * 60)
    print("Testing TestCaseGenerator")
    print("=" * 60)

    # Check if GLM-5 client is available
    try:
        from llm_clients import get_llm_client
        llm_client = get_llm_client("glm-5")

        generator = TestCaseGenerator(llm_client)

        # Test feature
        feature = {
            "id": "test-add-todo-001",
            "description": "添加新的待办事项",
            "e2e_steps": [
                "在输入框中输入 'Buy groceries'",
                "点击添加按钮",
                "验证列表中出现 'Buy groceries'"
            ]
        }

        context = {
            "tech_stack": "Next.js + TypeScript",
            "framework": "React"
        }

        print("\nTest 1: Generate Test Cases")
        print("-" * 60)

        test_cases = generator.generate_test_cases(feature, context)

        print(f"\nGenerated {len(test_cases)} test cases")

        for i, tc in enumerate(test_cases, 1):
            print(f"\nTest Case {i}:")
            print(f"  ID: {tc.get('id', 'N/A')}")
            print(f"  Title: {tc.get('title', 'N/A')}")
            print(f"  Category: {tc.get('category', 'N/A')}")
            print(f"  Priority: {tc.get('priority', 'N/A')}")
            print(f"  Steps: {len(tc.get('steps', []))} steps")

        return len(test_cases) > 0

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_result_analyzer():
    """测试结果分析器"""
    print("\n" + "=" * 60)
    print("Testing TestResultAnalyzer")
    print("=" * 60)

    try:
        from llm_clients import get_llm_client
        llm_client = get_llm_client("glm-5")

        analyzer = TestResultAnalyzer(llm_client)

        # Mock test result
        feature = {
            "id": "test-add-todo-001",
            "description": "添加新的待办事项"
        }

        test_result = {
            "feature_id": "test-add-todo-001",
            "steps": [
                {
                    "step_number": 1,
                    "description": "在输入框中输入 'Buy groceries'",
                    "passed": True
                },
                {
                    "step_number": 2,
                    "description": "点击添加按钮",
                    "passed": False,
                    "error": "Element not found: #add-button"
                }
            ],
            "passed": False,
            "error": "Step 2 failed"
        }

        context = {
            "tech_stack": "Next.js + TypeScript",
            "framework": "React"
        }

        print("\nTest 1: Analyze Test Failure")
        print("-" * 60)

        analysis = analyzer.analyze_failure(feature, test_result, context)

        print(f"\nAnalysis Result:")
        print(f"  Root Cause: {analysis.get('root_cause', 'N/A')}")
        print(f"  Category: {analysis.get('category', 'N/A')}")
        print(f"  Severity: {analysis.get('severity', 'N/A')}")

        suggested_fixes = analysis.get('suggested_fixes', [])
        print(f"  Suggested Fixes ({len(suggested_fixes)}):")
        for i, fix in enumerate(suggested_fixes, 1):
            print(f"    {i}. {fix}")

        verification_steps = analysis.get('verification_steps', [])
        print(f"  Verification Steps ({len(verification_steps)}):")
        for i, step in enumerate(verification_steps, 1):
            print(f"    {i}. {step}")

        return 'root_cause' in analysis

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_testing_agent():
    """测试 Testing Agent 整合功能"""
    print("\n" + "=" * 60)
    print("Testing TestingAgent")
    print("=" * 60)

    project_path = Path(__file__).parent / "workspace" / "demo-todo-app"

    if not project_path.exists():
        print(f"Project path not found: {project_path}")
        return False

    print(f"\nProject path: {project_path}")

    # Create testing agent
    try:
        agent = TestingAgent(
            project_path=str(project_path),
            llm_provider="glm-5",
            base_url="http://localhost:3000"
        )

        # Test feature
        feature = {
            "id": "test-data-model-001",
            "description": "定义 Todo 数据接口类型",
            "e2e_steps": [
                "检查 TypeScript 编译是否通过",
                "验证 Todo 类型包含 id, text, completed 字段"
            ]
        }

        context = {
            "tech_stack": "Next.js + TypeScript",
            "framework": "React"
        }

        print("\nTest 1: Test Single Feature")
        print("-" * 60)

        # Test without LLM (faster for verification)
        result = agent.test_feature(feature, context, use_llm=False)

        print(f"\nTest Result:")
        print(f"  Feature ID: {result['feature_id']}")
        print(f"  Passed: {result['passed']}")
        print(f"  Test Cases: {result['summary']['total']}")
        print(f"  Passed: {result['summary']['passed']}")
        print(f"  Failed: {result['summary']['failed']}")

        # Cleanup
        agent.cleanup()

        return 'feature_id' in result

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\nTesting Agent Integration Test\n")

    results = {
        "TestCaseGenerator": False,
        "TestResultAnalyzer": False,
        "TestingAgent": False
    }

    # Test 1: TestCaseGenerator
    try:
        results["TestCaseGenerator"] = test_test_case_generator()
    except Exception as e:
        print(f"TestCaseGenerator test failed: {e}")

    # Test 2: TestResultAnalyzer
    try:
        results["TestResultAnalyzer"] = test_result_analyzer()
    except Exception as e:
        print(f"TestResultAnalyzer test failed: {e}")

    # Test 3: TestingAgent
    try:
        results["TestingAgent"] = test_testing_agent()
    except Exception as e:
        print(f"TestingAgent test failed: {e}")

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for component, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {component}: {status}")

    all_passed = all(results.values())

    print("\n" + "=" * 60)
    if all_passed:
        print("ALL TESTS PASSED")
        print("=" * 60)
        sys.exit(0)
    else:
        print("SOME TESTS FAILED")
        print("=" * 60)
        sys.exit(1)
