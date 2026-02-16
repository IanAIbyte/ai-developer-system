"""
Initializer Agent - 初始化代理

职责：
1. 分析用户需求，生成详细的功能列表
2. 创建项目骨架
3. 编写 init.sh（开发服务器启动脚本）
4. 初始化 git 仓库
5. 创建 claude-progress.txt 进度跟踪文件
6. 配置测试环境

基于 Anthropic 的 "Effective harnesses for long-running agents" 框架
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional
import subprocess
from datetime import datetime


class InitializerAgent:
    """初始化代理 - 项目环境设置专家"""

    def __init__(self, project_path: str, user_prompt: str, template: str = "webapp"):
        """
        初始化代理

        Args:
            project_path: 项目路径
            user_prompt: 用户需求描述
            template: 项目模板类型 (webapp/api/library)
        """
        self.project_path = Path(project_path).absolute()
        self.user_prompt = user_prompt
        self.template = template
        self.timestamp = datetime.now().isoformat()

    def initialize(self) -> Dict:
        """
        执行完整初始化流程

        Returns:
            初始化结果字典
        """
        print(f"[Initializer] Starting project initialization at {self.project_path}")

        # 1. 创建项目目录
        self._create_project_structure()

        # 2. 生成功能列表（核心！）
        feature_list = self._generate_feature_list()

        # 3. 创建 init.sh 脚本
        init_script = self._create_init_script()

        # 4. 初始化 git 仓库
        self._initialize_git()

        # 5. 创建进度跟踪文件
        progress_file = self._create_progress_file()

        # 6. 配置测试环境
        test_config = self._setup_testing_environment()

        # 7. 初始 git commit
        self._initial_commit()

        result = {
            "status": "success",
            "project_path": str(self.project_path),
            "feature_count": len(feature_list["features"]),
            "template": self.template,
            "timestamp": self.timestamp,
            "next_step": "Run coding_agent.py to start development"
        }

        print(f"[Initializer] ✅ Initialization complete!")
        print(f"[Initializer] Generated {len(feature_list['features'])} features")
        print(f"[Initializer] Ready for coding agent to begin")

        return result

    def _create_project_structure(self):
        """创建基础项目结构（包括视觉验证预设）"""
        directories = [
            "src",
            "tests",
            "docs",
            "screenshots",
            ".claude",
            "logs"
        ]

        for directory in directories:
            dir_path = self.project_path / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"[Initializer] Created directory: {directory}")

        # 为视觉测试创建子目录结构
        if self.template in ["webapp", "api"]:
            screenshot_dirs = [
                "screenshots/baseline",
                "screenshots/actual",
                "screenshots/diff"
            ]
            for subdir in screenshot_dirs:
                subdir_path = self.project_path / subdir
                subdir_path.mkdir(parents=True, exist_ok=True)
                print(f"[Initializer] Created directory: {subdir}")

            # 创建 README 说明截图目录用途
            readme_path = self.project_path / "screenshots" / "README.md"
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write("""# Screenshots Directory

This directory is used for visual regression testing.

## Structure

- **baseline/**: Reference screenshots of expected UI states
- **actual/**: Current screenshots captured during testing
- **diff/**: Comparison images highlighting visual differences

## Usage

### Adding New Baseline Screenshots

1. Implement a feature
2. Manually capture screenshots of key UI states
3. Save them to `baseline/` with descriptive names:
   - `baseline/login-page-initial.png`
   - `baseline/dashboard-with-data.png`
   - `baseline/todo-item-hover.png`

### Automated Testing

When E2E tests run:
1. Screenshots are captured to `actual/`
2. Compared against `baseline/` images
3. Differences saved to `diff/`
4. Test fails if visual difference exceeds threshold

### Visual Validation Criteria

- Layout consistency (elements aligned correctly)
- Color accuracy (matches design tokens)
- Typography (fonts, sizes, weights)
- Component states (hover, active, disabled)
- Responsive breakpoints (mobile, tablet, desktop)

### Updating Baselines

When UI changes are intentional:
1. Review visual differences in `diff/`
2. If changes are correct, copy `actual/` to `baseline/`
3. Commit new baseline images
""")

    def _generate_feature_list(self) -> Dict:
        """
        生成功能列表 JSON 文件

        核心要素：
        - 将用户需求分解为 200+ 个细粒度功能
        - 每个功能包含：category, description, steps, passes (初始为 false)
        - 使用 JSON 格式（比 Markdown 更难被模型误改）
        """
        features = self._expand_prompt_to_features(self.user_prompt)

        feature_list = {
            "project_name": self._extract_project_name(),
            "user_prompt": self.user_prompt,
            "template": self.template,
            "total_features": len(features),
            "features": features,
            "metadata": {
                "generated_at": self.timestamp,
                "generated_by": "InitializerAgent",
                "version": "0.1.0"
            }
        }

        feature_list_path = self.project_path / "feature_list.json"
        with open(feature_list_path, 'w', encoding='utf-8') as f:
            json.dump(feature_list, f, indent=2, ensure_ascii=False)

        print(f"[Initializer] Created feature_list.json with {len(features)} features")
        return feature_list

    def _expand_prompt_to_features(self, prompt: str) -> List[Dict]:
        """
        将用户需求扩展为详细功能列表

        使用 GLM-5 API 智能分析需求并生成功能列表
        """
        try:
            from .llm_clients import GLM5Client
            import sys

            print(f"[Initializer] Using GLM-5 API to generate features...", file=sys.stderr, flush=True)

            # 创建 GLM-5 客户端
            glm_client = GLM5Client()

            # 调用 API 生成功能列表（标准模式：30 个功能）
            features = glm_client.analyze_requirements(prompt, max_features=30, show_progress=True)

            print(f"[Initializer] ✅ Generated {len(features)} features using GLM-5", file=sys.stderr, flush=True)
            return features

        except Exception as e:
            print(f"[Initializer] ⚠️  GLM-5 feature generation failed: {e}")
            print(f"[Initializer] Falling back to basic feature generation")

            # Fallback 到基础功能列表
            return [
                {
                    "id": "setup-env-001",
                    "category": "setup",
                    "priority": "critical",
                    "description": "Project dependencies are installed",
                    "steps": [
                        "Check package.json exists",
                        "Run npm install",
                        "Verify node_modules created"
                    ],
                    "passes": False,
                    "dependencies": []
                },
                {
                    "id": "setup-devserver-001",
                    "category": "setup",
                    "priority": "critical",
                    "description": "Development server starts successfully",
                    "steps": [
                        "Run init.sh script",
                        "Wait for server to start",
                        "Verify server is responding"
                    ],
                    "passes": False,
                    "dependencies": ["setup-env-001"]
                }
            ]

    def _create_init_script(self) -> str:
        """
        创建健壮的 init.sh 脚本（改进版）

        关键改进：
        1. 强制预检关键文件
        2. 对于 webapp，自动调用脚手架创建项目
        3. 环境完整性检查
        4. 失败时提供清晰的错误信息
        """
        # 模板配置
        template_configs = {
            "webapp": {
                "check_files": ["package.json"],
                "scaffold_command": "npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir --import-alias '@/*' --yes",
                "install_command": "npm install",
                "start_command": "npm run dev",
                "port": 3000,
                "wait_time": 8
            },
            "api": {
                "check_files": ["requirements.txt", "main.py"],
                "scaffold_command": "mkdir -p backend && cd backend && cat > requirements.txt << 'EOF'\nfastapi==0.115.0\nuvicorn[standard]==0.32.0\npydantic==2.10.0\npython-dotenv==1.0.0\nEOF\n",
                "install_command": "pip install -r requirements.txt",
                "start_command": "cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000",
                "port": 8000,
                "wait_time": 5
            },
            "library": {
                "check_files": ["setup.py", "pyproject.toml"],
                "scaffold_command": "cat > pyproject.toml << 'EOF'\n[build-system]\nrequires = [\"setuptools>=45\", \"wheel\"]\nbuild-backend = \"setuptools.build_meta\"\nEOF\n",
                "install_command": "pip install -e .",
                "start_command": "pytest -v",
                "port": None,
                "wait_time": 2
            }
        }

        # 获取当前模板配置（默认使用 webapp）
        config = template_configs.get(self.template, template_configs["webapp"])

        # 生成健壮的脚本内容
        script_content = f"""#!/bin/bash

# Init Script - Development Environment Setup (Enhanced)
# Generated by InitializerAgent
# Template: {self.template}
#
# Features:
# - Preflight checks for critical files
# - Automatic scaffolding if needed
# - Environment integrity validation
# - Clear error messages

set -e  # Exit on error

echo "🚀 Initializing development environment..."
echo "📋 Template type: {self.template}"
echo ""

# =============================================================================
# PREFLIGHT CHECKS - 强制检查关键文件
# =============================================================================
echo "🔍 Phase 1: Preflight Checks"
echo "-----------------------------------"

MISSING_FILES=()

# 检查关键文件是否存在
"""

        # 根据模板类型添加检查逻辑
        if self.template == "webapp":
            script_content += """
# Check for package.json
if [ ! -f "package.json" ]; then
    echo "⚠️  package.json not found"
    echo "🔧 Attempting to scaffold Next.js project..."

    # 检查是否在空目录中
    if [ -z "$(ls -A)" ]; then
        echo "📁 Empty directory detected, creating Next.js app..."
        npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir --import-alias '@/*' --yes || {
            echo "❌ Failed to scaffold Next.js project"
            echo "💡 Please ensure npx and Node.js are installed"
            echo "   Node.js: https://nodejs.org/"
            exit 1
        }
        echo "✅ Next.js project scaffolded successfully"
    else
        echo "❌ Error: Directory not empty and package.json missing"
        echo "💡 Either:"
        echo "   1. Start from an empty directory, or"
        echo "   2. Run 'npx create-next-app@latest . --typescript --tailwind' in current directory"
        echo "   3. Use an existing Next.js project with package.json"
        exit 1
    fi
else
    echo "✅ package.json found"
fi

# 验证 package.json 有效性
if [ -f "package.json" ]; then
    if ! jq empty package.json >/dev/null 2>&1; then
        echo "⚠️  Warning: package.json may be malformed"
        echo "   Attempting to fix..."
        jq '.' package.json > package.json.fixed
        mv package.json.fixed package.json
    fi
fi

echo ""
"""
        elif self.template == "api":
            script_content += """
# Check for Python API files
if [ ! -f "requirements.txt" ] && [ ! -f "main.py" ]; then
    echo "⚠️  API files not found"
    echo "🔧 Creating minimal FastAPI structure..."

    mkdir -p backend
    cd backend

    # Create requirements.txt
    cat > requirements.txt << 'REQEOF'
fastapi==0.115.0
uvicorn[standard]==0.32.0
pydantic==2.10.0
python-dotenv==1.0.0
REQEOF

    # Create minimal main.py
    cat > main.py << 'MAINEOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "running", "message": "API is ready"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
MAINEOF

    cd ..
    echo "✅ FastAPI structure created"
else
    echo "✅ API files found"
fi

echo ""
"""
        elif self.template == "library":
            script_content += """
# Check for library files
if [ ! -f "setup.py" ] && [ ! -f "pyproject.toml" ] && [ ! -f "package.json" ]; then
    echo "❌ Error: No library configuration found"
    echo "💡 Please provide one of:"
    echo "   - setup.py (Python)"
    echo "   - pyproject.toml (Python)"
    echo "   - package.json (Node.js)"
    exit 1
fi
echo "✅ Library configuration found"
echo ""
"""

        # 通用安装和启动逻辑
        script_content += f"""
# =============================================================================
# DEPENDENCY INSTALLATION
# =============================================================================
echo "📦 Phase 2: Installing Dependencies"
echo "-----------------------------------"

"""

        if self.template == "webapp":
            script_content += """
echo "📦 Installing Node.js dependencies..."
if command -v npm >/dev/null 2>&1; then
    npm install || {
        echo "❌ Failed to install dependencies"
        echo "💡 Try deleting node_modules and package-lock.json, then run again"
        exit 1
    }
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Error: npm not found"
    echo "💡 Install Node.js from: https://nodejs.org/"
    exit 1
fi

echo ""
"""
        elif self.template == "api":
            script_content += """
echo "📦 Installing Python dependencies..."
if command -v pip3 >/dev/null 2>&1; then
    # Check if backend directory exists
    if [ -d "backend" ]; then
        cd backend
        pip3 install -r requirements.txt || {
            echo "❌ Failed to install Python dependencies"
            echo "💡 Try: pip3 install --upgrade pip"
            exit 1
        }
        cd ..
        echo "✅ Python dependencies installed"
    else
        pip3 install -r requirements.txt || pip3 install -e .
    fi
else
    echo "❌ Error: pip3 not found"
    echo "💡 Install Python from: https://www.python.org/"
    exit 1
fi

echo ""
"""
        elif self.template == "library":
            script_content += """
echo "📦 Installing library..."
if [ -f "requirements.txt" ]; then
    pip3 install -e .
elif [ -f "package.json" ]; then
    npm install || npm link
fi
echo "✅ Library installed"
echo ""
"""

        # 启动服务
        script_content += f"""
# =============================================================================
# START DEVELOPMENT SERVER
# =============================================================================
echo "🔥 Phase 3: Starting Development Server"
echo "-----------------------------------"

"""

        if self.template == "webapp":
            script_content += """
echo "🚀 Starting Next.js development server..."
npm run dev > /tmp/dev-server.log 2>&1 &
DEV_PID=$!

echo "⏳ Waiting for server to start (this may take 10-15 seconds)..."
for i in {{1..{config['wait_time']}}}; do
    sleep 1
    if curl -s http://localhost:{config['port']} >/dev/null 2>&1; then
        echo "✅ Development server is ready!"
        break
    fi
    if [ $i -eq {config['wait_time']} ]; then
        echo "⚠️  Server taking longer than expected..."
        echo "📋 Check logs: tail -f /tmp/dev-server.log"
    fi
done

echo ""
echo "🎉 Initialization complete!"
echo "📍 Frontend: http://localhost:{config['port']}"
echo "📋 Logs: tail -f /tmp/dev-server.log"
echo ""
echo "💡 Press Ctrl+C to stop the server"

# 保持进程运行
wait $DEV_PID
"""
        elif self.template == "api":
            script_content += """
# Find and start the API
if [ -d "backend" ]; then
    cd backend
    START_CMD="uvicorn main:app --reload --host 0.0.0.0 --port {config['port']}"
else
    START_CMD="uvicorn main:app --reload --host 0.0.0.0 --port {config['port']}"
fi

echo "🚀 Starting API server..."
$START_CMD > /tmp/api-server.log 2>&1 &
API_PID=$!

echo "⏳ Waiting for server to start..."
sleep {config['wait_time']}

if curl -s http://localhost:{config['port']}/health >/dev/null 2>&1; then
    echo "✅ API server is ready!"
else
    echo "⚠️  Health check failed, check logs"
fi

echo ""
echo "🎉 Initialization complete!"
echo "📍 API: http://localhost:{config['port']}"
echo "📚 API Docs: http://localhost:{config['port']}/docs"
echo "📋 Logs: tail -f /tmp/api-server.log"
echo ""

wait $API_PID
"""
        elif self.template == "library":
            script_content += """
echo "🧪 Running tests..."
if [ -f "setup.py" ] || [ -f "pyproject.toml" ]; then
    pytest -v || python3 -m pytest -v || echo "⚠️  No tests found"
elif [ -f "package.json" ]; then
    npm test || echo "⚠️  No tests found"
fi

echo ""
echo "✅ Library setup complete!"
"""

        # 环境信息（保持不变）
        script_content += """

# =============================================================================
# ENVIRONMENT INFORMATION
# =============================================================================
echo ""
echo "📊 Environment Info:"
echo "   Python: $(python3 --version 2>/dev/null || python --version 2>/dev/null || echo 'Not found')"
echo "   Node.js: $(node --version 2>/dev/null || echo 'Not found')"
echo "   npm: $(npm --version 2>/dev/null || echo 'Not found')"
echo "   Working Directory: $(pwd)"
echo ""

# =============================================================================
# POST-INIT VALIDATION
# =============================================================================
echo "✅ Initialization completed successfully!"
echo ""
echo "📝 Next Steps:"
if [ "{self.template}" = "webapp" ]; then
    echo "   1. Open http://localhost:3000 in your browser"
    echo "   2. Start editing files in src/ or app/"
    echo "   3. Changes will auto-reload"
elif [ "{self.template}" = "api" ]; then
    echo "   1. Open http://localhost:8000/docs in your browser"
    echo "   2. Review API endpoints"
    echo "   3. Edit backend/main.py to add routes"
fi
echo ""

# Return success
exit 0
"""

        return script_content

echo "   Git: $(git --version 2>/dev/null || echo 'Not found')"
echo ""
echo "✅ Development environment setup complete!"
"""

        init_script_path = self.project_path / "init.sh"
        with open(init_script_path, 'w') as f:
            f.write(script_content)

        # Make executable
        os.chmod(init_script_path, 0o755)

        print(f"[Initializer] Created init.sh for template: {self.template}")
        return script_content

    def _initialize_git(self):
        """初始化 git 仓库（根据模板类型生成对应的 .gitignore）"""
        subprocess.run(
            ["git", "init"],
            cwd=self.project_path,
            capture_output=True,
            check=True
        )

        # 根据模板类型生成 .gitignore
        common_ignore = """# Environment
.env
.env.local
*.env

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db

# Editor
.vscode/
.idea/
*.swp
*.swo
*~

# AI Developer System
.claude/logs/
.claude/.tmp/

"""

        if self.template == "webapp":
            gitignore_content = common_ignore + """# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnpm-debug.log*

# Build outputs
dist/
build/
.next/
out/

# Testing
coverage/
.nyc_output/

# Misc
.cache/
.parcel-cache/
"""
        elif self.template == "api":
            gitignore_content = common_ignore + """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
ENV/
env/
.venv

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# Database
*.db
*.sqlite3
"""
        elif self.template == "library":
            gitignore_content = common_ignore + """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
ENV/
env/
.venv

# Node.js
node_modules/

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/
"""
        else:
            # 默认（webapp）
            gitignore_content = common_ignore + """# Node.js
node_modules/
dist/
build/
"""

        gitignore_path = self.project_path / ".gitignore"
        with open(gitignore_path, 'w') as f:
            f.write(gitignore_content)

        print(f"[Initializer] Initialized git repository with .gitignore for {self.template}")

    def _create_progress_file(self) -> str:
        """
        创建进度跟踪文件

        格式：claude-progress.txt
        内容：
        - 项目元数据
        - 每次会话的详细记录
        - 当前状态
        - 下一步计划
        """
        progress_content = f"""=== AI Developer System - Progress Log ===
Project: {self._extract_project_name()}
Template: {self.template}
Started: {self.timestamp}
User Prompt: {self.user_prompt}

[Session 0] Initializer Agent
Timestamp: {self.timestamp}
Completed:
- Created project structure
- Generated feature_list.json with features
- Created init.sh script
- Initialized git repository
- Configured testing environment

Status: READY FOR CODING AGENT
Next Steps:
1. Run init.sh to start development server
2. Coding agent should select highest-priority feature
3. Implement and test feature
4. Commit and update progress

Feature Statistics:
- Total: {len(self._expand_prompt_to_features(self.user_prompt))}
- Completed: 0
- In Progress: 0
- Pending: All

=== End of Session 0 ===
"""

        progress_path = self.project_path / "claude-progress.txt"
        with open(progress_path, 'w', encoding='utf-8') as f:
            f.write(progress_content)

        print(f"[Initializer] Created claude-progress.txt")
        return progress_content

    def _setup_testing_environment(self) -> Dict:
        """
        配置测试环境（包括视觉验证预设）

        根据模板类型设置：
        - E2E 测试框架 (Playwright/Puppeteer)
        - 单元测试框架
        - MCP 服务器配置
        - 视觉测试配置
        """
        # 基础测试配置
        test_config = {
            "e2e_framework": "playwright",
            "unit_framework": "jest",
            "mcp_servers": ["puppeteer"]
        }

        # 添加视觉验证配置（仅 webapp 和 api 模板）
        if self.template in ["webapp", "api"]:
            test_config["visual_testing"] = {
                "enabled": True,
                "framework": "playwright",  # 或 "puppeteer"
                "screenshots_dir": "screenshots",
                "baseline_dir": "screenshots/baseline",
                "actual_dir": "screenshots/actual",
                "diff_dir": "screenshots/diff",
                "comparison_threshold": 0.1,  # 像素差异阈值 (0-1)
                "screenshot_options": {
                    "full_page": True,
                    "capture_beyond_viewport": True,
                    "animations": "allowed",  # 允许动画完成
                },
                "validation_criteria": {
                    "layout": True,  # 检查布局一致性
                    "colors": True,  # 检查颜色准确性
                    "typography": True,  # 检查字体和排版
                    "interactions": True  # 检查交互状态
                },
                "ignored_regions": [],  # CSS selectors of dynamic regions to ignore
                "viewport_sizes": [
                    {"name": "mobile", "width": 375, "height": 667},
                    {"name": "tablet", "width": 768, "height": 1024},
                    {"name": "desktop", "width": 1440, "height": 900}
                ],
                "max_diff_pixels": 100,  # 最大允许不同像素数
                "update_baseline_command": "cp screenshots/actual/$TEST.png screenshots/baseline/$TEST.png"
            }

        config_path = self.project_path / ".claude" / "test_config.json"
        # 确保 .claude 目录存在
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(test_config, f, indent=2)

        print(f"[Initializer] Configured testing environment")
        if self.template in ["webapp", "api"]:
            print(f"[Initializer]   - Visual testing enabled with {len(test_config['visual_testing']['viewport_sizes'])} viewports")
        return test_config

    def _initial_commit(self):
        """创建初始 git commit"""
        subprocess.run(
            ["git", "add", "."],
            cwd=self.project_path,
            capture_output=True,
            check=True
        )

        commit_message = f"""feat: initial project setup

Initialized by AI Developer System Initializer Agent

- Created project structure
- Generated feature_list.json
- Created init.sh script
- Initialized git repository
- Configured testing environment

Project: {self._extract_project_name()}
Template: {self.template}
Timestamp: {self.timestamp}
"""

        subprocess.run(
            ["git", "commit", "-m", commit_message],
            cwd=self.project_path,
            capture_output=True,
            check=True
        )

        print(f"[Initializer] Created initial git commit")

    def _extract_project_name(self) -> str:
        """从用户提示中提取项目名称（简化版）"""
        return self.project_path.name


# CLI 接口
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Initializer Agent - Set up autonomous development environment"
    )
    parser.add_argument(
        "--prompt",
        required=True,
        help="User requirement description"
    )
    parser.add_argument(
        "--project",
        required=True,
        help="Project directory path"
    )
    parser.add_argument(
        "--template",
        default="webapp",
        choices=["webapp", "api", "library"],
        help="Project template type"
    )

    args = parser.parse_args()

    agent = InitializerAgent(
        project_path=args.project,
        user_prompt=args.prompt,
        template=args.template
    )

    result = agent.initialize()
    print("\n=== Initialization Result ===")
    print(json.dumps(result, indent=2))
