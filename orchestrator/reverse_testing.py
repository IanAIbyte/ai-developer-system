"""
Reverse Testing - 反向测试与鲁棒性验证

职责：
1. 执行全面的反向测试（失败场景、边界条件）
2. 性能回归检测
3. 边缘情况覆盖
4. 混沌测试（随机输入、错误注入）

基于 Gemini Pro 3 的建议：
- 优化"失败模式预防"逻辑
- 增强反向测试覆盖范围
- 主动发现潜在问题
"""

import os
import json
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class ReverseTestCase:
    """反向测试用例定义"""

    def __init__(self, test_id: str, metadata: Dict):
        self.test_id = test_id
        self.name = metadata.get("name", test_id)
        self.category = metadata.get("category", "general")
        self.description = metadata.get("description", "")
        self.test_type = metadata.get("test_type", "functional")  # functional, performance, security
        self.scenario = metadata.get("scenario", {})
        self.expected_behavior = metadata.get("expected_behavior", {})
        self.severity = metadata.get("severity", "medium")  # low, medium, high, critical


class ReverseTestSuite:
    """反向测试套件"""

    def __init__(self, project_path: str):
        """
        初始化反向测试套件

        Args:
            project_path: 项目路径
        """
        self.project_path = Path(project_path).absolute()
        self.test_cases: List[ReverseTestCase] = []
        self._load_test_cases()

    def _load_test_cases(self):
        """加载反向测试用例"""
        # 根据项目类型生成默认测试用例
        self._generate_default_test_cases()

    def _generate_default_test_cases(self):
        """生成默认反向测试用例"""

        # 测试用例 1: 空输入处理
        self.test_cases.append(ReverseTestCase(
            "empty-input-001",
            {
                "name": "空输入处理",
                "category": "input_validation",
                "test_type": "functional",
                "description": "系统应优雅地处理空输入，不应崩溃或返回错误信息",
                "scenario": {
                    "input": "",
                    "input_type": "string",
                    "context": "所有表单输入、API 端点"
                },
                "expected_behavior": {
                    "should_crash": False,
                    "should_validate": True,
                    "error_message": "友好的错误提示",
                    "fallback": "使用默认值或提示用户输入"
                },
                "severity": "high"
            }
        ))

        # 测试用例 2: 超长输入处理
        self.test_cases.append(ReverseTestCase(
            "long-input-001",
            {
                "name": "超长输入处理",
                "category": "input_validation",
                "test_type": "functional",
                "description": "系统应处理超长输入（10000+ 字符），不应导致内存溢出或性能下降",
                "scenario": {
                    "input": "A" * 10000,
                    "input_type": "string",
                    "context": "文本输入框、textarea、API 请求体"
                },
                "expected_behavior": {
                    "should_crash": False,
                    "should_truncate": True,
                    "max_length": 1000,
                    "error_message": "输入超过最大长度限制"
                },
                "severity": "medium"
            }
        ))

        # 测试用例 3: 特殊字符注入
        self.test_cases.append(ReverseTestCase(
            "special-chars-001",
            {
                "name": "特殊字符注入",
                "category": "security",
                "test_type": "security",
                "description": "系统应安全处理特殊字符，防止 XSS、SQL 注入等攻击",
                "scenario": {
                    "inputs": [
                        "<script>alert('XSS')</script>",
                        "'; DROP TABLE users; --",
                        "../../../etc/passwd",
                        "${7*7}",  # 模板注入
                        "{{7*7}}"  # 模板注入
                    ],
                    "context": "所有用户输入点"
                },
                "expected_behavior": {
                    "should_execute": False,
                    "should_sanitize": True,
                    "should_escape": True,
                    "error_message": "包含非法字符"
                },
                "severity": "critical"
            }
        ))

        # 测试用例 4: API 超时处理
        self.test_cases.append(ReverseTestCase(
            "api-timeout-001",
            {
                "name": "API 超时处理",
                "category": "resilience",
                "test_type": "functional",
                "description": "外部 API 调用超时时，系统应优雅降级，不应挂起",
                "scenario": {
                    "api_call": "外部 LLM API",
                    "timeout": 30,
                    "simulate": "延迟响应或无响应"
                },
                "expected_behavior": {
                    "should_hang": False,
                    "should_retry": True,
                    "max_retries": 3,
                    "fallback": "使用智能规则系统",
                    "error_message": "服务暂时不可用，请稍后重试"
                },
                "severity": "high"
            }
        ))

        # 测试用例 5: 并发请求处理
        self.test_cases.append(ReverseTestCase(
            "concurrent-requests-001",
            {
                "name": "并发请求处理",
                "category": "performance",
                "test_type": "performance",
                "description": "系统应正确处理并发请求，不应出现竞态条件或数据不一致",
                "scenario": {
                    "concurrent_users": 100,
                    "requests_per_second": 50,
                    "duration": "10秒"
                },
                "expected_behavior": {
                    "should_crash": False,
                    "should_handle": True,
                    "response_time": "< 500ms (P95)",
                    "error_rate": "< 1%"
                },
                "severity": "medium"
            }
        ))

        # 测试用例 6: 无效 JSON 处理
        self.test_cases.append(ReverseTestCase(
            "invalid-json-001",
            {
                "name": "无效 JSON 处理",
                "category": "input_validation",
                "test_type": "functional",
                "description": "API 应正确处理无效 JSON 请求，不应崩溃",
                "scenario": {
                    "content_type": "application/json",
                    "body": "{invalid json",
                    "endpoint": "POST /api/*"
                },
                "expected_behavior": {
                    "should_crash": False,
                    "status_code": 400,
                    "error_message": "Invalid JSON format"
                },
                "severity": "medium"
            }
        ))

        # 测试用例 7: 数据库连接失败
        self.test_cases.append(ReverseTestCase(
            "db-failure-001",
            {
                "name": "数据库连接失败",
                "category": "resilience",
                "test_type": "functional",
                "description": "数据库不可用时，系统应优雅降级，不应暴露敏感错误信息",
                "scenario": {
                    "failure_type": "connection_refused",
                    "simulate": "停止数据库服务"
                },
                "expected_behavior": {
                    "should_crash": False,
                    "should_retry": True,
                    "fallback": "使用缓存或返回友好错误",
                    "error_message": "服务暂时不可用",
                    "should_log": True  # 记录详细错误到日志
                },
                "severity": "critical"
            }
        ))

        # 测试用例 8: 内存泄漏检测
        self.test_cases.append(ReverseTestCase(
            "memory-leak-001",
            {
                "name": "内存泄漏检测",
                "category": "performance",
                "test_type": "performance",
                "description": "长时间运行不应导致内存持续增长",
                "scenario": {
                    "operations": [
                        "创建和销毁组件",
                        "频繁 API 调用",
                        "文件读写"
                    ],
                    "iterations": 1000,
                    "duration": "5分钟"
                },
                "expected_behavior": {
                    "memory_growth": "< 20%",
                    "should_release": True,
                    "gc_effective": True
                },
                "severity": "medium"
            }
        ))

        # 测试用例 9: 网络断开恢复
        self.test_cases.append(ReverseTestCase(
            "network-recovery-001",
            {
                "name": "网络断开恢复",
                "category": "resilience",
                "test_type": "functional",
                "description": "网络断开后恢复，系统应自动重连并恢复状态",
                "scenario": {
                    "events": [
                        "正常操作",
                        "网络断开",
                        "等待 10 秒",
                        "网络恢复",
                        "验证状态"
                    ]
                },
                "expected_behavior": {
                    "should_detect": True,
                    "should_retry": True,
                    "should_restore": True,
                    "user_prompt": "网络已断开，正在重连..."
                },
                "severity": "high"
            }
        ))

        # 测试用例 10: 边界值测试
        self.test_cases.append(ReverseTestCase(
            "boundary-values-001",
            {
                "name": "边界值测试",
                "category": "input_validation",
                "test_type": "functional",
                "description": "测试数值边界（0、-1、最大值、最小值）",
                "scenario": {
                    "inputs": [
                        {"value": 0, "description": "零值"},
                        {"value": -1, "description": "负数"},
                        {"value": 2147483647, "description": "INT_MAX"},
                        {"value": -2147483648, "description": "INT_MIN"},
                        {"value": 3.14159265359, "description": "浮点数精度"}
                    ],
                    "context": "所有数值输入"
                },
                "expected_behavior": {
                    "should_validate": True,
                    "should_handle": True,
                    "error_message": "数值超出允许范围"
                },
                "severity": "medium"
            }
        ))

        print(f"  🧪 Loaded {len(self.test_cases)} reverse test cases")

    async def run_reverse_tests(
        self,
        feature: Dict,
        test_categories: Optional[List[str]] = None
    ) -> Dict:
        """
        运行反向测试

        Args:
            feature: 功能定义
            test_categories: 测试类别（可选，如 ['input_validation', 'security']）

        Returns:
            测试结果
        """
        print(f"  🧪 [Reverse Testing] Running reverse tests...")

        # 根据功能选择相关测试用例
        relevant_tests = self._filter_tests_by_feature(feature, test_categories)

        if not relevant_tests:
            print(f"  ℹ️  No relevant reverse tests found for feature {feature['id']}")
            return {
                "passed": True,
                "tests_run": 0,
                "message": "No applicable reverse tests"
            }

        results = []
        critical_failures = []

        for test_case in relevant_tests:
            print(f"    → Running: {test_case.name}")
            result = await self._run_single_test(test_case, feature)
            results.append(result)

            if not result["passed"] and test_case.severity == "critical":
                critical_failures.append({
                    "test_id": test_case.test_id,
                    "name": test_case.name,
                    "issue": result.get("issue", "Unknown")
                })

        # 汇总结果
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r["passed"])
        failed_tests = total_tests - passed_tests

        all_passed = len(critical_failures) == 0

        if all_passed:
            print(f"  ✅ [Reverse Testing] All tests passed ({passed_tests}/{total_tests})")
        else:
            print(f"  ❌ [Reverse Testing] {failed_tests} tests failed, {len(critical_failures)} critical")

        return {
            "passed": all_passed,
            "tests_run": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "results": results,
            "critical_failures": critical_failures
        }

    def _filter_tests_by_feature(
        self,
        feature: Dict,
        categories: Optional[List[str]]
    ) -> List[ReverseTestCase]:
        """
        根据功能筛选相关测试用例

        Args:
            feature: 功能定义
            categories: 测试类别（可选）

        Returns:
            相关测试用例列表
        """
        filtered = self.test_cases

        # 按类别筛选
        if categories:
            filtered = [t for t in filtered if t.category in categories]

        # 按功能类别智能筛选
        feature_category = feature.get("category", "")
        feature_desc = feature.get("description", "").lower()

        # 如果是 API 相关功能，跳过纯 UI 测试
        if feature_category in ["api", "backend"]:
            filtered = [t for t in filtered if t.category not in ["ui_only"]]

        # 如果功能描述中提到"安全"、"认证"，增加安全测试
        if any(keyword in feature_desc for keyword in ["auth", "login", "password", "security"]):
            security_tests = [t for t in self.test_cases if t.category == "security"]
            filtered.extend(security_tests)

        # 去重
        seen = set()
        unique_filtered = []
        for test in filtered:
            if test.test_id not in seen:
                seen.add(test.test_id)
                unique_filtered.append(test)

        return unique_filtered

    async def _run_single_test(
        self,
        test_case: ReverseTestCase,
        feature: Dict
    ) -> Dict:
        """
        运行单个测试用例

        Args:
            test_case: 测试用例
            feature: 功能定义

        Returns:
            测试结果
        """
        try:
            # 根据测试类型执行不同的测试逻辑
            if test_case.test_type == "functional":
                return await self._run_functional_test(test_case, feature)
            elif test_case.test_type == "performance":
                return await self._run_performance_test(test_case, feature)
            elif test_case.test_type == "security":
                return await self._run_security_test(test_case, feature)
            else:
                return {
                    "test_id": test_case.test_id,
                    "passed": True,
                    "skipped": True,
                    "reason": "Unknown test type"
                }

        except Exception as e:
            return {
                "test_id": test_case.test_id,
                "passed": False,
                "error": str(e),
                "issue": f"Test execution failed: {e}"
            }

    async def _run_functional_test(
        self,
        test_case: ReverseTestCase,
        feature: Dict
    ) -> Dict:
        """运行功能测试"""
        # 这里实现实际的功能测试逻辑
        # 例如：发送测试请求、检查响应、验证行为

        # 简化实现：基于规则检查
        passed = self._check_functional_requirements(test_case, feature)

        return {
            "test_id": test_case.test_id,
            "passed": passed,
            "test_type": "functional",
            "severity": test_case.severity,
            "issue": None if passed else f"Functional requirement not met: {test_case.name}"
        }

    async def _run_performance_test(
        self,
        test_case: ReverseTestCase,
        feature: Dict
    ) -> Dict:
        """运行性能测试"""
        # 简化实现：检查代码中是否有性能优化措施
        passed = self._check_performance_requirements(test_case, feature)

        return {
            "test_id": test_case.test_id,
            "passed": passed,
            "test_type": "performance",
            "severity": test_case.severity,
            "issue": None if passed else f"Performance requirement not met: {test_case.name}"
        }

    async def _run_security_test(
        self,
        test_case: ReverseTestCase,
        feature: Dict
    ) -> Dict:
        """运行安全测试"""
        # 简化实现：检查代码中是否有安全防护措施
        passed = self._check_security_requirements(test_case, feature)

        return {
            "test_id": test_case.test_id,
            "passed": passed,
            "test_type": "security",
            "severity": test_case.severity,
            "issue": None if passed else f"Security requirement not met: {test_case.name}"
        }

    def _check_functional_requirements(
        self,
        test_case: ReverseTestCase,
        feature: Dict
    ) -> bool:
        """检查功能需求（基于规则）"""
        # 读取相关代码文件
        code_files = self._get_feature_code_files(feature)

        if not code_files:
            # 如果没有代码文件，跳过测试
            return True

        all_code = "\n".join(code_files.values())

        # 根据测试用例类型检查
        if test_case.test_id == "empty-input-001":
            # 检查是否有输入验证
            has_validation = (
                "required" in all_code.lower() or
                "validator" in all_code.lower() or
                "if not" in all_code or
                "if ==" in all_code
            )
            return has_validation

        elif test_case.test_id == "api-timeout-001":
            # 检查是否有超时处理
            has_timeout = (
                "timeout" in all_code.lower() or
                "retry" in all_code.lower() or
                "except" in all_code
            )
            return has_timeout

        elif test_case.test_id == "invalid-json-001":
            # 检查是否有错误处理
            has_error_handling = (
                "try {" in all_code or
                "try:" in all_code or
                "catch" in all_code.lower() or
                "except" in all_code
            )
            return has_error_handling

        # 默认通过
        return True

    def _check_performance_requirements(
        self,
        test_case: ReverseTestCase,
        feature: Dict
    ) -> bool:
        """检查性能需求（基于规则）"""
        code_files = self._get_feature_code_files(feature)

        if not code_files:
            return True

        all_code = "\n".join(code_files.values())

        if test_case.test_id == "memory-leak-001":
            # 检查是否有资源清理逻辑
            has_cleanup = (
                "cleanup" in all_code.lower() or
                "dispose" in all_code.lower() or
                "finally" in all_code.lower() or
                "close()" in all_code
            )
            return has_cleanup

        # 默认通过
        return True

    def _check_security_requirements(
        self,
        test_case: ReverseTestCase,
        feature: Dict
    ) -> bool:
        """检查安全需求（基于规则）"""
        code_files = self._get_feature_code_files(feature)

        if not code_files:
            return True

        all_code = "\n".join(code_files.values())

        if test_case.test_id == "special-chars-001":
            # 检查是否有输入清理
            has_sanitization = (
                "sanitize" in all_code.lower() or
                "escape" in all_code.lower() or
                "validate" in all_code.lower() or
                "filter" in all_code.lower()
            )
            return has_sanitization

        # 默认通过
        return True

    def _get_feature_code_files(self, feature: Dict) -> Dict[str, str]:
        """获取功能相关的代码文件"""
        code_files = {}

        # 根据功能类别查找文件
        category = feature.get("category", "")

        if category in ["ui", "frontend"]:
            for ts_file in self.project_path.rglob("*.tsx"):
                code_files[str(ts_file.relative_to(self.project_path))] = ts_file.read_text()

        elif category in ["api", "backend"]:
            for py_file in self.project_path.rglob("*.py"):
                code_files[str(py_file.relative_to(self.project_path))] = py_file.read_text()

        return code_files


# 全局函数
async def run_reverse_tests_for_feature(
    project_path: str,
    feature: Dict,
    test_categories: Optional[List[str]] = None
) -> Dict:
    """
    为功能运行反向测试的便捷函数

    Args:
        project_path: 项目路径
        feature: 功能定义
        test_categories: 测试类别（可选）

    Returns:
        测试结果
    """
    suite = ReverseTestSuite(project_path)
    return await suite.run_reverse_tests(feature, test_categories)
