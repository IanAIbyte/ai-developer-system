"""
Scheduler - 调度器

职责：
1. 管理 Initializer Agent 和 Coding Agent 的切换
2. 监控会话状态
3. 处理错误和重试
4. 提供自主运行模式

这是整个系统的"大脑"，决定何时运行哪个代理。
"""

import json
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import argparse

from .initializer_agent import InitializerAgent
from .coding_agent import CodingAgent


class Scheduler:
    """调度器 - 多代理编排器"""

    def __init__(self, project_path: str, mode: str = "manual"):
        """
        调度器

        Args:
            project_path: 项目路径
            mode: 运行模式
                - manual: 手动模式（一次会话）
                - autonomous: 自主模式（持续运行直到完成）
                - single-feature: 单功能模式（完成一个功能后停止）
        """
        self.project_path = Path(project_path).absolute()
        self.mode = mode
        self.session_count = 0

    def run(self) -> Dict:
        """
        运行调度流程

        Returns:
            总体结果字典
        """
        print(f"\n{'='*70}")
        print(f"AI Developer System - Scheduler")
        print(f"Mode: {self.mode}")
        print(f"Project: {self.project_path}")
        print(f"{'='*70}\n")

        # 检查项目状态
        project_status = self._check_project_status()

        if project_status["needs_initialization"]:
            # 阶段 1: 运行 Initializer Agent
            print("📍 Phase: INITIALIZATION")
            print("→ Running Initializer Agent...\n")

            init_result = self._run_initializer_agent()

            if not init_result["status"] == "success":
                return {
                    "status": "failed",
                    "phase": "initialization",
                    "error": init_result.get("error")
                }

            print(f"\n✅ Initialization complete!")
            print(f"   Features generated: {init_result['feature_count']}")
            print(f"   Ready for coding agent\n")
        else:
            print(f"📍 Phase: DEVELOPMENT")
            print(f"   Project already initialized")
            print(f"   Total features: {project_status['total_features']}")
            print(f"   Completed: {project_status['completed_features']}")
            print(f"   Pending: {project_status['pending_features']}\n")

        # 阶段 2: 运行 Coding Agent（根据模式）
        if self.mode == "manual":
            return self._run_single_session()

        elif self.mode == "single-feature":
            return self._run_single_feature()

        elif self.mode == "autonomous":
            return self._run_autonomous_loop()

        else:
            return {
                "status": "error",
                "error": f"Unknown mode: {self.mode}"
            }

    def _check_project_status(self) -> Dict:
        """
        检查项目状态

        Returns:
            {
                "needs_initialization": bool,
                "total_features": int,
                "completed_features": int,
                "pending_features": int
            }
        """
        # 检查 feature_list.json 是否存在
        feature_list_path = self.project_path / "feature_list.json"

        if not feature_list_path.exists():
            return {
                "needs_initialization": True,
                "total_features": 0,
                "completed_features": 0,
                "pending_features": 0
            }

        # 读取功能列表
        with open(feature_list_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        total = len(data["features"])
        completed = sum(1 for f in data["features"] if f.get("passes", False))

        return {
            "needs_initialization": False,
            "total_features": total,
            "completed_features": completed,
            "pending_features": total - completed
        }

    def _run_initializer_agent(self) -> Dict:
        """运行初始化代理"""
        # 读取用户提示（如果有）
        prompt_path = self.project_path / "user_prompt.txt"

        if not prompt_path.exists():
            return {
                "status": "error",
                "error": "user_prompt.txt not found. Please create it with your requirements."
            }

        with open(prompt_path, 'r', encoding='utf-8') as f:
            user_prompt = f.read()

        # 运行 Initializer Agent
        initializer = InitializerAgent(
            project_path=str(self.project_path),
            user_prompt=user_prompt,
            template="webapp"  # TODO: 从配置读取
        )

        return initializer.initialize()

    def _run_single_session(self) -> Dict:
        """运行单个会话（手动模式）"""
        print("📍 Running single coding session...\n")

        coding_agent = CodingAgent(project_path=str(self.project_path))
        result = coding_agent.start_session()

        return {
            "status": "completed",
            "mode": "manual",
            "session_result": result
        }

    def _run_single_feature(self) -> Dict:
        """运行单功能模式"""
        print("📍 Running until one feature is complete...\n")

        session_count = 0
        max_sessions = 5  # 防止无限循环

        while session_count < max_sessions:
            coding_agent = CodingAgent(project_path=str(self.project_path))
            result = coding_agent.start_session()
            session_count += 1

            if result["status"] == "completed":
                # 所有功能完成
                return {
                    "status": "completed",
                    "mode": "single-feature",
                    "message": "All features completed",
                    "sessions_run": session_count
                }

            if result["status"] == "success" and result.get("test_passed"):
                # 功能成功完成
                return {
                    "status": "completed",
                    "mode": "single-feature",
                    "feature_completed": result["feature"],
                    "sessions_run": session_count
                }

            # 功能失败，继续尝试
            print(f"\n⚠️  Feature not complete, retrying... ({session_count}/{max_sessions})\n")

        return {
            "status": "timeout",
            "mode": "single-feature",
            "message": f"Max sessions ({max_sessions}) reached without completion"
        }

    def _run_autonomous_loop(self) -> Dict:
        """
        运行自主循环模式

        持续运行会话，直到：
        1. 所有功能完成
        2. 达到最大会话数
        3. 发生严重错误
        """
        print("📍 Running autonomous development loop...")
        print("   Will continue until all features are complete\n")

        session_count = 0
        max_sessions = 1000  # 安全限制
        completed_features = []

        while session_count < max_sessions:
            print(f"\n{'#'*70}")
            print(f"# Autonomous Session #{session_count + 1}")
            print(f"{'#'*70}\n")

            coding_agent = CodingAgent(project_path=str(self.project_path))
            result = coding_agent.start_session()
            session_count += 1
            self.session_count = session_count

            if result["status"] == "completed":
                # 所有功能完成
                print("\n" + "="*70)
                print("🎉 ALL FEATURES COMPLETED!")
                print("="*70)
                return {
                    "status": "completed",
                    "mode": "autonomous",
                    "total_sessions": session_count,
                    "completed_features": completed_features
                }

            if result["status"] == "success":
                feature_id = result["feature"]
                if result.get("test_passed"):
                    completed_features.append(feature_id)
                    print(f"\n✅ Feature {feature_id} completed and tested")

                    # 更新进度
                    status = self._check_project_status()
                    print(f"   Progress: {status['completed_features']}/{status['total_features']} features")

                    if status["pending_features"] == 0:
                        print("\n🎉 ALL FEATURES COMPLETED!")
                        return {
                            "status": "completed",
                            "mode": "autonomous",
                            "total_sessions": session_count,
                            "completed_features": completed_features
                        }
                else:
                    print(f"\n⚠️  Feature {feature_id} implemented but tests failed")
                    print(f"   Will retry in next session")

            elif result["status"] == "failed":
                print(f"\n❌ Session failed: {result.get('error')}")
                print(f"   Continuing to next session...")

            # 短暂暂停（让用户看到输出）
            if session_count < max_sessions:
                print(f"\n⏸️  Pausing briefly before next session...")
                time.sleep(2)

        return {
            "status": "timeout",
            "mode": "autonomous",
            "message": f"Max sessions ({max_sessions}) reached",
            "total_sessions": session_count,
            "completed_features": completed_features
        }


# CLI 接口
def main():
    parser = argparse.ArgumentParser(
        description="AI Developer System - Scheduler",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Manual mode (single session)
  python scheduler.py --project ./my-project --mode manual

  # Single feature mode (stop after first feature)
  python scheduler.py --project ./my-project --mode single-feature

  # Autonomous mode (continue until all features done)
  python scheduler.py --project ./my-project --mode autonomous
        """
    )

    parser.add_argument(
        "--project",
        required=True,
        help="Project directory path"
    )
    parser.add_argument(
        "--mode",
        choices=["manual", "single-feature", "autonomous"],
        default="manual",
        help="Operation mode"
    )

    args = parser.parse_args()

    scheduler = Scheduler(
        project_path=args.project,
        mode=args.mode
    )

    result = scheduler.run()

    print("\n" + "="*70)
    print("FINAL RESULT")
    print("="*70)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
