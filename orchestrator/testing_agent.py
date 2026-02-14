"""
Testing Agent - Professional Testing Agent

Responsibilities:
1. Use LLM for intelligent test analysis and test case generation
2. Execute E2E tests and verify features
3. Intelligent failure diagnosis and fix recommendations
4. Generate detailed test reports
5. Integrate with Scheduler for automated testing workflow
"""

import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import sys

try:
    from .llm_clients import GLM5Client, get_llm_client
    from .mcp_client import PuppeteerE2ETester
except ImportError:
    from llm_clients import GLM5Client, get_llm_client
    from mcp_client import PuppeteerE2ETester


class TestCaseGenerator:
    """
    Test Case Generator

    Uses LLM to automatically generate test cases based on feature descriptions
    """

    def __init__(self, llm_client: GLM5Client):
        """
        Initialize test case generator

        Args:
            llm_client: LLM client
        """
        self.llm_client = llm_client

    def generate_test_cases(
            self,
            feature: Dict,
            context: Dict
    ) -> List[Dict]:
        """
        Generate detailed test cases for a feature

        Args:
            feature: Feature definition
            context: Project context

        Returns:
            List of test cases
        """
        feature_id = feature["id"]
        description = feature["description"]
        existing_steps = feature.get("e2e_steps", [])

        print(f"    [TestCaseGenerator] Generating test cases for {feature_id}")

        # Build test generation prompt
        prompt = self._build_test_generation_prompt(
            feature_id=feature_id,
            description=description,
            existing_steps=existing_steps,
            context=context
        )

        # Call LLM to generate test cases
        response = self.llm_client.chat_completion(
            messages=[
                {"role": "system", "content": "You are an expert QA engineer specializing in test case design and E2E testing."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=4096
        )

        if "error" in response or "choices" not in response:
            print(f"    [TestCaseGenerator] Warning: LLM generation failed, using fallback")
            return self._generate_fallback_test_cases(feature)

        # Parse generated test cases
        content = response["choices"][0]["message"]["content"]
        test_cases = self._parse_test_cases(content)

        print(f"    [TestCaseGenerator] Generated {len(test_cases)} test cases")
        return test_cases

    def _build_test_generation_prompt(
            self,
            feature_id: str,
            description: str,
            existing_steps: List[str],
            context: Dict
    ) -> str:
        """Build test case generation prompt"""
        return f"""
## Feature to Test

**Feature ID**: {feature_id}
**Description**: {description}

## Existing E2E Steps
{json.dumps(existing_steps, indent=2, ensure_ascii=False)}

## Project Context
**Tech Stack**: {context.get('tech_stack', 'Unknown')}
**Framework**: {context.get('framework', 'Unknown')}

## Task

Generate comprehensive test cases for this feature. For each test case, provide:

1. **Test Case ID**: Unique identifier (e.g., {feature_id}-tc-001)
2. **Title**: Brief description of what is being tested
3. **Preconditions**: What must be true before running test
4. **Test Steps**: Detailed step-by-step instructions
5. **Expected Result**: What should happen if feature works correctly
6. **Test Data**: Sample data to use (if applicable)

Focus on:
- **Happy Path**: Normal usage scenarios
- **Edge Cases**: Boundary conditions and unusual inputs
- **Error Cases**: Invalid inputs and error handling
- **Accessibility**: Testing for accessibility compliance
- **Performance**: Load and response time considerations

Format your output as JSON:
```json
{{
  "test_cases": [
    {{
      "id": "{feature_id}-tc-001",
      "title": "Test title",
      "category": "happy_path|edge_case|error_case|accessibility|performance",
      "priority": "critical|high|medium|low",
      "preconditions": ["Precondition 1", "Precondition 2"],
      "steps": ["Step 1", "Step 2", "Step 3"],
      "expected_result": "Description of expected result",
      "test_data": {{"key": "value"}}
    }}
  ]
}}
```
"""

    def _parse_test_cases(self, content: str) -> List[Dict]:
        """Parse LLM-generated test cases"""
        try:
            # Try to extract JSON
            start_idx = content.find("{")
            end_idx = content.rfind("}") + 1

            if start_idx >= 0 and end_idx > start_idx:
                json_str = content[start_idx:end_idx]
                data = json.loads(json_str)

                if "test_cases" in data:
                    return data["test_cases"]

            # If no test_cases found, return empty list
            return []

        except Exception as e:
            print(f"    [TestCaseGenerator] Parse error: {e}")
            return []

    def _generate_fallback_test_cases(self, feature: Dict) -> List[Dict]:
        """Generate fallback test cases (when LLM fails)"""
        feature_id = feature["id"]
        description = feature["description"]

        return [
            {
                "id": f"{feature_id}-tc-001",
                "title": f"Basic {description}",
                "category": "happy_path",
                "priority": "high",
                "preconditions": ["Application is running"],
                "steps": feature.get("e2e_steps", ["Verify feature is working"]),
                "expected_result": "Feature functions correctly"
            }
        ]


class TestResultAnalyzer:
    """
    Test Result Analyzer

    Uses LLM to analyze test failures and provide fix recommendations
    """

    def __init__(self, llm_client: GLM5Client):
        """
        Initialize test result analyzer

        Args:
            llm_client: LLM client
        """
        self.llm_client = llm_client

    def analyze_failure(
            self,
            feature: Dict,
            test_result: Dict,
            context: Dict
    ) -> Dict:
        """
        Analyze test failure causes

        Args:
            feature: Feature definition
            test_result: Test result
            context: Project context

        Returns:
            Analysis result (including fix recommendations)
        """
        feature_id = feature["id"]
        failed_step = self._extract_failed_step(test_result)

        print(f"    [TestResultAnalyzer] Analyzing failure for {feature_id}")

        # Build analysis prompt
        prompt = self._build_analysis_prompt(
            feature=feature,
            test_result=test_result,
            failed_step=failed_step,
            context=context
        )

        # Call LLM for analysis
        response = self.llm_client.chat_completion(
            messages=[
                {"role": "system", "content": "You are an expert debugging engineer specializing in web application testing and troubleshooting."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=4096
        )

        if "error" in response or "choices" not in response:
            return self._generate_fallback_analysis(test_result)

        # Parse analysis result
        content = response["choices"][0]["message"]["content"]
        analysis = self._parse_analysis(content)

        print(f"    [TestResultAnalyzer] Analysis complete")
        return analysis

    def _extract_failed_step(self, test_result: Dict) -> Optional[Dict]:
        """Extract failed step"""
        steps = test_result.get("steps", [])

        for step in steps:
            if not step.get("passed", True):
                return step

        return None

    def _build_analysis_prompt(
            self,
            feature: Dict,
            test_result: Dict,
            failed_step: Optional[Dict],
            context: Dict
    ) -> str:
        """Build analysis prompt"""
        return f"""
## Test Failure Analysis

**Feature ID**: {feature['id']}
**Feature Description**: {feature['description']}

**Test Result**:
```json
{json.dumps(test_result, indent=2, ensure_ascii=False)}
```

**Failed Step**:
```json
{json.dumps(failed_step, indent=2, ensure_ascii=False) if failed_step else "None"}
```

**Project Context**:
- Tech Stack: {context.get('tech_stack', 'Unknown')}
- Framework: {context.get('framework', 'Unknown')}

## Task

Analyze the test failure and provide:

1. **Root Cause**: What is causing this failure?
2. **Category**: Type of issue (bug, configuration, timeout, selector issue, etc.)
3. **Severity**: Impact level (critical, high, medium, low)
4. **Suggested Fixes**: Specific steps to fix the issue
5. **Verification Steps**: How to verify the fix works

Format your output as JSON:
```json
{{
  "root_cause": "Description of root cause",
  "category": "bug|configuration|timeout|selector|network|environment",
  "severity": "critical|high|medium|low",
  "suggested_fixes": [
    "Fix step 1",
    "Fix step 2"
  ],
  "verification_steps": [
    "Verification step 1",
    "Verification step 2"
  ]
}}
```
"""

    def _parse_analysis(self, content: str) -> Dict:
        """Parse analysis result"""
        try:
            start_idx = content.find("{")
            end_idx = content.rfind("}") + 1

            if start_idx >= 0 and end_idx > start_idx:
                json_str = content[start_idx:end_idx]
                return json.loads(json_str)

        except Exception as e:
            print(f"    [TestResultAnalyzer] Parse error: {e}")

        # Return fallback analysis
        return {
            "root_cause": "Unable to analyze with LLM",
            "category": "unknown",
            "severity": "medium",
            "suggested_fixes": ["Review test logs"],
            "verification_steps": ["Re-run test"]
        }

    def _generate_fallback_analysis(self, test_result: Dict) -> Dict:
        """Generate fallback analysis"""
        return {
            "root_cause": test_result.get("error", "Unknown error"),
            "category": "unknown",
            "severity": "medium",
            "suggested_fixes": ["Check application logs", "Verify test steps"],
            "verification_steps": ["Re-run test after investigation"]
        }


class TestingAgent:
    """
    Testing Agent - Professional Testing Agent

    Responsibilities:
    1. Intelligent test case generation
    2. E2E test execution
    3. Test failure analysis
    4. Fix recommendations
    5. Test report generation
    """

    def __init__(
            self,
            project_path: str,
            llm_provider: str = "glm-5",
            base_url: str = "http://localhost:3000"
    ):
        """
        Initialize testing agent

        Args:
            project_path: Project path
            llm_provider: LLM provider
            base_url: Application base URL
        """
        self.project_path = Path(project_path).absolute()
        self.base_url = base_url

        # Initialize LLM client
        try:
            self.llm_client = get_llm_client(llm_provider)
            print(f"    [TestingAgent] Using {llm_provider.upper()} for intelligent testing")
        except Exception as e:
            print(f"    [TestingAgent] Warning: LLM client initialization failed: {e}")
            self.llm_client = None

        # Initialize components
        self.test_case_generator = None
        self.result_analyzer = None

        if self.llm_client:
            self.test_case_generator = TestCaseGenerator(self.llm_client)
            self.result_analyzer = TestResultAnalyzer(self.llm_client)

        # E2E tester
        self.e2e_tester: Optional[PuppeteerE2ETester] = None

        # Test statistics
        self.test_statistics = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0
        }

    def test_feature(
            self,
            feature: Dict,
            context: Dict,
            use_llm: bool = True
    ) -> Dict:
        """
        Test a single feature

        Args:
            feature: Feature definition
            context: Project context
            use_llm: Whether to use LLM for enhanced testing

        Returns:
            Test result
        """
        feature_id = feature["id"]
        description = feature["description"]

        print(f"    [TestingAgent] Testing: {description}")
        print(f"    [TestingAgent] Feature ID: {feature_id}")

        # Generate test cases
        test_cases = []

        if use_llm and self.test_case_generator:
            test_cases = self.test_case_generator.generate_test_cases(
                feature=feature,
                context=context
            )
        else:
            # Use basic E2E steps
            test_cases = [
                {
                    "id": f"{feature_id}-tc-001",
                    "title": description,
                    "category": "happy_path",
                    "priority": "high",
                    "steps": feature.get("e2e_steps", []),
                    "expected_result": "Feature works as expected"
                }
            ]

        # Start E2E tester
        if not self.e2e_tester:
            self.e2e_tester = PuppeteerE2ETester(
                project_path=str(self.project_path),
                base_url=self.base_url
            )

            if not self.e2e_tester.start():
                return {
                    "feature_id": feature_id,
                    "passed": False,
                    "error": "Failed to start E2E tester"
                }

        try:
            # Execute test cases
            feature_passed = True
            test_case_results = []

            for test_case in test_cases:
                print(f"    [TestingAgent] Running: {test_case['title']}")

                result = self._execute_test_case(
                    feature=feature,
                    test_case=test_case,
                    context=context
                )

                test_case_results.append(result)

                if not result["passed"]:
                    feature_passed = False

                    # Use LLM to analyze failure
                    if use_llm and self.result_analyzer:
                        analysis = self.result_analyzer.analyze_failure(
                            feature=feature,
                            test_result=result,
                            context=context
                        )
                        result["analysis"] = analysis

            # Update statistics
            self.test_statistics["total"] += len(test_cases)
            self.test_statistics["passed"] += sum(1 for r in test_case_results if r["passed"])
            self.test_statistics["failed"] += sum(1 for r in test_case_results if not r["passed"])

            return {
                "feature_id": feature_id,
                "passed": feature_passed,
                "test_cases": test_case_results,
                "summary": {
                    "total": len(test_cases),
                    "passed": sum(1 for r in test_case_results if r["passed"]),
                    "failed": sum(1 for r in test_case_results if not r["passed"])
                }
            }

        finally:
            # Note: Don't stop E2E tester, may be used for subsequent tests
            pass

    def _execute_test_case(
            self,
            feature: Dict,
            test_case: Dict,
            context: Dict
    ) -> Dict:
        """
        Execute a single test case

        Args:
            feature: Feature definition
            test_case: Test case
            context: Context

        Returns:
            Test result
        """
        test_case_id = test_case["id"]
        steps = test_case.get("steps", [])

        # Use E2E tester to execute steps
        if self.e2e_tester:
            result = self.e2e_tester.execute_e2e_steps(
                feature_id=test_case_id,
                e2e_steps=steps,
                context=context
            )

            # Add test case info
            result["test_case_id"] = test_case_id
            result["title"] = test_case.get("title", "")

            return result
        else:
            # Fallback implementation
            return {
                "test_case_id": test_case_id,
                "title": test_case.get("title", ""),
                "passed": False,
                "error": "E2E tester not available"
            }

    def test_batch_features(
            self,
            features: List[Dict],
            context: Dict,
            use_llm: bool = True
    ) -> Dict:
        """
        Test features in batch

        Args:
            features: List of features
            context: Project context
            use_llm: Whether to use LLM enhancement

        Returns:
            Batch test results
        """
        print(f"    [TestingAgent] Testing batch of {len(features)} features")

        results = {
            "total": len(features),
            "passed": 0,
            "failed": 0,
            "details": []
        }

        # Start E2E test environment
        if not self.e2e_tester:
            self.e2e_tester = PuppeteerE2ETester(
                project_path=str(self.project_path),
                base_url=self.base_url
            )

        if not self.e2e_tester.start():
            return {
                **results,
                "error": "Failed to start E2E test environment"
            }

        try:
            for feature in features:
                test_result = self.test_feature(
                    feature=feature,
                    context=context,
                    use_llm=use_llm
                )

                results["details"].append(test_result)

                if test_result["passed"]:
                    results["passed"] += 1
                else:
                    results["failed"] += 1

        finally:
            # Stop E2E test environment
            if self.e2e_tester:
                self.e2e_tester.stop()

        # Generate test report
        report = self._generate_detailed_report(results)
        self._save_test_report(report)

        print(f"    [TestingAgent] Batch testing complete")
        print(f"    [TestingAgent]    Passed: {results['passed']}/{results['total']}")
        print(f"    [TestingAgent]    Failed: {results['failed']}/{results['total']}")

        return results

    def _generate_detailed_report(self, results: Dict) -> Dict:
        """
        Generate detailed test report

        Args:
            results: Test results

        Returns:
            Detailed report
        """
        total = results["total"]
        passed = results["passed"]
        failed = results["failed"]

        report = {
            "summary": {
                "total_features": total,
                "passed_features": passed,
                "failed_features": failed,
                "pass_rate": f"{(passed/total*100):.1f}%" if total > 0 else "0%"
            },
            "statistics": self.test_statistics,
            "feature_results": results["details"],
            "generated_at": datetime.now().isoformat(),
            "agent_version": "1.0.0"
        }

        # Add failure analysis and fix recommendations
        failed_features = [
            r for r in results["details"] if not r["passed"]
        ]

        if failed_features:
            report["failures"] = {
                "count": len(failed_features),
                "details": failed_features
            }

        return report

    def _save_test_report(self, report: Dict):
        """
        Save test report

        Args:
            report: Test report
        """
        report_path = self.project_path / "testing_report.json"

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"    [TestingAgent] Test report saved: {report_path}")

    def cleanup(self):
        """Clean up resources"""
        if self.e2e_tester:
            self.e2e_tester.stop()
            self.e2e_tester = None
