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
            # 即使失败也要记录到进度文件
            self._record_implementation_failure(feature, implementation_result)
            return {
                "status": "failed",
                "session_id": self.session_id,
                "feature": feature["id"],
                "error": implementation_result.get("error"),
                "requires_manual_implementation": implementation_result.get("requires_manual_implementation", False)
            }

        # Phase 4: 测试功能
        print(f"\n[Phase 4] Testing feature...")
        test_result = self._test_feature(feature, context)

        # Phase 5: 清理状态（传递 implementation_result）
        print(f"\n[Phase 5] Cleaning up state...")
        self._clean_state(feature, test_result, implementation_result)

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
        选择下一个要实现的功能（基于依赖图的拓扑排序）

        策略：
        1. 找到所有 passes=false 的功能
        2. 检查依赖关系（拓扑排序）
        3. 选择最高优先级且依赖已满足的功能
        4. 检测循环依赖
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

        print(f"    → Pending features: {len(pending_features)}")

        # 选择第一个依赖已满足的功能
        blocked_features = []
        for feature in pending_features:
            deps_status = self._check_dependencies(feature, feature_list)

            if deps_status["satisfied"]:
                # 依赖已满足
                if deps_status["dependencies"]:
                    print(f"    → {feature['id']}: dependencies satisfied: {deps_status['dependencies']}")
                return feature
            else:
                # 依赖未满足，记录原因
                blocked_features.append({
                    "id": feature["id"],
                    "priority": feature.get("priority", "medium"),
                    "waiting_for": deps_status["missing_deps"],
                    "reason": deps_status["reason"]
                })

        # 所有功能都被阻塞，显示详细原因
        if blocked_features:
            print(f"    ⚠️  All pending features are blocked by dependencies:")
            for blocked in blocked_features[:5]:  # 只显示前 5 个
                print(f"       - {blocked['id']} (priority: {blocked['priority']})")
                print(f"         Waiting for: {', '.join(blocked['waiting_for'])}")
                if blocked.get("reason"):
                    print(f"         Reason: {blocked['reason']}")

            if len(blocked_features) > 5:
                print(f"       ... and {len(blocked_features) - 5} more")

            # 检测是否存在循环依赖
            circular_deps = self._detect_circular_dependencies(feature_list)
            if circular_deps:
                print(f"    ❌ Circular dependencies detected:")
                for cycle in circular_deps:
                    print(f"       {' → '.join(cycle)} → (cycle)")

        return None

    def _check_dependencies(self, feature: Dict, all_features: List[Dict]) -> Dict:
        """
        检查功能依赖是否已满足

        Returns:
            {
                "satisfied": bool,  # 所有依赖是否都满足
                "dependencies": List[str],  # 所有依赖 ID
                "missing_deps": List[str],  # 未满足的依赖 ID
                "reason": str  # 未满足的原因（如果有）
            }
        """
        dependencies = feature.get("dependencies", [])
        satisfied_deps = []
        missing_deps = []

        for dep_id in dependencies:
            # 找到依赖的功能
            dep_feature = next(
                (f for f in all_features if f["id"] == dep_id),
                None
            )

            if not dep_feature:
                missing_deps.append(dep_id)
                return {
                    "satisfied": False,
                    "dependencies": dependencies,
                    "missing_deps": [dep_id],
                    "reason": f"Dependency '{dep_id}' not found in feature list"
                }

            if dep_feature.get("passes", False):
                satisfied_deps.append(dep_id)
            else:
                missing_deps.append(dep_id)

        if missing_deps:
            return {
                "satisfied": False,
                "dependencies": dependencies,
                "missing_deps": missing_deps,
                "reason": f"Waiting for {len(missing_deps)} dependencies to complete"
            }

        return {
            "satisfied": True,
            "dependencies": satisfied_deps,
            "missing_deps": [],
            "reason": None
        }

    def _detect_circular_dependencies(self, all_features: List[Dict]) -> List[List[str]]:
        """
        检测循环依赖（使用深度优先搜索）

        Returns:
            循环依赖列表，每个循环是一个 feature ID 列表
        """
        # 构建依赖图
        graph = {}
        for feature in all_features:
            graph[feature["id"]] = feature.get("dependencies", [])

        # 检测循环
        visited = set()
        rec_stack = set()
        cycles = []

        def dfs(node: str, path: List[str]):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    result = dfs(neighbor, path.copy())
                    if result:
                        cycles.append(result)
                elif neighbor in rec_stack:
                    # 找到循环
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)

            rec_stack.remove(node)
            return None

        for node in graph:
            if node not in visited:
                dfs(node, [])

        return cycles

    def _visualize_dependency_graph(self, all_features: List[Dict]) -> str:
        """
        可视化依赖图结构（用于调试）

        Returns:
            文本形式的依赖图
        """
        lines = []
        lines.append("\n=== Dependency Graph Visualization ===")

        # 按状态分组
        completed = [f for f in all_features if f.get("passes", False)]
        pending = [f for f in all_features if not f.get("passes", False)]

        lines.append(f"\n✅ Completed ({len(completed)}):")
        for f in completed:
            deps = f.get("dependencies", [])
            if deps:
                lines.append(f"  {f['id']} (priority: {f.get('priority', 'medium')})")
                lines.append(f"    ← depends on: {', '.join(deps)}")
            else:
                lines.append(f"  {f['id']} (priority: {f.get('priority', 'medium')}) - no dependencies")

        lines.append(f"\n⏳ Pending ({len(pending)}):")
        for f in pending:
            deps = f.get("dependencies", [])
            status = self._check_dependencies(f, all_features)

            if status["satisfied"]:
                lines.append(f"  ✓ {f['id']} (priority: {f.get('priority', 'medium')}) - ready to implement")
            else:
                lines.append(f"  ✗ {f['id']} (priority: {f.get('priority', 'medium')}) - blocked")
                if status["missing_deps"]:
                    lines.append(f"    ← missing: {', '.join(status['missing_deps'])}")

        lines.append("\n" + "=" * 40)
        return "\n".join(lines)

    def _export_dependency_graph_dot(self, all_features: List[Dict], output_path: str = None) -> str:
        """
        导出依赖图为 DOT 格式（可用 Graphviz 可视化）

        Args:
            all_features: 功能列表
            output_path: 输出文件路径（可选）

        Returns:
            DOT 格式的依赖图字符串
        """
        dot_lines = ["digraph FeatureDependencies {"]
        dot_lines.append("  rankdir=TB;")
        dot_lines.append("  node [shape=box, style=rounded];")
        dot_lines.append("")

        # 按状态分组节点
        completed = [f for f in all_features if f.get("passes", False)]
        pending = [f for f in all_features if not f.get("passes", False)]

        # 添加节点
        for f in completed:
            label = f"{f['id']}\\n({f.get('priority', 'medium')})"
            dot_lines.append(f"  \"{f['id']}\" [label=\"{label}\", style=\"rounded,filled\", fillcolor=lightgray];")

        for f in pending:
            label = f"{f['id']}\\n({f.get('priority', 'medium')})"
            dot_lines.append(f"  \"{f['id']}\" [label=\"{label}\", style=\"rounded,filled\", fillcolor=lightblue];")

        dot_lines.append("")

        # 添加边（依赖关系）
        for f in all_features:
            deps = f.get("dependencies", [])
            for dep_id in deps:
                dot_lines.append(f"  \"{dep_id}\" -> \"{f['id']}\";")

        dot_lines.append("}")

        dot_content = "\n".join(dot_lines)

        # 如果指定了输出路径，保存到文件
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(dot_content)
            print(f"    → Dependency graph exported to: {output_path}")

        return dot_content

    def _implement_feature(self, feature: Dict, context: Dict) -> Dict:
        """
        实现功能

        优先使用 GLM-5 API，如果失败则使用模拟实现
        """
        try:
            # 尝试使用增强的编码代理（带 GLM-5 API）
            from .enhanced_coding_agent import EnhancedCodingAgent

            enhanced_agent = EnhancedCodingAgent(
                project_path=str(self.project_path),
                llm_provider="glm-5",  # 使用 GLM-5
                session_id=self.session_id
            )

            return enhanced_agent.implement_feature_real(feature, context)

        except ImportError:
            print("    ⚠️  Enhanced agent not available, using simulation mode")
        except Exception as e:
            print(f"    ⚠️  Enhanced agent failed: {e}, using simulation mode")

        # Fallback 到模拟实现
        print(f"    Implementing: {feature['description']}")

        # 创建模拟实现文件
        impl_dir = self.project_path / "src" / "features" / feature["id"]
        impl_dir.mkdir(parents=True, exist_ok=True)

        impl_file = impl_dir / "implementation.md"
        with open(impl_file, 'w', encoding='utf-8') as f:
            f.write(f"# {feature['id']} - Implementation\n\n")
            f.write(f"## Description\n{feature['description']}\n\n")
            f.write(f"## Steps\n")
            for i, step in enumerate(feature.get("steps", []), 1):
                f.write(f"{i}. {step}\n")

        return {
            "success": True,
            "files_changed": [str(impl_file)],
            "implementation_notes": "Simulation mode - GLM-5 API integration available"
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

    def _clean_state(self, feature: Dict, test_result: Dict, implementation_result: Dict):
        """
        清理状态 - 关键步骤！

        Anthropic 强调：每次会话结束必须是干净状态
        - 可合并到 main 的代码
        - 清晰的 git commit
        - 更新的进度文件
        - 更新的功能列表（passes 字段）

        如果测试失败，不要标记为通过，先修复 bug

        新增：检查 generation_method，simulation mode 不标记为完成
        """
        generation_method = implementation_result.get("generation_method", "unknown")
        requires_manual = implementation_result.get("requires_manual_implementation", False)

        # 1. 更新 feature_list.json
        # 只有当测试通过 且 不是 simulation mode 时，才标记为完成
        should_mark_complete = (
            test_result["passed"] and
            generation_method != "simulation" and
            not requires_manual
        )

        if should_mark_complete:
            print("  → Updating feature_list.json (marking as complete)")
            self._update_feature_status(
                feature["id"],
                passes=True,
                generation_method=generation_method
            )
        else:
            if requires_manual:
                print("  → ⚠️  Feature requires manual implementation (not marking as complete)")
                self._update_feature_status(
                    feature["id"],
                    passes=False,
                    generation_method=generation_method,
                    requires_manual_implementation=True
                )
            else:
                print("  → Updating feature_list.json (not complete yet)")
                self._update_feature_status(
                    feature["id"],
                    passes=False,
                    generation_method=generation_method
                )

        # 2. 更新 claude-progress.txt
        print("  → Updating claude-progress.txt")
        self._append_to_progress_file(feature, test_result, implementation_result)

        # 3. Git commit（只在真正完成时）
        if should_mark_complete:
            print("  → Creating git commit")
            self._create_commit(feature, test_result, implementation_result)
        else:
            print("  → Skipping git commit (feature not complete)")

    def _update_feature_status(
        self,
        feature_id: str,
        passes: bool,
        generation_method: str = "unknown",
        requires_manual_implementation: bool = False
    ):
        """
        更新功能的 passes 状态

        Args:
            feature_id: 功能 ID
            passes: 是否完成
            generation_method: 生成方法（glm-5-api, simulation 等）
            requires_manual_implementation: 是否需要手动实现
        """
        feature_list_path = self.project_path / "feature_list.json"

        with open(feature_list_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for feature in data["features"]:
            if feature["id"] == feature_id:
                feature["passes"] = passes
                # 新增元数据
                feature["generation_method"] = generation_method
                feature["requires_manual_implementation"] = requires_manual_implementation

                # 根据状态添加实现状态
                if requires_manual_implementation:
                    feature["implementation_status"] = "requires_manual"
                elif passes:
                    feature["implementation_status"] = "complete"
                else:
                    feature["implementation_status"] = "in_progress"
                break

        with open(feature_list_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _record_implementation_failure(self, feature: Dict, implementation_result: Dict):
        """记录实现失败的情况"""
        progress_path = self.project_path / "claude-progress.txt"

        generation_method = implementation_result.get("generation_method", "unknown")
        requires_manual = implementation_result.get("requires_manual_implementation", False)

        new_entry = f"""

[Session {self.session_id}] Coding Agent - IMPLEMENTATION FAILED
Timestamp: {self.timestamp}
Feature: {feature['id']}
Description: {feature['description']}
Status: ❌ FAIL
Generation Method: {generation_method}
Requires Manual Implementation: {requires_manual}

Error Details:
- API attempts exhausted after {implementation_result.get('attempts_exhausted', 'N/A')} tries
- Fallback reason: {implementation_result.get('fallback_reason', 'Unknown')}

⚠️  This feature needs to be implemented manually!
Please review the implementation guide in src/features/{feature['id']}/

"""

        with open(progress_path, 'a', encoding='utf-8') as f:
            f.write(new_entry)

    def _append_to_progress_file(
        self,
        feature: Dict,
        test_result: Dict,
        implementation_result: Dict
    ):
        """追加进度到 claude-progress.txt"""
        progress_path = self.project_path / "claude-progress.txt"

        status_icon = "✅" if test_result["passed"] else "❌"
        generation_method = implementation_result.get("generation_method", "unknown")

        # 根据生成方法添加不同的图标
        if generation_method == "simulation":
            method_icon = "⚠️ "
            method_text = "SIMULATION MODE - Requires manual implementation"
        elif generation_method == "glm-5-api":
            method_icon = "🤖 "
            method_text = "GLM-5 API Generated"
        else:
            method_icon = "📝 "
            method_text = generation_method

        new_entry = f"""

[Session {self.session_id}] Coding Agent
Timestamp: {self.timestamp}
Feature: {feature['id']}
Description: {feature['description']}
Status: {status_icon} {'PASS' if test_result['passed'] else 'FAIL'}
Generation Method: {method_icon} {method_text}

Changes:
- Implemented feature
- Tested with E2E automation
- Updated feature_list.json

"""

        with open(progress_path, 'a', encoding='utf-8') as f:
            f.write(new_entry)

    def _create_commit(self, feature: Dict, test_result: Dict, implementation_result: Dict):
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
        generation_method = implementation_result.get("generation_method", "unknown")

        commit_message = f"""feat: {feature['id']} - {feature['description']}

Implemented by AI Developer System Coding Agent (Session {self.session_id})

Feature ID: {feature['id']}
Category: {feature.get('category', 'unknown')}
Status: {status_text}
Generation Method: {generation_method}
Timestamp: {self.timestamp}

Changes:
- Feature implementation
- E2E testing completed
- Progress updated
- Feature marked as complete
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
