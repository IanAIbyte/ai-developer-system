#!/usr/bin/env python3
"""
GLM-5 API 集成测试脚本

验证 GLM-5 API 连接和基本功能
"""

import os
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))


def test_api_key():
    """测试 1: 检查 API Key 配置"""
    print("\n" + "="*70)
    print("测试 1: 检查 API Key 配置")
    print("="*70)

    api_key = os.getenv("ZHIPUAI_API_KEY")

    if not api_key:
        print("❌ 失败: 未找到 ZHIPUAI_API_KEY 环境变量")
        print("\n请执行以下步骤：")
        print("  1. 访问: https://open.bigmodel.cn/usercenter/apikeys")
        print("  2. 创建 API Key")
        print("  3. 设置环境变量:")
        print("     export ZHIPUAI_API_KEY=your_actual_api_key_here")
        return False

    # 隐藏部分 key
    masked_key = api_key[:8] + "..." + api_key[-4:]
    print(f"✅ API Key 已配置: {masked_key}")
    return True


def test_client_init():
    """测试 2: GLM5Client 初始化"""
    print("\n" + "="*70)
    print("测试 2: GLM5Client 初始化")
    print("="*70)

    try:
        from orchestrator.llm_clients import GLM5Client

        client = GLM5Client()
        print("✅ GLM5Client 初始化成功")
        print(f"   API Base: {client.API_BASE}")
        print(f"   Model: {client.MODEL_NAME}")
        return True, client

    except Exception as e:
        print(f"❌ 失败: {e}")
        return False, None


def test_simple_chat(client):
    """测试 3: 简单对话测试"""
    print("\n" + "="*70)
    print("测试 3: 简单对话测试")
    print("="*70)

    try:
        messages = [
            {
                "role": "user",
                "content": "你好！请用一句话介绍你自己。"
            }
        ]

        print("发送请求: 你好！请用一句话介绍你自己。")
        print("等待 GLM-5 响应...")

        response = client.chat_completion(
            messages=messages,
            temperature=0.7,
            max_tokens=100
        )

        if response.get("error"):
            print(f"❌ API 错误: {response.get('message')}")
            return False

        content = response["choices"][0]["message"]["content"]
        print(f"✅ API 响应成功:")
        print(f"   {content}")

        return True

    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_code_generation(client):
    """测试 4: 代码生成测试"""
    print("\n" + "="*70)
    print("测试 4: 代码生成测试")
    print("="*70)

    try:
        prompt = """
请生成一个简单的 React 组件：

需求：
- 一个计数器按钮
- 点击按钮时数字增加
- 使用 TypeScript
- 包含基本样式

请只返回组件代码，不需要解释。
"""

        print("发送代码生成请求...")
        print("等待 GLM-5 生成代码...")

        generated_code = client.generate_code(
            prompt=prompt,
            temperature=0.3,
            max_tokens=1000
        )

        print("✅ 代码生成成功:")
        print("-" * 70)
        print(generated_code[:500] + "..." if len(generated_code) > 500 else generated_code)
        print("-" * 70)

        return True

    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_feature_analysis(client):
    """测试 5: 功能分析测试（简化版）"""
    print("\n" + "="*70)
    print("测试 5: 功能分析测试")
    print("="*70)

    try:
        user_prompt = """
构建一个简单的待办事项应用：
- 用户可以添加待办
- 用户可以标记完成
- 用户可以删除待办
"""

        print("分析用户需求...")
        print(f"需求: {user_prompt.strip()}")
        print("\n等待 GLM-5 生成功能列表...")

        features = client.analyze_requirements(user_prompt)

        print(f"\n✅ 功能分析成功: 生成了 {len(features)} 个功能")
        print("\n前 5 个功能:")
        for i, feature in enumerate(features[:5], 1):
            print(f"  {i}. [{feature['id']}] {feature['description']}")
            print(f"     优先级: {feature['priority']}")

        return True

    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试流程"""
    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + "  GLM-5 API 集成测试".center(68) + "█")
    print("█" + " "*68 + "█")
    print("█"*70)

    # 测试 1: API Key
    if not test_api_key():
        print("\n" + "="*70)
        print("测试终止: 请先配置 API Key")
        print("="*70)
        sys.exit(1)

    # 测试 2: 客户端初始化
    success, client = test_client_init()
    if not success:
        print("\n" + "="*70)
        print("测试失败: 无法初始化 GLM5Client")
        print("="*70)
        sys.exit(1)

    # 测试 3: 简单对话
    if not test_simple_chat(client):
        print("\n⚠️  警告: 简单对话测试失败，但继续其他测试")

    # 测试 4: 代码生成
    if not test_code_generation(client):
        print("\n⚠️  警告: 代码生成测试失败，但继续其他测试")

    # 测试 5: 功能分析
    if not test_feature_analysis(client):
        print("\n⚠️  警告: 功能分析测试失败")

    # 总结
    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + "  测试完成！".center(68) + "█")
    print("█" + " "*68 + "█")
    print("█"*70)

    print("\n下一步:")
    print("  1. 如果所有测试通过，可以开始使用 GLM-5 API 进行开发")
    print("  2. 创建新项目:")
    print("     python3 -m orchestrator.initializer_agent \\")
    print("         --project ./workspace/my-app \\")
    print("         --prompt 'Build a todo app' \\")
    print("         --template webapp")
    print("  3. 或运行自主开发:")
    print("     python3 -m orchestrator.scheduler \\")
    print("         --project ./workspace/my-app \\")
    print("         --mode autonomous")
    print()


if __name__ == "__main__":
    main()
