"""
Test Template-Aware init.sh Generation

验证 InitializerAgent 的模板自适应功能：
1. Webapp 模板生成 Node.js 启动脚本
2. API 模板生成 Python/Node.js API 启动脚本
3. Library 模板生成库测试脚本
4. .gitignore 根据模板类型调整
"""

import tempfile
import shutil
from pathlib import Path
from orchestrator.initializer_agent import InitializerAgent


def test_webapp_template():
    """测试 Webapp 模板"""
    print("\n=== Test 1: Webapp Template ===\n")

    with tempfile.TemporaryDirectory() as tmpdir:
        agent = InitializerAgent(
            project_path=tmpdir,
            user_prompt="Create a web application",
            template="webapp"
        )

        # 生成 init.sh
        init_script = agent._create_init_script()

        print("Generated init.sh (first 50 lines):")
        print(init_script[:800] + "...")

        # 验证关键内容
        assert "npm install" in init_script, "Should include npm install"
        assert "npm run dev" in init_script, "Should include npm run dev"
        assert "localhost:3000" in init_script, "Should use port 3000"
        assert "Web Application (Next.js, React, Vue)" in init_script, "Should mention webapp"
        print("\n✅ Pass - Webapp template generates correct script")


def test_api_template():
    """测试 API 模板"""
    print("\n=== Test 2: API Template ===\n")

    with tempfile.TemporaryDirectory() as tmpdir:
        agent = InitializerAgent(
            project_path=tmpdir,
            user_prompt="Create an API service",
            template="api"
        )

        # 生成 init.sh
        init_script = agent._create_init_script()

        print("Generated init.sh (first 50 lines):")
        print(init_script[:800] + "...")

        # 验证关键内容
        assert "pip install -r requirements.txt" in init_script or "pip install -e ." in init_script
        assert "uvicorn" in init_script, "Should include uvicorn"
        assert "localhost:8000" in init_script, "Should use port 8000"
        assert "API Service (FastAPI, Express, Django)" in init_script, "Should mention API"
        assert "/docs" in init_script, "Should mention API docs endpoint"
        print("\n✅ Pass - API template generates correct script")


def test_library_template():
    """测试 Library 模板"""
    print("\n=== Test 3: Library Template ===\n")

    with tempfile.TemporaryDirectory() as tmpdir:
        agent = InitializerAgent(
            project_path=tmpdir,
            user_prompt="Create a library",
            template="library"
        )

        # 生成 init.sh
        init_script = agent._create_init_script()

        print("Generated init.sh (first 50 lines):")
        print(init_script[:800] + "...")

        # 验证关键内容
        assert "pip install -e ." in init_script or "npm link" in init_script
        assert "pytest" in init_script, "Should include pytest"
        assert "Library Project (Python/Node.js library)" in init_script, "Should mention library"
        print("\n✅ Pass - Library template generates correct script")


def test_gitignore_webapp():
    """测试 Webapp 模板的 .gitignore"""
    print("\n=== Test 4: Webapp .gitignore ===\n")

    with tempfile.TemporaryDirectory() as tmpdir:
        agent = InitializerAgent(
            project_path=tmpdir,
            user_prompt="Create a web application",
            template="webapp"
        )

        # 初始化 git（生成 .gitignore）
        agent._initialize_git()

        gitignore_path = Path(tmpdir) / ".gitignore"
        assert gitignore_path.exists(), ".gitignore should be created"

        with open(gitignore_path) as f:
            gitignore_content = f.read()

        print(".gitignore content (first 500 chars):")
        print(gitignore_content[:500] + "...")

        # 验证关键内容
        assert "node_modules/" in gitignore_content, "Should ignore node_modules"
        assert ".next/" in gitignore_content or "dist/" in gitignore_content
        assert ".DS_Store" in gitignore_content, "Should ignore .DS_Store"
        assert ".claude/logs/" in gitignore_content, "Should ignore AI logs"
        print("\n✅ Pass - Webapp .gitignore includes correct patterns")


def test_gitignore_api():
    """测试 API 模板的 .gitignore"""
    print("\n=== Test 5: API .gitignore ===\n")

    with tempfile.TemporaryDirectory() as tmpdir:
        agent = InitializerAgent(
            project_path=tmpdir,
            user_prompt="Create an API service",
            template="api"
        )

        # 初始化 git（生成 .gitignore）
        agent._initialize_git()

        gitignore_path = Path(tmpdir) / ".gitignore"
        assert gitignore_path.exists(), ".gitignore should be created"

        with open(gitignore_path) as f:
            gitignore_content = f.read()

        print(".gitignore content (first 500 chars):")
        print(gitignore_content[:500] + "...")

        # 验证关键内容
        assert "__pycache__/" in gitignore_content, "Should ignore Python cache"
        assert "venv/" in gitignore_content or "ENV/" in gitignore_content
        assert "*.py[cod]" in gitignore_content, "Should ignore Python bytecode"
        assert ".DS_Store" in gitignore_content, "Should ignore .DS_Store"
        print("\n✅ Pass - API .gitignore includes correct patterns")


def test_gitignore_library():
    """测试 Library 模板的 .gitignore"""
    print("\n=== Test 6: Library .gitignore ===\n")

    with tempfile.TemporaryDirectory() as tmpdir:
        agent = InitializerAgent(
            project_path=tmpdir,
            user_prompt="Create a library",
            template="library"
        )

        # 初始化 git（生成 .gitignore）
        agent._initialize_git()

        gitignore_path = Path(tmpdir) / ".gitignore"
        assert gitignore_path.exists(), ".gitignore should be created"

        with open(gitignore_path) as f:
            gitignore_content = f.read()

        print(".gitignore content (first 500 chars):")
        print(gitignore_content[:500] + "...")

        # 验证关键内容
        assert "__pycache__/" in gitignore_content, "Should ignore Python cache"
        assert "*.egg-info/" in gitignore_content, "Should ignore egg-info"
        assert ".pytest_cache/" in gitignore_content or ".tox/" in gitignore_content
        print("\n✅ Pass - Library .gitignore includes correct patterns")


def test_environment_info():
    """测试环境信息显示"""
    print("\n=== Test 7: Environment Info Display ===\n")

    with tempfile.TemporaryDirectory() as tmpdir:
        agent = InitializerAgent(
            project_path=tmpdir,
            user_prompt="Create a web application",
            template="webapp"
        )

        # 生成 init.sh
        init_script = agent._create_init_script()

        # 验证包含环境信息部分
        assert "Environment Info:" in init_script, "Should show environment info"
        assert "Python:" in init_script, "Should show Python version"
        assert "Node.js:" in init_script, "Should show Node.js version"
        assert "Git:" in init_script, "Should show Git version"
        print("✅ Pass - Script includes environment information display")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Testing Template-Aware init.sh Generation")
    print("=" * 60)

    try:
        test_webapp_template()
        test_api_template()
        test_library_template()
        test_gitignore_webapp()
        test_gitignore_api()
        test_gitignore_library()
        test_environment_info()

        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        print("\n📋 Summary:")
        print("  - Webapp: Node.js/npm with dev server on port 3000")
        print("  - API: Python pip with uvicorn on port 8000")
        print("  - Library: Development install with test runner")
        print("  - .gitignore: Tailored to each template type")

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        raise
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise
