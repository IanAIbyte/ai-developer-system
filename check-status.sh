#!/bin/bash
# AI Developer System - 项目状态快速查看脚本

PROJECT_PATH="${1:-.}"

echo "🔍 检查项目状态: $PROJECT_PATH"
echo ""

# 运行 Python 脚本
python3 check_project_status.py "$PROJECT_PATH" "$@"
