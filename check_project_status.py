#!/usr/bin/env python3
"""
AI Developer System - 项目状态查看工具

通用的项目状态检查脚本，可以用于任何由 AI Developer System 创建的项目
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class ProjectStatusChecker:
    """项目状态检查器"""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path).absolute()
        self.feature_list_path = self.project_path / "feature_list.json"
        self.progress_file_path = self.project_path / "claude-progress.txt"

    def check_project_exists(self) -> bool:
        """检查项目是否存在"""
        if not self.project_path.exists():
            return False
        if not self.feature_list_path.exists():
            return False
        return True

    def print_header(self):
        """打印标题"""
        print("=" * 70)
        print("📊 AI Developer System - 项目状态报告")
        print("=" * 70)
        print()

    def print_overview(self):
        """打印总体概览"""
        print("📈 总体概览")
        print("-" * 70)

        with open(self.feature_list_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        total = len(data['features'])
        completed = [f for f in data['features'] if f.get('passes', False)]
        pending = [f for f in data['features'] if not f.get('passes', False)]
        percentage = len(completed) / total * 100 if total > 0 else 0

        print(f"项目路径: {self.project_path}")
        print(f"项目名称: {data.get('project_name', 'N/A')}")
        print(f"模板类型: {data.get('template', 'N/A')}")
        print(f"总功能数: {total}")
        print(f"✅ 已完成: {len(completed)}")
        print(f"⏳ 待完成: {len(pending)}")
        print(f"📊 完成度: {percentage:.1f}%")
        print(f"🕐 报告时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

    def print_priority_breakdown(self):
        """按优先级分类统计"""
        print("🎯 按优先级分类")
        print("-" * 70)

        with open(self.feature_list_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for priority in ['critical', 'high', 'medium', 'low']:
            features = [f for f in data['features'] if f.get('priority', 'medium') == priority]
            completed_count = len([f for f in features if f.get('passes', False)])
            percentage = (completed_count / len(features) * 100) if features else 0

            # 进度条
            bar_length = 30
            filled = int(bar_length * completed_count / len(features)) if features else 0
            bar = "█" * filled + "░" * (bar_length - filled)

            print(f"{priority.upper():10} [{bar}] {completed_count:2}/{len(features):2} ({percentage:5.1f}%)")

        print()

    def print_completed_features(self, limit: int = 10):
        """打印已完成功能"""
        print("✅ 已完成功能列表")
        print("-" * 70)

        with open(self.feature_list_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        completed = [f for f in data['features'] if f.get('passes', False)]

        if not completed:
            print("暂无已完成的功能")
            print()
            return

        # 显示最近完成的 N 个功能
        for i, f in enumerate(completed[-limit:], 1):
            print(f"{i:2}. [{f['id']}] {f['description']}")
            print(f"    类别: {f.get('category', 'N/A')}")
            print(f"    优先级: {f.get('priority', 'N/A').upper()}")

        if len(completed) > limit:
            print(f"    ... 还有 {len(completed) - limit} 个功能")

        print()

    def print_next_feature(self):
        """打印下一个待实现功能"""
        print("⏳ 下一个待实现功能")
        print("-" * 70)

        with open(self.feature_list_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        completed = [f for f in data['features'] if f.get('passes', False)]
        pending = [f for f in data['features'] if not f.get('passes', False)]

        for f in pending:
            deps = f.get('dependencies', [])
            deps_completed = all(
                any(c.get('id') == dep and c.get('passes', False) for c in completed)
                for dep in deps
            )

            if deps_completed or len(deps) == 0:
                print(f"功能 ID: {f['id']}")
                print(f"描述: {f['description']}")
                print(f"类别: {f.get('category', 'N/A')}")
                print(f"优先级: {f.get('priority', 'N/A').upper()}")

                if deps:
                    print(f"依赖: {', '.join(deps)} (✅ 已满足)")
                else:
                    print(f"依赖: 无")

                if 'verification_step' in f:
                    print(f"验证: {f['verification_step']}")
                print()
                break

    def print_git_status(self):
        """打印 Git 状态"""
        print("🔄 Git 状态")
        print("-" * 70)

        try:
            result = subprocess.run(
                ['git', 'status'],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                print("✅ Git 仓库: 正常")

                # 获取当前分支
                branch_result = subprocess.run(
                    ['git', 'branch', '--show-current'],
                    cwd=self.project_path,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                branch = branch_result.stdout.strip()
                print(f"当前分支: {branch}")

                # 获取最新提交
                log_result = subprocess.run(
                    ['git', 'log', '--oneline', '-5'],
                    cwd=self.project_path,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                print("\n最近提交:")
                print(log_result.stdout)
            else:
                print("❌ 不是 Git 仓库")

        except Exception as e:
            print(f"❌ 无法获取 Git 状态: {e}")

        print()

    def print_process_status(self):
        """打印进程状态"""
        print("💻 后台进程状态")
        print("-" * 70)

        try:
            result = subprocess.run(
                ['ps', 'aux'],
                capture_output=True,
                text=True,
                timeout=5
            )

            lines = result.stdout.split('\n')
            found = False

            for line in lines:
                if 'orchestrator.scheduler' in line and self.project_path.as_posix() in line:
                    found = True
                    parts = line.split()
                    if len(parts) >= 8:
                        print(f"✅ 自主开发进程正在运行")
                        print(f"   进程 ID: {parts[1]}")
                        print(f"   CPU 使用: {parts[2]}")
                        print(f"   内存使用: {parts[3]}")
                        print(f"   运行时间: {parts[9] if len(parts) > 9 else 'N/A'}")
                    break

            if not found:
                print("ℹ️  自主开发进程: 未运行")

        except Exception as e:
            print(f"❌ 无法检查进程状态: {e}")

        print()

    def print_progress_summary(self):
        """打印进度摘要"""
        print("📊 进度摘要")
        print("-" * 70)

        with open(self.feature_list_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        total = len(data['features'])
        completed = [f for f in data['features'] if f.get('passes', False)]
        remaining = total - len(completed)

        avg_time = 2.5
        estimated_minutes = remaining * avg_time
        hours = int(estimated_minutes // 60)
        minutes = int(estimated_minutes % 60)

        print(f"剩余功能数: {remaining}")
        print(f"平均速度: {avg_time} 分钟/功能")
        print(f"预计剩余时间: 约 {hours} 小时 {minutes} 分钟")

        if len(completed) > 0:
            print(f"\n首个功能: {completed[0]['id']}")
            print(f"最新功能: {completed[-1]['id']}")

        print()

    def print_recent_activity(self):
        """打印最近活动"""
        print("🕒 最近活动")
        print("-" * 70)

        if not self.progress_file_path.exists():
            print("进度文件不存在")
            print()
            return

        with open(self.progress_file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取最近的会话记录
        sessions = content.split('[Session')
        recent_sessions = sessions[-3:] if len(sessions) > 1 else sessions

        for session in reversed(recent_sessions):
            if not session.strip():
                continue

            lines = session.strip().split('\n')
            if len(lines) > 0:
                print(f"\n{lines[0] if lines else ''}")

                # 提取关键信息
                for line in lines[1:8]:
                    if line.startswith('Feature:') or line.startswith('Status:') or line.startswith('Description:'):
                        print(f"  {line}")

        print()

    def run(self, detailed: bool = True):
        """运行完整的状态检查"""
        self.print_header()
        self.print_overview()
        self.print_priority_breakdown()

        if detailed:
            self.print_completed_features(limit=10)
            self.print_next_feature()
            self.print_git_status()
            self.print_process_status()
            self.print_progress_summary()
            self.print_recent_activity()
        else:
            self.print_completed_features(limit=5)
            self.print_next_feature()

        print("=" * 70)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="查看 AI Developer System 项目的开发状态"
    )
    parser.add_argument(
        'project',
        nargs='?',
        default='.',
        help='项目目录路径（默认为当前目录）'
    )
    parser.add_argument(
        '--simple',
        action='store_true',
        help='简化输出（只显示关键信息）'
    )

    args = parser.parse_args()

    # 创建检查器
    checker = ProjectStatusChecker(args.project)

    # 检查项目是否存在
    if not checker.check_project_exists():
        print(f"❌ 错误: 项目不存在或 feature_list.json 缺失")
        print(f"   路径: {args.project}")
        sys.exit(1)

    # 运行检查
    checker.run(detailed=not args.simple)


if __name__ == "__main__":
    main()
