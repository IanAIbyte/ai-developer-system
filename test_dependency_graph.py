"""
Test Dependency Graph Enhancement

验证 CodingAgent 的依赖图功能：
1. 依赖关系检查
2. 拓扑排序
3. 循环依赖检测
4. 依赖图可视化
"""

import json
from pathlib import Path
from orchestrator.coding_agent import CodingAgent


def test_dependency_checking():
    """测试依赖关系检查"""
    print("\n=== Test 1: Dependency Checking ===\n")

    # 创建测试功能列表
    features = [
        {
            "id": "setup-init-001",
            "description": "Initialize project",
            "priority": "critical",
            "passes": True,
            "dependencies": []
        },
        {
            "id": "data-model-001",
            "description": "Define data model",
            "priority": "critical",
            "passes": True,
            "dependencies": ["setup-init-001"]
        },
        {
            "id": "ui-todo-001",
            "description": "Create todo UI component",
            "priority": "high",
            "passes": False,
            "dependencies": ["data-model-001"]
        },
        {
            "id": "ui-todo-002",
            "description": "Add delete button",
            "priority": "medium",
            "passes": False,
            "dependencies": ["ui-todo-001"]
        }
    ]

    # 创建临时 CodingAgent 实例（不需要真实项目路径）
    from unittest.mock import Mock
    agent = CodingAgent(project_path="/tmp/test-project")
    agent.project_path = Path("/tmp/test-project")

    print("Test 1a: Check satisfied dependencies")
    result = agent._check_dependencies(features[2], features)
    print(f"  ui-todo-001 dependencies satisfied: {result['satisfied']}")
    print(f"  Satisfied deps: {result['dependencies']}")
    print(f"  Missing deps: {result['missing_deps']}")
    assert result['satisfied'] == True, "Should be satisfied"
    print("  ✅ Pass")

    print("\nTest 1b: Check unsatisfied dependencies")
    result = agent._check_dependencies(features[3], features)
    print(f"  ui-todo-002 dependencies satisfied: {result['satisfied']}")
    print(f"  Missing deps: {result['missing_deps']}")
    print(f"  Reason: {result['reason']}")
    assert result['satisfied'] == False, "Should not be satisfied"
    assert "ui-todo-001" in result['missing_deps']
    print("  ✅ Pass")


def test_circular_dependency_detection():
    """测试循环依赖检测"""
    print("\n=== Test 2: Circular Dependency Detection ===\n")

    features_with_cycle = [
        {
            "id": "feature-a",
            "description": "Feature A",
            "priority": "high",
            "passes": False,
            "dependencies": ["feature-b"]
        },
        {
            "id": "feature-b",
            "description": "Feature B",
            "priority": "high",
            "passes": False,
            "dependencies": ["feature-c"]
        },
        {
            "id": "feature-c",
            "description": "Feature C",
            "priority": "high",
            "passes": False,
            "dependencies": ["feature-a"]  # 循环：A → B → C → A
        }
    ]

    agent = CodingAgent(project_path="/tmp/test-project")
    agent.project_path = Path("/tmp/test-project")

    cycles = agent._detect_circular_dependencies(features_with_cycle)

    print(f"Detected {len(cycles)} circular dependency cycle(s):")
    for i, cycle in enumerate(cycles, 1):
        print(f"  Cycle {i}: {' → '.join(cycle)}")

    assert len(cycles) > 0, "Should detect circular dependency"
    print("  ✅ Pass")


def test_dependency_visualization():
    """测试依赖图可视化"""
    print("\n=== Test 3: Dependency Graph Visualization ===\n")

    features = [
        {
            "id": "setup-init-001",
            "description": "Initialize project",
            "priority": "critical",
            "passes": True,
            "dependencies": []
        },
        {
            "id": "data-model-001",
            "description": "Define data model",
            "priority": "critical",
            "passes": False,
            "dependencies": ["setup-init-001"]
        },
        {
            "id": "ui-todo-001",
            "description": "Create todo UI component",
            "priority": "high",
            "passes": False,
            "dependencies": ["data-model-001"]
        }
    ]

    agent = CodingAgent(project_path="/tmp/test-project")
    agent.project_path = Path("/tmp/test-project")

    visualization = agent._visualize_dependency_graph(features)
    print(visualization)

    assert "Completed (1)" in visualization
    assert "Pending (2)" in visualization
    assert "setup-init-001" in visualization
    print("  ✅ Pass")


def test_topological_sort():
    """测试拓扑排序功能"""
    print("\n=== Test 4: Topological Sort ===\n")

    features = [
        {
            "id": "setup-init-001",
            "description": "Initialize project",
            "priority": "critical",
            "passes": True,
            "dependencies": []
        },
        {
            "id": "data-model-001",
            "description": "Define data model",
            "priority": "critical",
            "passes": False,
            "dependencies": ["setup-init-001"]
        },
        {
            "id": "ui-header-001",
            "description": "Create header",
            "priority": "low",
            "passes": False,
            "dependencies": []  # 无依赖，但优先级低
        },
        {
            "id": "ui-todo-001",
            "description": "Create todo UI component",
            "priority": "high",
            "passes": False,
            "dependencies": ["data-model-001"]
        }
    ]

    agent = CodingAgent(project_path="/tmp/test-project")
    agent.project_path = Path("/tmp/test-project")

    context = {"feature_list": {"features": features}}

    # 选择下一个功能
    next_feature = agent._select_next_feature(context)

    print(f"Next feature selected: {next_feature['id']}")
    print(f"Description: {next_feature['description']}")
    print(f"Priority: {next_feature['priority']}")

    # 应该选择 data-model-001（critical 优先级，依赖已满足）
    # 而不是 ui-header-001（low 优先级，虽然无依赖）
    assert next_feature['id'] == 'data-model-001', "Should select data-model-001"
    print("  ✅ Pass - Correctly respects both priority and dependencies")


def test_dot_export():
    """测试 DOT 格式导出"""
    print("\n=== Test 5: DOT Format Export ===\n")

    features = [
        {
            "id": "setup-init-001",
            "description": "Initialize project",
            "priority": "critical",
            "passes": True,
            "dependencies": []
        },
        {
            "id": "data-model-001",
            "description": "Define data model",
            "priority": "critical",
            "passes": False,
            "dependencies": ["setup-init-001"]
        }
    ]

    agent = CodingAgent(project_path="/tmp/test-project")
    agent.project_path = Path("/tmp/test-project")

    dot_content = agent._export_dependency_graph_dot(features)

    print("DOT format preview:")
    print(dot_content[:200] + "...")

    assert "digraph FeatureDependencies" in dot_content
    assert "setup-init-001" in dot_content
    assert "data-model-001" in dot_content
    print("  ✅ Pass")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Testing Dependency Graph Enhancement")
    print("=" * 60)

    try:
        test_dependency_checking()
        test_circular_dependency_detection()
        test_dependency_visualization()
        test_topological_sort()
        test_dot_export()

        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        raise
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise
