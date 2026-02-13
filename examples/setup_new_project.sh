#!/bin/bash

# AI Developer System - 示例：设置新项目

set -e

echo "========================================="
echo "AI Developer System - New Project Setup"
echo "========================================="
echo ""

# 1. 创建项目目录
PROJECT_DIR="./workspace/my-first-ai-app"
echo "1. Creating project directory: $PROJECT_DIR"
mkdir -p "$PROJECT_DIR"

# 2. 创建用户需求文件
cat > "$PROJECT_DIR/user_prompt.txt" << 'EOF'
Build a simple todo app with the following features:

Core Features:
- User can add a new todo item
- User can mark todos as complete
- User can delete todos
- User can filter todos by status (all/active/completed)
- Todos are persisted in local storage

Technical Requirements:
- Use Next.js with TypeScript
- Use Tailwind CSS for styling
- Use localStorage for data persistence
- Include E2E tests with Playwright
- Follow responsive design principles

Design:
- Clean, modern interface
- Mobile-friendly
- Good accessibility (ARIA labels, keyboard navigation)
EOF

echo "   Created user_prompt.txt"

# 3. 运行初始化代理
echo ""
echo "2. Running Initializer Agent..."
echo ""

python3 -m orchestrator.initializer_agent \
    --project "$PROJECT_DIR" \
    --prompt "$(cat $PROJECT_DIR/user_prompt.txt)" \
    --template webapp

echo ""
echo "========================================="
echo "✅ Setup Complete!"
echo "========================================="
echo ""
echo "Project directory: $PROJECT_DIR"
echo ""
echo "Next steps:"
echo "  1. cd $PROJECT_DIR"
echo "  2. Review feature_list.json"
echo "  3. Run: python3 -m orchestrator.scheduler --project . --mode single-feature"
echo "  4. Or for autonomous mode: python3 -m orchestrator.scheduler --project . --mode autonomous"
echo ""
