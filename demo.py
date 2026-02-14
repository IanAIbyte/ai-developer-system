#!/usr/bin/env python3
"""
AI Developer System - Quick Demo

快速演示系统核心功能
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

print("="*70)
print("AI Developer System - Quick Demo")
print("="*70)
print()

# 演示 1: 验证导入
print("1. Testing imports...")
try:
    from orchestrator.initializer_agent import InitializerAgent
    from orchestrator.coding_agent import CodingAgent
    from orchestrator.scheduler import Scheduler
    from orchestrator.state_manager import StateManager
    print("   ✅ All modules imported successfully")
except ImportError as e:
    print(f"   ❌ Import failed: {e}")
    sys.exit(1)

# 演示 2: 验证状态管理器
print()
print("2. Testing StateManager...")
sm = StateManager(".")
metrics = sm.get_progress_metrics()
print(f"   StateManager initialized")
print(f"   Current metrics: {metrics}")

# 演示 3: 显示 CLI 帮助
print()
print("3. CLI Tools Available:")
print()
print("   a) Initializer Agent:")
print("      python -m orchestrator.initializer_agent --help")
print()
print("   b) Coding Agent:")
print("      python -m orchestrator.coding_agent --help")
print()
print("   c) Scheduler:")
print("      python -m orchestrator.scheduler --help")
print()

# 演示 4: 创建演示项目
print("4. Demo: Create a test project")
print()
print("   To create a new project, run:")
print()
print("   mkdir -p ./workspace/demo-project")
print("   echo 'Build a hello world app' > ./workspace/demo-project/user_prompt.txt")
print("   python -m orchestrator.initializer_agent \\")
print("       --project ./workspace/demo-project \\")
print("       --prompt 'Build a hello world app' \\")
print("       --template webapp")
print()
print("   Then run autonomous development:")
print()
print("   python -m orchestrator.scheduler \\")
print("       --project ./workspace/demo-project \\")
print("       --mode autonomous")
print()

print("="*70)
print("✅ Demo complete!")
print("="*70)
print()
print("For full documentation, see README.md")
print()
