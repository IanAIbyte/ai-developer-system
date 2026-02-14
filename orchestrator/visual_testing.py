"""
Visual Testing Helper - 视觉测试辅助工具

提供截图捕获、视觉比较和回归检测功能。
可以与 Playwright/Puppeteer 集成使用。
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class VisualTestingHelper:
    """视觉测试辅助类"""

    def __init__(self, project_path: str):
        """
        初始化视觉测试辅助器

        Args:
            project_path: 项目根目录
        """
        self.project_path = Path(project_path)
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """加载测试配置"""
        config_path = self.project_path / ".claude" / "test_config.json"

        if not config_path.exists():
            return {}

        with open(config_path, 'r') as f:
            return json.load(f)

    def get_screenshot_path(
            self,
            feature_id: str,
            viewport: str = "desktop",
            type: str = "actual"
    ) -> Path:
        """
        获取截图文件路径

        Args:
            feature_id: 功能 ID（如 "ui-login-001"）
            viewport: 视口名称（mobile/tablet/desktop）
            type: 类型（baseline/actual/diff）

        Returns:
            截图文件完整路径
        """
        if not self.config.get("visual_testing", {}).get("enabled"):
            raise ValueError("Visual testing is not enabled in test_config.json")

        vt_config = self.config["visual_testing"]
        base_dir = vt_config.get(f"{type}_dir", f"screenshots/{type}")

        # 构建文件名：feature-viewport-timestamp.png
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"{feature_id}-{viewport}-{timestamp}.png"

        return self.project_path / base_dir / filename

    def get_baseline_path(self, feature_id: str, viewport: str = "desktop") -> Path:
        """获取 baseline 截图路径"""
        vt_config = self.config.get("visual_testing", {})
        baseline_dir = vt_config.get("baseline_dir", "screenshots/baseline")
        filename = f"{feature_id}-{viewport}.png"
        return self.project_path / baseline_dir / filename

    def get_diff_path(self, feature_id: str, viewport: str = "desktop") -> Path:
        """获取 diff 截图路径"""
        vt_config = self.config.get("visual_testing", {})
        diff_dir = vt_config.get("diff_dir", "screenshots/diff")
        filename = f"{feature_id}-{viewport}-diff.png"
        return self.project_path / diff_dir / filename

    def get_viewport_configs(self) -> List[Dict]:
        """获取所有视口配置"""
        vt_config = self.config.get("visual_testing", {})
        return vt_config.get("viewport_sizes", [
            {"name": "desktop", "width": 1440, "height": 900}
        ])

    def get_verification_step(self, feature_description: str) -> str:
        """
        生成视觉验证步骤文本

        Args:
            feature_description: 功能描述

        Returns:
            验证步骤文本
        """
        vt_config = self.config.get("visual_testing", {})
        validation = vt_config.get("validation_criteria", {})

        criteria = []
        if validation.get("layout"):
            criteria.append("layout is consistent")
        if validation.get("colors"):
            criteria.append("colors match design tokens")
        if validation.get("typography"):
            criteria.append("typography is correct")
        if validation.get("interactions"):
            criteria.append("component states are visible")

        if not criteria:
            return "Visually verify the feature is implemented correctly"

        return f"Verify {', '.join(criteria)} for {feature_description}"

    def should_capture_screenshot(self, feature: Dict) -> bool:
        """
        判断是否需要为功能捕获截图

        Args:
            feature: 功能字典

        Returns:
            是否需要截图
        """
        # 只有 UI 和 style 类别的功能需要截图
        category = feature.get("category", "")
        return category in ["ui", "style"]

    def get_viewports_for_feature(self, feature: Dict) -> List[str]:
        """
        根据功能获取需要测试的视口

        Args:
            feature: 功能字典

        Returns:
            视口名称列表
        """
        vt_config = self.config.get("visual_testing", {})

        # 默认测试所有视口
        viewports = vt_config.get("viewport_sizes", [])
        return [v["name"] for v in viewports]

    def get_comparison_threshold(self) -> float:
        """获取视觉比较阈值"""
        vt_config = self.config.get("visual_testing", {})
        return vt_config.get("comparison_threshold", 0.1)

    def get_max_diff_pixels(self) -> int:
        """获取最大允许差异像素数"""
        vt_config = self.config.get("visual_testing", {})
        return vt_config.get("max_diff_pixels", 100)

    def format_visual_validation_result(
            self,
            feature_id: str,
            passed: bool,
            diff_pixels: Optional[int] = None,
            viewports_tested: Optional[List[str]] = None
    ) -> Dict:
        """
        格式化视觉验证结果

        Args:
            feature_id: 功能 ID
            passed: 是否通过
            diff_pixels: 差异像素数
            viewports_tested: 测试的视口列表

        Returns:
            结果字典
        """
        result = {
            "feature_id": feature_id,
            "visual_test_passed": passed,
            "timestamp": datetime.now().isoformat()
        }

        if diff_pixels is not None:
            result["diff_pixels"] = diff_pixels
            threshold = self.get_max_diff_pixels()
            result["within_threshold"] = diff_pixels <= threshold

        if viewports_tested:
            result["viewports_tested"] = viewports_tested

        return result

    def generate_screenshot_command(
            self,
            feature_id: str,
            viewport: Dict,
            type: str = "actual"
    ) -> str:
        """
        生成 Playwright 截图命令

        Args:
            feature_id: 功能 ID
            viewport: 视口配置
            type: 类型

        Returns:
            Playwright 截图代码示例
        """
        output_path = self.get_screenshot_path(feature_id, viewport["name"], type)

        return f"""await page.setViewportSize({viewport['width']}, {viewport['height']});
await page.screenshot({{
    path: '{output_path.relative_to(self.project_path)}',
    fullPage: true
}});"""

    def generate_comparison_code(
            self,
            feature_id: str,
            viewport: str
    ) -> str:
        """
        生成视觉比较代码示例

        Args:
            feature_id: 功能 ID
            viewport: 视口名称

        Returns:
            比较代码示例
        """
        baseline_path = self.get_baseline_path(feature_id, viewport)
        actual_path = self.get_screenshot_path(feature_id, viewport, "actual")
        diff_path = self.get_diff_path(feature_id, viewport)

        return f"""// Visual comparison for {feature_id} ({viewport})
const baseline = await fs.readFile('{baseline_path.relative_to(self.project_path)}');
const actual = await fs.readFile('{actual_path.relative_to(self.project_path)}');

// Compare images using PixelMatch or similar library
const diff = await compareImages(baseline, actual, {{
    threshold: {self.get_comparison_threshold()}
}});

if (diff.differentPixels > {self.get_max_diff_pixels()}) {{
    await fs.writeFile('{diff_path.relative_to(self.project_path)}', diff.diffImage);
    throw new Error(`Visual regression detected: ${{diff.differentPixels}} pixels different`);
}}"""


def create_visual_test_helper(project_path: str) -> VisualTestingHelper:
    """
    工厂函数：创建视觉测试辅助器

    Args:
        project_path: 项目路径

    Returns:
        VisualTestingHelper 实例
    """
    return VisualTestingHelper(project_path)


# CLI 接口
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Visual Testing Helper - 视觉测试辅助工具"
    )
    parser.add_argument(
        "--project",
        required=True,
        help="Project directory path"
    )
    parser.add_argument(
        "--feature",
        required=True,
        help="Feature ID to test"
    )
    parser.add_argument(
        "--viewport",
        default="desktop",
        choices=["mobile", "tablet", "desktop"],
        help="Viewport to test"
    )
    parser.add_argument(
        "--action",
        choices=["path", "baseline", "code"],
        default="path",
        help="Action to perform"
    )

    args = parser.parse_args()

    helper = create_visual_test_helper(args.project)

    if args.action == "path":
        # 获取截图路径
        path = helper.get_screenshot_path(args.feature, args.viewport, "actual")
        print(f"Screenshot path: {path}")

    elif args.action == "baseline":
        # 获取 baseline 路径
        path = helper.get_baseline_path(args.feature, args.viewport)
        print(f"Baseline path: {path}")

    elif args.action == "code":
        # 生成截图代码
        viewports = helper.get_viewport_configs()
        viewport = next(v for v in viewports if v["name"] == args.viewport)
        code = helper.generate_screenshot_command(args.feature, viewport)
        print(f"Screenshot code for {args.viewport}:")
        print(code)
