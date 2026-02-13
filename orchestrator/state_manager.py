"""
State Manager - 状态管理器

职责：
1. 管理会话状态
2. 创建检查点
3. 状态恢复
4. 监控进度指标

支持：
- 会话恢复（崩溃后继续）
- 检查点管理（回滚到之前状态）
- 进度可视化
"""

import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import hashlib


class StateManager:
    """状态管理器 - 会话状态持久化专家"""

    def __init__(self, project_path: str):
        """
        状态管理器

        Args:
            project_path: 项目路径
        """
        self.project_path = Path(project_path).absolute()
        self.checkpoints_dir = self.project_path / ".claude" / "checkpoints"
        self.state_file = self.project_path / ".claude" / "state.json"

    def save_checkpoint(self, session_id: str, description: str = "") -> str:
        """
        创建检查点

        检查点包含：
        - feature_list.json 快照
        - claude-progress.txt 快照
        - Git commit hash
        - 会话元数据

        Args:
            session_id: 会话 ID
            description: 检查点描述

        Returns:
            检查点 ID
        """
        checkpoint_id = self._generate_checkpoint_id(session_id)
        checkpoint_dir = self.checkpoints_dir / checkpoint_id

        # 创建检查点目录
        checkpoint_dir.mkdir(parents=True, exist_ok=True)

        # 复制关键文件
        files_to_checkpoint = [
            "feature_list.json",
            "claude-progress.txt"
        ]

        for filename in files_to_checkpoint:
            src = self.project_path / filename
            if src.exists():
                dst = checkpoint_dir / filename
                shutil.copy2(src, dst)

        # 获取 git commit hash
        git_hash = self._get_git_hash()

        # 创建检查点元数据
        metadata = {
            "checkpoint_id": checkpoint_id,
            "session_id": session_id,
            "description": description,
            "timestamp": datetime.now().isoformat(),
            "git_hash": git_hash,
            "project_path": str(self.project_path)
        }

        metadata_path = checkpoint_dir / "metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)

        print(f"[StateManager] Checkpoint created: {checkpoint_id}")
        return checkpoint_id

    def restore_checkpoint(self, checkpoint_id: str) -> Dict:
        """
        恢复检查点

        Args:
            checkpoint_id: 检查点 ID

        Returns:
            恢复结果字典
        """
        checkpoint_dir = self.checkpoints_dir / checkpoint_id

        if not checkpoint_dir.exists():
            return {
                "status": "error",
                "error": f"Checkpoint {checkpoint_id} not found"
            }

        # 读取元数据
        metadata_path = checkpoint_dir / "metadata.json"
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        # 恢复文件
        files_to_restore = [
            "feature_list.json",
            "claude-progress.txt"
        ]

        for filename in files_to_restore:
            src = checkpoint_dir / filename
            if src.exists():
                dst = self.project_path / filename
                shutil.copy2(src, dst)

        # 可选：恢复 git 状态
        # git_hash = metadata["git_hash"]
        # self._git_restore(git_hash)

        print(f"[StateManager] Checkpoint restored: {checkpoint_id}")

        return {
            "status": "success",
            "checkpoint_id": checkpoint_id,
            "restored_at": datetime.now().isoformat(),
            "original_timestamp": metadata["timestamp"]
        }

    def list_checkpoints(self) -> List[Dict]:
        """列出所有检查点"""
        if not self.checkpoints_dir.exists():
            return []

        checkpoints = []

        for checkpoint_dir in sorted(self.checkpoints_dir.iterdir()):
            if not checkpoint_dir.is_dir():
                continue

            metadata_path = checkpoint_dir / "metadata.json"
            if not metadata_path.exists():
                continue

            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)

            checkpoints.append(metadata)

        return checkpoints

    def get_progress_metrics(self) -> Dict:
        """
        获取进度指标

        Returns:
            {
                "total_features": int,
                "completed_features": int,
                "in_progress_features": int,
                "pending_features": int,
                "completion_percentage": float,
                "estimated_sessions_remaining": int
            }
        """
        feature_list_path = self.project_path / "feature_list.json"

        if not feature_list_path.exists():
            return {
                "total_features": 0,
                "completed_features": 0,
                "in_progress_features": 0,
                "pending_features": 0,
                "completion_percentage": 0.0,
                "estimated_sessions_remaining": 0
            }

        with open(feature_list_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        total = len(data["features"])
        completed = sum(1 for f in data["features"] if f.get("passes", False))

        # TODO: 添加 in_progress 状态跟踪
        in_progress = 0
        pending = total - completed - in_progress

        completion_percentage = (completed / total * 100) if total > 0 else 0

        # 粗略估计：假设每个功能平均需要 1-2 个会话
        estimated_remaining = pending * 1.5

        return {
            "total_features": total,
            "completed_features": completed,
            "in_progress_features": in_progress,
            "pending_features": pending,
            "completion_percentage": round(completion_percentage, 2),
            "estimated_sessions_remaining": int(estimated_remaining)
        }

    def _generate_checkpoint_id(self, session_id: str) -> str:
        """生成检查点 ID"""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        content = f"{session_id}-{timestamp}"
        hash_obj = hashlib.md5(content.encode())
        return f"cp-{hash_obj.hexdigest()[:8]}-{timestamp}"

    def _get_git_hash(self) -> Optional[str]:
        """获取当前 git commit hash"""
        try:
            import subprocess
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except:
            return None
