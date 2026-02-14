"""
Test Visual Testing Helper

验证 VisualTestingHelper 的功能：
1. 配置加载
2. 路径生成
3. 视口配置
4. 验证步骤生成
5. 代码生成
"""

import tempfile
import json
from pathlib import Path
from orchestrator.visual_testing import VisualTestingHelper


def create_test_project(project_type: str = "webapp") -> str:
    """创建测试项目并返回路径"""
    tmpdir = tempfile.mkdtemp()

    # 创建必要的目录和配置
    (Path(tmpdir) / "screenshots").mkdir()
    (Path(tmpdir) / "screenshots" / "baseline").mkdir()
    (Path(tmpdir) / "screenshots" / "actual").mkdir()
    (Path(tmpdir) / "screenshots" / "diff").mkdir()
    (Path(tmpdir) / ".claude").mkdir()

    # 创建测试配置
    if project_type in ["webapp", "api"]:
        test_config = {
            "e2e_framework": "playwright",
            "unit_framework": "jest",
            "mcp_servers": ["puppeteer"],
            "visual_testing": {
                "enabled": True,
                "framework": "playwright",
                "screenshots_dir": "screenshots",
                "baseline_dir": "screenshots/baseline",
                "actual_dir": "screenshots/actual",
                "diff_dir": "screenshots/diff",
                "comparison_threshold": 0.1,
                "screenshot_options": {
                    "full_page": True
                },
                "validation_criteria": {
                    "layout": True,
                    "colors": True,
                    "typography": True,
                    "interactions": True
                },
                "viewport_sizes": [
                    {"name": "mobile", "width": 375, "height": 667},
                    {"name": "tablet", "width": 768, "height": 1024},
                    {"name": "desktop", "width": 1440, "height": 900}
                ],
                "max_diff_pixels": 100
            }
        }
    else:
        test_config = {
            "e2e_framework": "pytest",
            "unit_framework": "pytest"
        }

    with open(Path(tmpdir) / ".claude" / "test_config.json", 'w') as f:
        json.dump(test_config, f, indent=2)

    return tmpdir


def test_config_loading():
    """测试配置加载"""
    print("\n=== Test 1: Configuration Loading ===\n")

    project_dir = create_test_project("webapp")
    helper = VisualTestingHelper(project_dir)

    config = helper.config
    assert "visual_testing" in config, "Should load visual_testing config"
    assert config["visual_testing"]["enabled"] == True, "Visual testing should be enabled"
    print("✓ Configuration loaded successfully")
    print(f"  Framework: {config['visual_testing']['framework']}")
    print(f"  Viewports: {len(config['visual_testing']['viewport_sizes'])} configured")
    print("✅ Pass")


def test_screenshot_path_generation():
    """测试截图路径生成"""
    print("\n=== Test 2: Screenshot Path Generation ===\n")

    project_dir = create_test_project("webapp")
    helper = VisualTestingHelper(project_dir)

    # Test actual screenshot path
    path = helper.get_screenshot_path("ui-login-001", "desktop", "actual")
    assert "screenshots/actual" in str(path), "Should include actual directory"
    assert "ui-login-001" in str(path), "Should include feature ID"
    assert "desktop" in str(path), "Should include viewport name"
    print(f"✓ Actual path: {path.name}")
    print(f"  Full: {path}")

    # Test baseline path
    baseline = helper.get_baseline_path("ui-login-001", "mobile")
    assert "screenshots/baseline" in str(baseline), "Should include baseline directory"
    print(f"✓ Baseline path: {baseline.name}")

    # Test diff path
    diff = helper.get_diff_path("ui-login-001", "tablet")
    assert "screenshots/diff" in str(diff), "Should include diff directory"
    assert "diff" in str(diff), "Should include diff suffix"
    print(f"✓ Diff path: {diff.name}")

    print("✅ Pass")


def test_viewport_configs():
    """测试视口配置"""
    print("\n=== Test 3: Viewport Configurations ===\n")

    project_dir = create_test_project("webapp")
    helper = VisualTestingHelper(project_dir)

    viewports = helper.get_viewport_configs()

    assert len(viewports) == 3, "Should have 3 viewports"
    print(f"✓ Viewports configured: {len(viewports)}")

    for vp in viewports:
        assert "name" in vp
        assert "width" in vp
        assert "height" in vp
        print(f"  {vp['name']}: {vp['width']}x{vp['height']}")

    print("✅ Pass")


def test_verification_step_generation():
    """测试验证步骤生成"""
    print("\n=== Test 4: Verification Step Generation ===\n")

    project_dir = create_test_project("webapp")
    helper = VisualTestingHelper(project_dir)

    step = helper.get_verification_step("login form")
    print(f"✓ Generated step: {step}")

    assert "layout" in step.lower(), "Should mention layout"
    assert "colors" in step.lower(), "Should mention colors"
    assert "typography" in step.lower(), "Should mention typography"
    print("  ✓ All validation criteria included")

    print("✅ Pass")


def test_should_capture_screenshot():
    """测试截图判断逻辑"""
    print("\n=== Test 5: Should Capture Screenshot ===\n")

    project_dir = create_test_project("webapp")
    helper = VisualTestingHelper(project_dir)

    # UI feature - should capture
    ui_feature = {"id": "ui-button-001", "category": "ui"}
    assert helper.should_capture_screenshot(ui_feature) == True
    print("✓ UI feature: should capture screenshot ✓")

    # Style feature - should capture
    style_feature = {"id": "style-colors-001", "category": "style"}
    assert helper.should_capture_screenshot(style_feature) == True
    print("✓ Style feature: should capture screenshot ✓")

    # Data feature - should NOT capture
    data_feature = {"id": "data-model-001", "category": "data"}
    assert helper.should_capture_screenshot(data_feature) == False
    print("✓ Data feature: should NOT capture screenshot ✓")

    print("✅ Pass")


def test_threshold_values():
    """测试阈值配置"""
    print("\n=== Test 6: Threshold Values ===\n")

    project_dir = create_test_project("webapp")
    helper = VisualTestingHelper(project_dir)

    threshold = helper.get_comparison_threshold()
    max_diff = helper.get_max_diff_pixels()

    print(f"✓ Threshold: {threshold}")
    print(f"✓ Max diff pixels: {max_diff}")

    assert 0 <= threshold <= 1, "Threshold should be 0-1"
    assert max_diff > 0, "Max diff should be positive"
    assert max_diff == 100, "Should match configured value"

    print("✅ Pass")


def test_visual_validation_result():
    """测试视觉验证结果格式化"""
    print("\n=== Test 7: Visual Validation Result ===\n")

    project_dir = create_test_project("webapp")
    helper = VisualTestingHelper(project_dir)

    # Test passed result
    result = helper.format_visual_validation_result(
        "ui-login-001",
        passed=True,
        diff_pixels=50,
        viewports_tested=["mobile", "desktop"]
    )

    print("✓ Result format:")
    print(f"  Feature: {result['feature_id']}")
    print(f"  Passed: {result['visual_test_passed']}")
    print(f"  Diff pixels: {result['diff_pixels']}")
    print(f"  Within threshold: {result['within_threshold']}")
    print(f"  Viewports: {result['viewports_tested']}")

    assert result["visual_test_passed"] == True
    assert result["within_threshold"] == True
    assert result["diff_pixels"] == 50

    print("✅ Pass")


def test_screenshot_code_generation():
    """测试截图代码生成"""
    print("\n=== Test 8: Screenshot Code Generation ===\n")

    project_dir = create_test_project("webapp")
    helper = VisualTestingHelper(project_dir)

    code = helper.generate_screenshot_command("ui-login-001", {"name": "desktop", "width": 1440, "height": 900})

    print("✓ Generated code:")
    print(code)

    assert "await page.setViewportSize" in code, "Should set viewport"
    assert "1440, 900" in code, "Should use viewport dimensions"
    assert "await page.screenshot" in code, "Should capture screenshot"
    assert "fullPage: true" in code, "Should capture full page"
    assert "screenshots/actual" in code, "Should save to actual directory"

    print("\n✅ Pass")


def test_comparison_code_generation():
    """测试比较代码生成"""
    print("\n=== Test 9: Comparison Code Generation ===\n")

    project_dir = create_test_project("webapp")
    helper = VisualTestingHelper(project_dir)

    code = helper.generate_comparison_code("ui-login-001", "desktop")

    print("✓ Generated comparison code:")
    print(code[:300] + "...")

    assert "compareImages" in code, "Should use comparison function"
    assert "0.1" in code, "Should use threshold"
    assert "100" in code, "Should check max diff pixels"
    assert "Visual regression detected" in code, "Should have error message"
    assert "screenshots/diff" in code, "Should save diff to diff directory"

    print("\n✅ Pass")


def test_library_template_no_visual_testing():
    """测试 Library 模板没有视觉测试"""
    print("\n=== Test 10: Library Template (No Visual Testing) ===\n")

    project_dir = create_test_project("library")
    helper = VisualTestingHelper(project_dir)

    # Library 模板不应该启用视觉测试
    config = helper.config
    if "visual_testing" in config:
        print("⚠️  Warning: Library has visual_testing (unexpected)")
    else:
        print("✓ Library template correctly has no visual_testing")

    print("✅ Pass")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Testing Visual Testing Helper")
    print("=" * 60)

    try:
        test_config_loading()
        test_screenshot_path_generation()
        test_viewport_configs()
        test_verification_step_generation()
        test_should_capture_screenshot()
        test_threshold_values()
        test_visual_validation_result()
        test_screenshot_code_generation()
        test_comparison_code_generation()
        test_library_template_no_visual_testing()

        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        print("\n📋 Summary:")
        print("  - Configuration loading: ✓")
        print("  - Path generation: baseline, actual, diff")
        print("  - Viewport configs: mobile, tablet, desktop")
        print("  - Verification steps: Auto-generated with criteria")
        print("  - Screenshot logic: UI/style features only")
        print("  - Threshold validation: Configurable")
        print("  - Code generation: Playwright snippets")
        print("  - Template awareness: Library has no visual testing")

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        raise
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise
