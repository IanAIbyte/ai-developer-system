#!/usr/bin/env python3
"""
MCP Client Test

测试 MCP 客户端与 Puppeteer MCP Server 的通信
"""

import sys
from pathlib import Path

# 添加 orchestrator 目录到路径
orchestrator_dir = Path(__file__).parent / "orchestrator"
sys.path.insert(0, str(orchestrator_dir))

from mcp_client import MCPClient, PuppeteerE2ETester


def test_mcp_client():
    """测试 MCP 客户端基本功能"""
    print("=" * 60)
    print("Testing MCP Client")
    print("=" * 60)

    # 创建 MCP 客户端
    client = MCPClient("npx puppeteer-mcp-server")

    # 启动服务器
    print("\nTest 1: Start MCP Server")
    print("-" * 60)

    if not client.start_server():
        print("❌ Failed to start server")
        return False

    print("✅ Server started")

    try:
        # 测试列出工具
        print("\nTest 2: List Available Tools")
        print("-" * 60)

        tools = client.list_tools()
        print(f"✅ Found {len(tools)} tools")

        if tools:
            print("\nAvailable tools:")
            for tool in tools[:5]:  # 只显示前5个
                name = tool.get("name", "unknown")
                description = tool.get("description", "")
                print(f"  - {name}: {description[:60]}...")

        # 测试导航功能
        print("\nTest 3: Navigate to URL")
        print("-" * 60)

        nav_result = client.navigate("https://example.com")

        if "error" in nav_result:
            print(f"❌ Navigation failed: {nav_result['error']}")
        else:
            print(f"✅ Navigation successful")

        # 测试截图功能
        print("\nTest 4: Take Screenshot")
        print("-" * 60)

        screenshot_path = "/tmp/test_screenshot.png"
        screenshot_result = client.screenshot(screenshot_path)

        if "error" in screenshot_result:
            print(f"❌ Screenshot failed: {screenshot_result['error']}")
        else:
            print(f"✅ Screenshot saved")

    finally:
        # 停止服务器
        print("\nTest 5: Stop Server")
        print("-" * 60)
        client.stop_server()
        print("✅ Server stopped")

    print("\n" + "=" * 60)
    print("✅ MCP Client tests completed")
    print("=" * 60)

    return True


def test_puppeteer_e2e_tester():
    """测试 PuppeteerE2ETester 功能"""
    print("\n" + "=" * 60)
    print("Testing PuppeteerE2ETester")
    print("=" * 60)

    project_path = Path(__file__).parent / "workspace" / "demo-todo-app"

    if not project_path.exists():
        print(f"❌ Project path not found: {project_path}")
        return False

    print(f"\n✅ Project path: {project_path}")

    # 创建测试器
    tester = PuppeteerE2ETester(
        project_path=str(project_path),
        base_url="https://example.com"  # 使用 example.com 进行测试
    )

    print("\nTest 1: Start Test Environment")
    print("-" * 60)

    if not tester.start():
        print("❌ Failed to start test environment")
        return False

    print("✅ Test environment started")

    try:
        # 测试 E2E 步骤执行
        print("\nTest 2: Execute E2E Steps")
        print("-" * 60)

        e2e_steps = [
            "访问 https://example.com",
            "验证页面加载成功",
            "检查页面标题"
        ]

        result = tester.execute_e2e_steps(
            feature_id="mcp-test-001",
            e2e_steps=e2e_steps,
            context={}
        )

        print(f"\nResult:")
        print(f"  Feature ID: {result['feature_id']}")
        print(f"  Passed: {result['passed']}")
        print(f"  Steps: {len(result['steps'])}")

        for step in result['steps']:
            status = "✅" if step['passed'] else "❌"
            print(f"    {status} Step {step['step_number']}: {step['description']}")

    finally:
        print("\nTest 3: Stop Test Environment")
        print("-" * 60)
        tester.stop()
        print("✅ Test environment stopped")

    print("\n" + "=" * 60)
    print("✅ PuppeteerE2ETester tests completed")
    print("=" * 60)

    return True


if __name__ == "__main__":
    print("\n🧪 MCP Client Integration Test\n")

    success = True

    try:
        # Test 1: MCP Client
        if not test_mcp_client():
            success = False

        # Test 2: PuppeteerE2ETester
        if not test_puppeteer_e2e_tester():
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
