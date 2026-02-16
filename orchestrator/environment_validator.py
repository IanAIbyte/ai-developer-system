"""
Environment Validator - 环境完整性验证器

职责：
1. 强制环境完整性检查
2. 防止"空城计"（文件缺失但标记完成）
3. 反向测试（鲁棒性验证）
4. 失败模式预防
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional


class EnvironmentValidator:
    """环境完整性验证器"""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path).absolute()

    def validate_before_completion(
        self,
        feature: Dict,
        implementation_result: Dict
    ) -> Dict:
        """
        在标记功能为完成之前执行验证

        Args:
            feature: 功能定义
            implementation_result: 实现结果

        Returns:
            验证结果
        """
        print("  🔍 [Environment Validator] Running pre-completion checks...")

        checks = {
            "critical_files_exist": self._check_critical_files(feature),
            "no_empty_placeholders": self._check_no_empty_placeholders(),
            "actual_code_content": self._check_actual_code_content(),
            "integration_points": self._check_integration_points(feature)
        }

        all_passed = all(check["passed"] for check in checks.values())

        if not all_passed:
            failed_checks = [name for name, check in checks.items() if not check["passed"]]
            print(f"  ❌ [Environment Validator] Validation failed: {', '.join(failed_checks)}")

            return {
                "passed": False,
                "checks": checks,
                "reason": "Environment validation failed"
            }

        print("  ✅ [Environment Validator] All checks passed")
        return {"passed": True, "checks": checks}

    def _check_critical_files(self, feature: Dict) -> Dict:
        """
        检查关键文件是否存在

        根据功能类型确定必须存在的文件
        """
        category = feature.get("category", "")
        required_files = []

        # 根据类别确定必需文件
        if category in ["ui", "frontend"]:
            required_files = ["package.json"]
        elif category in ["api", "backend"]:
            required_files = ["requirements.txt", "main.py"]
        elif category == "setup":
            required_files = ["package.json", "requirements.txt"]

        missing_files = []
        for file in required_files:
            if not (self.project_path / file).exists():
                missing_files.append(file)

        if missing_files:
            return {
                "passed": False,
                "reason": f"Critical files missing: {', '.join(missing_files)}",
                "missing_files": missing_files
            }

        return {"passed": True}

    def _check_no_empty_placeholders(self) -> Dict:
        """
        检查是否只有空占位符文件

        检测：
        - .md 文件包含 "TODO" 或 "PLACEHOLDER"
        - .tsx/.ts 文件内容过少（< 50 字符）
        """
        placeholder_patterns = ["TODO", "PLACEHOLDER", "NOT IMPLEMENTED", "Required"]
        suspicious_files = []

        # 检查 TypeScript/React 文件
        for ts_file in self.project_path.rglob("*.tsx"):
            content = ts_file.read_text()
            if len(content.strip()) < 50:
                suspicious_files.append({
                    "file": str(ts_file.relative_to(self.project_path)),
                    "reason": "File too short (possibly placeholder)",
                    "length": len(content.strip())
                })

        # 检查 Markdown 文件
        for md_file in self.project_path.rglob("*.md"):
            content = md_file.read_text()
            for pattern in placeholder_patterns:
                if pattern in content.upper():
                    suspicious_files.append({
                        "file": str(md_file.relative_to(self.project_path)),
                        "reason": f"Contains placeholder pattern: {pattern}"
                    })

        if suspicious_files:
            return {
                "passed": False,
                "reason": "Placeholder files detected",
                "files": suspicious_files
            }

        return {"passed": True}

    def _check_actual_code_content(self) -> Dict:
        """
        检查是否有实际的代码内容

        不能只有文档，必须有可执行代码
        """
        code_files = []
        doc_files = []

        for file in self.project_path.rglob("*"):
            if file.is_file():
                suffix = file.suffix
                if suffix in [".tsx", ".ts", ".jsx", ".js", ".py"]:
                    code_files.append(file)
                elif suffix in [".md"]:
                    doc_files.append(file)

        # 必须有代码文件
        if not code_files:
            return {
                "passed": False,
                "reason": "No code files found, only documentation"
            }

        # 检查代码文件是否实际包含代码
        empty_code_files = []
        for code_file in code_files:
            if code_file.stat().st_size < 100:  # 小于 100 字节
                empty_code_files.append(str(code_file.relative_to(self.project_path)))

        if empty_code_files:
            return {
                "passed": False,
                "reason": "Code files appear to be empty",
                "files": empty_code_files
            }

        return {
            "passed": True,
            "code_files_count": len(code_files),
            "doc_files_count": len(doc_files)
        }

    def _check_integration_points(self, feature: Dict) -> Dict:
        """
        检查集成点

        例如：如果功能是"添加 API 调用"，必须检查：
        - 是否真的有 fetch/axios 调用
        - 是否有 API endpoint 配置
        """
        category = feature.get("category", "")
        description = feature.get("description", "").lower()

        # 检查 API 集成
        if "api" in description or "backend" in description:
            tsx_files = list(self.project_path.rglob("*.tsx"))
            has_api_calls = False

            for tsx_file in tsx_files:
                content = tsx_file.read_text()
                if "fetch(" in content or "axios." in content:
                    has_api_calls = True
                    break

            if not has_api_calls:
                return {
                    "passed": False,
                    "reason": "Feature requires API integration but no API calls found"
                }

        # 检查状态管理集成
        if "state" in description or "store" in description:
            tsx_files = list(self.project_path.rglob("*.tsx"))
            has_state = False

            for tsx_file in tsx_files:
                content = tsx_file.read_text()
                if "useState" in content or "useStore" in content:
                    has_state = True
                    break

            if not has_state:
                return {
                    "passed": False,
                    "reason": "Feature mentions state but no state management found"
                }

        return {"passed": True}

    def run_reverse_tests(self, feature: Dict) -> Dict:
        """
        运行反向测试（鲁棒性验证）

        测试场景：
        1. 空输入处理
        2. 错误输入处理
        3. 边界条件
        """
        print("  🧪 [Environment Validator] Running reverse tests...")

        test_results = []

        # 测试1: 空输入
        if feature.get("category") == "ui":
            test_results.append(self._test_empty_input_handling(feature))

        # 测试2: API 错误处理
        if "api" in feature.get("description", "").lower():
            test_results.append(self._test_api_error_handling())

        passed = all(test["passed"] for test in test_results if test)

        if passed:
            print("  ✅ [Environment Validator] Reverse tests passed")
        else:
            print("  ⚠️  [Environment Validator] Some reverse tests failed")

        return {"passed": passed, "tests": test_results}

    def _test_empty_input_handling(self, feature: Dict) -> Dict:
        """
        测试空输入处理

        检查代码是否有输入验证
        """
        # 检查表单验证逻辑
        tsx_files = list(self.project_path.rglob("*.tsx"))

        has_validation = False
        for tsx_file in tsx_files:
            content = tsx_file.read_text()
            if "required" in content or "validator" in content.lower():
                has_validation = True
                break

        return {
            "name": "Empty Input Test",
            "passed": has_validation,
            "details": "Form validation found" if has_validation else "No input validation"
        }

    def _test_api_error_handling(self) -> Dict:
        """
        测试 API 错误处理

        检查是否有 try-catch 或错误处理
        """
        tsx_files = list(self.project_path.rglob("*.tsx"))
        py_files = list(self.project_path.rglob("*.py"))

        has_error_handling = False

        for file in tsx_files + py_files:
            content = file.read_text()
            if "try {" in content or "try:" in content or "catch" in content:
                has_error_handling = True
                break

        return {
            "name": "API Error Handling Test",
            "passed": has_error_handling,
            "details": "Error handling found" if has_error_handling else "No error handling"
        }


# 全局验证函数
def validate_environment(project_path: str, feature: Dict, implementation_result: Dict) -> Dict:
    """
    便捷函数：验证环境并返回结果

    Returns:
        {
            "passed": bool,
            "can_mark_complete": bool,
            "checks": dict,
            "warnings": list
        }
    """
    validator = EnvironmentValidator(project_path)
    result = validator.validate_before_completion(feature, implementation_result)

    return result
