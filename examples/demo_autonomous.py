#!/usr/bin/env python3
"""
AI Developer System - Demo: 自主开发模式

这个脚本演示如何使用调度器的自主模式，让 AI 自动完成所有功能。
"""

import sys
from pathlib import Path

# 添加项目路径到 sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from orchestrator.scheduler import Scheduler


def main():
    """运行自主开发演示"""

    # 项目路径
    project_dir = "./workspace/my-first-ai-app"

    print("="*70)
    print("AI Developer System - Autonomous Development Demo")
    print("="*70)
    print()
    print("This will run the coding agent autonomously until all features")
    print("in the feature list are implemented and tested.")
    print()
    print(f"Project: {project_dir}")
    print("Mode: autonomous")
    print()
    print("The agent will:")
    print("  1. Read the feature_list.json")
    print("  2. Select the highest-priority pending feature")
    print("  3. Implement the feature")
    print("  4. Test it with E2E automation")
    print("  5. Commit the changes")
    print("  6. Update progress files")
    print("  7. Repeat until all features are done")
    print()
    print("Press Ctrl+C to stop at any time")
    print()
    print("="*70)
    print()

    # 创建调度器
    scheduler = Scheduler(
        project_path=project_dir,
        mode="autonomous"
    )

    # 运行
    try:
        result = scheduler.run()

        print()
        print("="*70)
        print("AUTONOMOUS DEVELOPMENT COMPLETE")
        print("="*70)
        print()

        if result["status"] == "completed":
            print("✅ All features successfully completed!")
            print(f"   Total sessions: {result['total_sessions']}")
            print(f"   Features completed: {len(result['completed_features'])}")
        else:
            print(f"Status: {result['status']}")
            print(f"Message: {result.get('message', 'N/A')}")

    except KeyboardInterrupt:
        print()
        print()
        print("="*70)
        print("⏸️  Autonomous development stopped by user")
        print("="*70)
        print()
        print("Progress has been saved. You can:")
        print(f"  1. cd {project_dir}")
        print("  2. Check claude-progress.txt for details")
        print("  3. Run autonomous mode again to continue")
        print()


if __name__ == "__main__":
    main()
