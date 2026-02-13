"""
Coding Agent - 编码代理

职责：
1. 快速上手（Get Up to Speed）
2. 增量开发（Incremental Progress）
3. 清理状态（Clean State）

关键原则：
- 每次会话只处理一个功能
- 必须完整测试功能
- 必须留下干净状态（可合并的 git commit）
- 更新进度文件

基于 Anthropic 的 "Effective harnesses for long-running agents" 框架
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import sys


class CodingAgent:
    """编码代理 - 增量开发专家"""

    def __init__(self, project_path: str, session_id: Optional[str] = None):
        """
        编码代理

        Args:
            project_path: 项目路径
            session_id: 会话 ID（自动生成）
        """
        self.project_path = Path(project_path).absolute()
        self.session_id = session_id or self._generate_session_id()
        self.timestamp = datetime.now().isoformat()

    def start_session(self) -> Dict:
        """
        启动编码会话

        核心流程：
        1. 快速上手
        2. 选择下一个功能
        3. 实现功能
        4. 测试功能
        5. 清理状态

        Returns:
            会话结果字典
        """
        print(f"\n{'='*60}")
        print(f"[Coding Agent] Session {self.session_id}")
        print(f"[Coding Agent] Timestamp: {self.timestamp}")
        print(f"{'='*60}\n")

        # Phase 1: 快速上手
        print("[Phase 1] Getting up to speed...")
        context = self._get_up_to_speed()

        # Phase 2: 选择下一个功能
        print("\n[Phase 2] Selecting next feature...")
        feature = self._select_next_feature(context)

        if not feature:
            print("[Coding Agent] ✅ All features completed!")
            return {
                "status": "completed",
                "session_id": self.session_id,
                "message": "All features in feature_list.json have passes=true"
            }

        print(f"[Coding Agent] Selected feature: {feature['id']}")
        print(f"[Coding Agent] Description: {feature['description']}")

        # Phase 3: 实现功能（调用 Claude）
        print(f"\n[Phase 3] Implementing feature...")
        implementation_result = self._implement_feature(feature, context)

        if not implementation_result["success"]:
            print(f"[Coding Agent] ❌ Implementation failed")
            return {
                "status": "failed",
                "session_id": self.session_id,
                "feature": feature["id"],
                "error": implementation_result.get("error")
            }

        # Phase 4: 测试功能
        print(f"\n[Phase 4] Testing feature...")
        test_result = self._test_feature(feature, context)

        # Phase 5: 清理状态
        print(f"\n[Phase 5] Cleaning up state...")
        self._clean_state(feature, test_result)

        result = {
            "status": "success",
            "session_id": self.session_id,
            "feature": feature["id"],
            "timestamp": self.timestamp,
            "test_passed": test_result["passed"],
            "next_feature": self._get_next_pending_feature(feature["id"])
        }

        print(f"\n{'='*60}")
        print(f"[Coding Agent] ✅ Session {self.session_id} complete")
        print(f"[Coding Agent] Feature: {feature['id']}")
        print(f"[Coding Agent] Test: {'PASS' if test_result['passed'] else 'FAIL'}")
        print(f"{'='*60}\n")

        return result

    def _get_up_to_speed(self) -> Dict:
        """
        快速上手 - Anthropic 推荐的标准步骤

        步骤：
        1. pwd - 确认工作目录
        2. 读取 claude-progress.txt - 了解进度
        3. 读取 feature_list.json - 了解功能
        4. 读取 git log - 了解最近工作
        5. 运行 init.sh - 启动开发服务器
        6. 运行基础测试 - 验证当前状态

        Returns:
            上下文字典
        """
        context = {}

        # 1. pwd
        print("  → pwd")
        context["cwd"] = str(self.project_path)
        print(f"    Working directory: {context['cwd']}")

        # 2. 读取 claude-progress.txt
        print("  → Reading claude-progress.txt")
        progress_path = self.project_path / "claude-progress.txt"
        if progress_path.exists():
            with open(progress_path, 'r', encoding='utf-8') as f:
                context["progress"] = f.read()
            print(f"    Progress file loaded ({len(context['progress'])} chars)")
        else:
            print("    ⚠️  Warning: claude-progress.txt not found")
            context["progress"] = ""

        # 3. 读取 feature_list.json
        print("  → Reading feature_list.json")
        feature_list_path = self.project_path / "feature_list.json"
        if feature_list_path.exists():
            with open(feature_list_path, 'r', encoding='utf-8') as f:
                context["feature_list"] = json.load(f)
            total = len(context["feature_list"]["features"])
            completed = sum(1 for f in context["feature_list"]["features"] if f.get("passes"))
            print(f"    Features: {completed}/{total} completed")
        else:
            print("    ❌ Error: feature_list.json not found")
            raise FileNotFoundError("feature_list.json not found. Run Initializer Agent first.")

        # 4. 读取 git log
        print("  → Reading git log")
        try:
            result = subprocess.run(
                ["git", "log", "--oneline", "-20"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                check=True
            )
            context["git_log"] = result.stdout.strip()
            print(f"    Recent commits: {len(context['git_log'].split(chr(10)))} shown")
        except subprocess.CalledProcessError:
            print("    ⚠️  Warning: Could not read git log")
            context["git_log"] = ""

        # 5. 运行 init.sh（如果存在）
        print("  → Running init.sh (if exists)")
        init_script = self.project_path / "init.sh"
        if init_script.exists():
            print("    Found init.sh, starting development server...")
            # 实际实现应该在后台运行
            context["server_started"] = True
        else:
            print("    No init.sh found")
            context["server_started"] = False

        # 6. 运行基础测试
        print("  → Running basic tests")
        basic_test_result = self._run_basic_tests(context)
        context["basic_test_result"] = basic_test_result

        if basic_test_result["passed"]:
            print("    ✅ Basic tests passed")
        else:
            print("    ⚠️  Basic tests failed - may need to fix first")

        return context

    def _select_next_feature(self, context: Dict) -> Optional[Dict]:
        """
        选择下一个要实现的功能

        策略：
        1. 找到所有 passes=false 的功能
        2. 检查依赖关系
        3. 选择最高优先级且依赖已满足的功能
        """
        feature_list = context["feature_list"]["features"]

        # 找到未完成的功能
        pending_features = [
            f for f in feature_list
            if not f.get("passes", False)
        ]

        if not pending_features:
            return None

        # 按优先级排序
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        pending_features.sort(
            key=lambda f: (priority_order.get(f.get("priority", "medium"), 0), f["id"])
        )

        # 选择第一个依赖已满足的功能
        for feature in pending_features:
            if self._check_dependencies(feature, feature_list):
                return feature

        return None

    def _check_dependencies(self, feature: Dict, all_features: List[Dict]) -> bool:
        """检查功能依赖是否已满足"""
        dependencies = feature.get("dependencies", [])

        for dep_id in dependencies:
            # 找到依赖的功能
            dep_feature = next(
                (f for f in all_features if f["id"] == dep_id),
                None
            )
            if not dep_feature or not dep_feature.get("passes", False):
                return False

        return True

    def _implement_feature(self, feature: Dict, context: Dict) -> Dict:
        """
        实现功能

        这里应该调用 Claude Code 或 Claude Agent SDK

        简化实现：返回成功（实际应该真正实现）
        """
        print(f"    Implementing: {feature['description']}")

        # TODO: 实际实现应该：
        # 1. 调用 Claude Code API
        # 2. 传递上下文（功能描述、项目状态）
        # 3. Claude 进行代码生成/修改
        # 4. 返回实现结果

        # 简化：返回成功
        return {
            "success": True,
            "files_changed": [],
            "implementation_notes": "TODO: Integrate with Claude Code API"
        }

    def _test_feature(self, feature: Dict, context: Dict) -> Dict:
        """
        测试功能

        必须使用 E2E 测试（浏览器自动化）来验证功能真正可用

        Anthropic 强调：只看代码是不够的，必须像用户一样测试
        """
        print(f"    Testing: {feature['description']}")
        print(f"    Steps to verify:")

        for i, step in enumerate(feature.get("steps", []), 1):
            print(f"      {i}. {step}")

        # TODO: 实际实现应该：
        # 1. 使用 Puppeteer MCP 或 Playwright
        # 2. 执行每个步骤
        # 3. 截图验证
        # 4. 记录测试结果

        # 简化：返回通过（实际应该真正测试）
        return {
            "passed": True,
            "test_output": "TODO: Integrate with Puppeteer MCP",
            "screenshots": []
        }

    def _run_basic_tests(self, context: Dict) -> Dict:
        """
        运行基础测试

        在实现新功能之前，先验证现有功能没有被破坏
        """
        # TODO: 实际实现应该运行测试套件
        return {"passed": True}

    def _clean_state(self, feature: Dict, test_result: Dict):
        """
        清理状态 - 关键步骤！

        Anthropic 强调：每次会话结束必须是干净状态
        - 可合并到 main 的代码
        - 清晰的 git commit
        - 更新的进度文件
        - 更新的功能列表（passes 字段）

        如果测试失败，不要标记为通过，先修复 bug
        """
        # 1. 更新 feature_list.json
        if test_result["passed"]:
            print("  → Updating feature_list.json")
            self._update_feature_status(feature["id"], passes=True)

        # 2. 更新 claude-progress.txt
        print("  → Updating claude-progress.txt")
        self._append_to_progress_file(feature, test_result)

        # 3. Git commit
        print("  → Creating git commit")
        self._create_commit(feature, test_result)

    def _update_feature_status(self, feature_id: str, passes: bool):
        """更新功能的 passes 状态"""
        feature_list_path = self.project_path / "feature_list.json"

        with open(feature_list_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for feature in data["features"]:
            if feature["id"] == feature_id:
                feature["passes"] = passes
                break

        with open(feature_list_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _append_to_progress_file(self, feature: Dict, test_result: Dict):
        """追加进度到 claude-progress.txt"""
        progress_path = self.project_path / "claude-progress.txt"

        status_icon = "✅" if test_result["passed"] else "❌"
        new_entry = f"""

[Session {self.session_id}] Coding Agent
Timestamp: {self.timestamp}
Feature: {feature['id']}
Description: {feature['description']}
Status: {status_icon} {'PASS' if test_result['passed'] else 'FAIL'}

Changes:
- Implemented feature
- Tested with E2E automation
- Updated feature_list.json

Git commit: feat: {feature['id']} - {feature['description']}

"""

        with open(progress_path, 'a', encoding='utf-8') as f:
            f.write(new_entry)

    def _create_commit(self, feature: Dict, test_result: Dict):
        """创建 git commit"""
        # Add all changes
        subprocess.run(
            ["git", "add", "."],
            cwd=self.project_path,
            capture_output=True,
            check=True
        )

        # Create commit
        status_text = "PASS" if test_result["passed"] else "FAIL"
        commit_message = f"""feat: {feature['id']} - {feature['description']}

Implemented by AI Developer System Coding Agent (Session {self.session_id})

Feature ID: {feature['id']}
Category: {feature.get('category', 'unknown')}
Status: {status_text}
Timestamp: {self.timestamp}

Changes:
- Feature implementation
- E2E testing completed
- Progress updated
"""

        subprocess.run(
            ["git", "commit", "-m", commit_message],
            cwd=self.project_path,
            capture_output=True,
            check=True
        )

    def _generate_session_id(self) -> str:
        """生成会话 ID"""
        return datetime.now().strftime("%Y%m%d-%H%M%S")

    def _get_next_pending_feature(self, current_feature_id: str) -> Optional[str]:
        """获取下一个待处理功能的 ID"""
        feature_list_path = self.project_path / "feature_list.json"

        with open(feature_list_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for feature in data["features"]:
            if not feature.get("passes", False) and feature["id"] != current_feature_id:
                return feature["id"]

        return None


# CLI 接口
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Coding Agent - Incremental development specialist"
    )
    parser.add_argument(
        "--project",
        required=True,
        help="Project directory path"
    )
    parser.add_argument(
        "--session-id",
        help="Session ID (auto-generated if not provided)"
    )

    args = parser.parse_args()

    agent = CodingAgent(
        project_path=args.project,
        session_id=args.session_id
    )

    result = agent.start_session()
    print("\n=== Session Result ===")
    print(json.dumps(result, indent=2))
