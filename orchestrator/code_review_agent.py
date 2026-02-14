"""
Code Review Agent - Professional Code Review Agent

Responsibilities:
1. Use LLM for intelligent code review
2. Security vulnerability scanning
3. Best practices enforcement
4. Performance optimization suggestions
5. Git workflow integration
"""

import json
import subprocess
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import re

try:
    from .llm_clients import GLM5Client, get_llm_client
except ImportError:
    from llm_clients import GLM5Client, get_llm_client


class SecurityScanner:
    """
    Security Scanner

    Scans code for security vulnerabilities and OWASP Top 10 issues
    """

    # OWASP Top 10 patterns (simplified regex-based detection)
    SECURITY_PATTERNS = {
        "sql_injection": [
            r"execute\s*\(\s*['\"]SELECT\s+.*\+\s*",
            r"query\s*=\s*['\"]SELECT\s+.*\+\s*",
            r"\.execute\(['\"].*SELECT",
            r"cursor\.execute\s*\(\s*f['\"]?\s*.*\+\s*"
        ],
        "xss": [
            r"innerHTML\s*=\s*[^;]*[^;]*request\.",
            r"dangerouslySetInnerHTML",
            r"\.html\s*\(\s*[^;]*request\.",
            r"document\.write\s*\(\s*[^;]*request\."
        ],
        "hardcoded_secrets": [
            r"api[_-]?key\s*=\s*['\"][\w-]{20,}['\"]",
            r"password\s*=\s*['\"][\w-]{8,}['\"]",
            r"secret\s*=\s*['\"][\w-]{16,}['\"]",
            r"token\s*=\s*['\"][\w-]{20,}['\"]",
            r"Bearer\s+[a-zA-Z0-9]{20,}"
        ],
        "command_injection": [
            r"exec\s*\(\s*[^;]*request\.",
            r"spawn\s*\(\s*[^;]*request\.",
            r"system\s*\(\s*[^;]*request\.",
            r"subprocess\.(call|run|Popen)\s*\(\s*[^)]*request\."
        ],
        "path_traversal": [
            r"open\s*\(\s*[^)]*\.\.[/\\]",
            r"readFile\s*\(\s*[^)]*\.\.[/\\]",
            r"fs\.readFileSync\s*\(\s*[^)]*\.\.[/\\]"
        ],
        "insecure_deserialization": [
            r"pickle\.loads",
            r"marshal\.loads",
            r"yaml\.load\s*\(\s*[^,)]",
            r"JSON\.parse\s*\(\s*[^)]*request\."
        ],
        "crypto_issues": [
            r"md4\s*\(",
            r"sha1\s*\(",
            r"RC4\s*\(",
            r"DES\s*\(",
            r"ecb\s*=\s*['\"]crypto"
        ]
    }

    def __init__(self, llm_client: GLM5Client):
        """
        Initialize security scanner

        Args:
            llm_client: LLM client for intelligent analysis
        """
        self.llm_client = llm_client

    def scan_code(
            self,
            file_path: str,
            content: str,
            language: str
    ) -> Dict:
        """
        Scan code for security vulnerabilities

        Args:
            file_path: File path
            content: File content
            language: Programming language

        Returns:
            Scan results with vulnerabilities found
        """
        print(f"    [SecurityScanner] Scanning {file_path}")

        vulnerabilities = []

        # Pattern-based detection
        for vuln_type, patterns in self.SECURITY_PATTERNS.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    line_content = content.split('\n')[line_num - 1].strip()

                    vulnerabilities.append({
                        "type": vuln_type,
                        "severity": self._get_severity(vuln_type),
                        "line": line_num,
                        "code_snippet": line_content[:100],
                        "pattern_matched": pattern
                    })

        # LLM-enhanced analysis for critical issues
        critical_vulns = [v for v in vulnerabilities if v["severity"] == "critical"]

        if critical_vulns and self.llm_client:
            print(f"    [SecurityScanner] Analyzing {len(critical_vulns)} critical vulns with LLM")

            llm_analysis = self._llm_analyze_vulnerabilities(
                file_path=file_path,
                vulnerabilities=critical_vulns,
                content=content,
                language=language
            )

            # Enhance with LLM suggestions
            for vuln in vulnerabilities:
                if vuln in critical_vulns:
                    vuln["llm_analysis"] = llm_analysis.get(vuln["type"], {})
                    vuln["fix_suggestions"] = llm_analysis.get("fix_suggestions", [])

        return {
            "file_path": file_path,
            "language": language,
            "vulnerabilities": vulnerabilities,
            "total": len(vulnerabilities),
            "by_severity": self._count_by_severity(vulnerabilities),
            "scanned_at": datetime.now().isoformat()
        }

    def _get_severity(self, vuln_type: str) -> str:
        """Get severity level for vulnerability type"""
        severity_map = {
            "sql_injection": "critical",
            "xss": "critical",
            "hardcoded_secrets": "critical",
            "command_injection": "critical",
            "path_traversal": "high",
            "insecure_deserialization": "high",
            "crypto_issues": "medium"
        }
        return severity_map.get(vuln_type, "medium")

    def _count_by_severity(self, vulnerabilities: List[Dict]) -> Dict[str, int]:
        """Count vulnerabilities by severity"""
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for vuln in vulnerabilities:
            severity = vuln.get("severity", "low")
            counts[severity] = counts.get(severity, 0) + 1
        return counts

    def _llm_analyze_vulnerabilities(
            self,
            file_path: str,
            vulnerabilities: List[Dict],
            content: str,
            language: str
    ) -> Dict:
        """
        Use LLM to analyze critical vulnerabilities

        Args:
            file_path: File path
            vulnerabilities: List of critical vulnerabilities
            content: File content
            language: Programming language

        Returns:
            LLM analysis with fix suggestions
        """
        vuln_types = list(set(v["type"] for v in vulnerabilities))

        prompt = f"""
## Security Vulnerability Analysis

**File**: {file_path}
**Language**: {language}
**Vulnerability Types**: {', '.join(vuln_types)}

## Vulnerabilities Found
{json.dumps(vulnerabilities, indent=2, ensure_ascii=False)}

## Context (excerpt)
```{language}
{content[:2000]}
```

## Task

For each vulnerability type, provide:
1. **Explanation**: Why is this a security risk?
2. **Attack Scenario**: How could an attacker exploit this?
3. **Fix Strategy**: Best practice to remediate
4. **Code Example**: Secure implementation example
5. **Verification**: How to test that the fix works

Format your output as JSON:
```json
{{
  "vulnerability_analyses": {{
    "{vuln_types[0] if vuln_types else 'generic'}": {{
      "explanation": "Detailed explanation",
      "attack_scenario": "How attacker could exploit",
      "fix_strategy": "Best practice for remediation",
      "code_example": "Secure implementation",
      "verification": "How to verify fix"
    }}
  }},
  "fix_suggestions": [
    "Specific actionable fix 1",
    "Specific actionable fix 2"
  ]
}}
```
"""

        response = self.llm_client.chat_completion(
            messages=[
                {"role": "system", "content": "You are an expert security analyst specializing in OWASP Top 10 vulnerabilities and secure coding practices."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=4096
        )

        if "error" in response or "choices" not in response:
            return {}

        content = response["choices"][0]["message"]["content"]

        try:
            start_idx = content.find("{")
            end_idx = content.rfind("}") + 1

            if start_idx >= 0 and end_idx > start_idx:
                json_str = content[start_idx:end_idx]
                return json.loads(json_str)
        except Exception as e:
            print(f"    [SecurityScanner] Warning: Failed to parse LLM analysis: {e}")

        return {}


class CodeQualityChecker:
    """
    Code Quality Checker

    Checks code against best practices and common anti-patterns
    """

    # Code quality anti-patterns
    QUALITY_PATTERNS = {
        "long_function": {
            "pattern": r"def\s+\w+\s*\([^)]*\)\s*:\s*\n((?:\s{4}.*\n){{50,}}",
            "severity": "medium",
            "message": "Function exceeds 50 lines, consider splitting"
        },
        "deep_nesting": {
            "pattern": r"\s{20,}",
            "severity": "low",
            "message": "Deep nesting (>5 levels) detected, consider refactoring"
        },
        "magic_numbers": {
            "pattern": r"(?<![\w])([0-9]+)(?![\w])",
            "severity": "low",
            "message": "Magic number detected, use named constant"
        },
        "console_log": {
            "pattern": r"console\.log\s*\(",
            "severity": "low",
            "message": "Console.log statement found in production code"
        },
        "TODO_comment": {
            "pattern": r"TODO|FIXME|HACK|XXX",
            "severity": "low",
            "message": "Outstanding TODO/FIXME comment found"
        },
        "large_file": {
            "pattern": None,  # Checked separately
            "severity": "medium",
            "message": "File exceeds 800 lines, consider splitting"
        },
        "duplicate_code": {
            "pattern": None,  # Requires AST analysis
            "severity": "medium",
            "message": "Duplicate code detected"
        },
        "unused_import": {
            "pattern": None,  # Requires AST analysis
            "severity": "low",
            "message": "Unused import detected"
        }
    }

    def __init__(self, llm_client: GLM5Client):
        """
        Initialize code quality checker

        Args:
            llm_client: LLM client for intelligent analysis
        """
        self.llm_client = llm_client

    def check_quality(
            self,
            file_path: str,
            content: str,
            language: str
    ) -> Dict:
        """
        Check code quality and best practices

        Args:
            file_path: File path
            content: File content
            language: Programming language

        Returns:
            Quality check results
        """
        print(f"    [CodeQualityChecker] Checking {file_path}")

        issues = []

        # Check file length
        lines = content.split('\n')
        if len(lines) > 800:
            issues.append({
                "type": "large_file",
                "severity": "medium",
                "line": len(lines),
                "message": f"File has {len(lines)} lines, exceeds recommended 800"
            })

        # Pattern-based checks
        for issue_type, config in self.QUALITY_PATTERNS.items():
            if config["pattern"] is None:
                continue

            pattern = config["pattern"]
            matches = re.finditer(pattern, content, re.MULTILINE)

            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                line_content = content.split('\n')[line_num - 1].strip()

                issues.append({
                    "type": issue_type,
                    "severity": config["severity"],
                    "line": line_num,
                    "message": config["message"],
                    "code_snippet": line_content[:100]
                })

        # LLM-enhanced quality analysis
        if issues and self.llm_client:
            print(f"    [CodeQualityChecker] Analyzing {len(issues)} issues with LLM")

            llm_analysis = self._llm_analyze_quality(
                file_path=file_path,
                issues=issues,
                content=content,
                language=language
            )

            # Enhance with LLM suggestions
            for issue in issues:
                issue["llm_analysis"] = llm_analysis.get("refactoring_suggestions", [])
                issue["best_practice"] = llm_analysis.get("best_practices", {})

        return {
            "file_path": file_path,
            "language": language,
            "lines": len(lines),
            "issues": issues,
            "total": len(issues),
            "by_severity": self._count_by_severity(issues),
            "checked_at": datetime.now().isoformat()
        }

    def _count_by_severity(self, issues: List[Dict]) -> Dict[str, int]:
        """Count issues by severity"""
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for issue in issues:
            severity = issue.get("severity", "low")
            counts[severity] = counts.get(severity, 0) + 1
        return counts

    def _llm_analyze_quality(
            self,
            file_path: str,
            issues: List[Dict],
            content: str,
            language: str
    ) -> Dict:
        """
        Use LLM to analyze code quality issues

        Args:
            file_path: File path
            issues: List of quality issues
            content: File content
            language: Programming language

        Returns:
            LLM analysis with refactoring suggestions
        """
        issue_types = list(set(i["type"] for i in issues))

        prompt = f"""
## Code Quality Analysis

**File**: {file_path}
**Language**: {language}
**Issues Found**: {len(issues)}
**Issue Types**: {', '.join(issue_types)}

## Issues
{json.dumps(issues[:10], indent=2, ensure_ascii=False)}

## Context (excerpt)
```{language}
{content[:2000]}
```

## Task

Provide:
1. **Refactoring Suggestions**: Specific improvements
2. **Best Practices**: What should be done instead
3. **Priority**: Which issues to fix first
4. **Code Examples**: Better implementations

Format your output as JSON:
```json
{{
  "refactoring_suggestions": [
    "Specific actionable refactoring 1",
    "Specific actionable refactoring 2"
  ],
  "best_practices": {{
    "clean_code": "Principles to follow",
    "solid_principles": "SOLID adherence",
    "design_patterns": "Applicable patterns"
  }}
}}
```
"""

        response = self.llm_client.chat_completion(
            messages=[
                {"role": "system", "content": "You are an expert code quality analyst specializing in clean code, SOLID principles, and refactoring."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=4096
        )

        if "error" in response or "choices" not in response:
            return {}

        content = response["choices"][0]["message"]["content"]

        try:
            start_idx = content.find("{")
            end_idx = content.rfind("}") + 1

            if start_idx >= 0 and end_idx > start_idx:
                json_str = content[start_idx:end_idx]
                return json.loads(json_str)
        except Exception as e:
            print(f"    [CodeQualityChecker] Warning: Failed to parse LLM analysis: {e}")

        return {}


class CodeReviewAgent:
    """
    Code Review Agent - Professional Code Review Agent

    Responsibilities:
    1. Comprehensive code review using LLM
    2. Security vulnerability scanning
    3. Code quality and best practices checking
    4. Performance optimization suggestions
    5. Git workflow integration
    """

    def __init__(
            self,
            project_path: str,
            llm_provider: str = "glm-5"
    ):
        """
        Initialize code review agent

        Args:
            project_path: Project path
            llm_provider: LLM provider
        """
        self.project_path = Path(project_path).absolute()

        # Initialize LLM client
        try:
            self.llm_client = get_llm_client(llm_provider)
            print(f"    [CodeReviewAgent] Using {llm_provider.upper()} for code review")
        except Exception as e:
            print(f"    [CodeReviewAgent] Warning: LLM client initialization failed: {e}")
            self.llm_client = None

        # Initialize components
        if self.llm_client:
            self.security_scanner = SecurityScanner(self.llm_client)
            self.quality_checker = CodeQualityChecker(self.llm_client)
        else:
            self.security_scanner = None
            self.quality_checker = None

        # Review statistics
        self.review_statistics = {
            "files_reviewed": 0,
            "vulnerabilities_found": 0,
            "quality_issues": 0,
            "suggestions": 0
        }

    def review_file(
            self,
            file_path: str,
            language: Optional[str] = None
    ) -> Dict:
        """
        Review a single file

        Args:
            file_path: Path to file
            language: Programming language (auto-detected if None)

        Returns:
            Review results
        """
        print(f"    [CodeReviewAgent] Reviewing {file_path}")

        # Read file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return {
                "file_path": file_path,
                "error": f"Failed to read file: {e}"
            }

        # Auto-detect language
        if language is None:
            language = self._detect_language(file_path)

        # Security scan
        security_results = {}
        if self.security_scanner:
            security_results = self.security_scanner.scan_code(
                file_path=file_path,
                content=content,
                language=language
            )

        # Quality check
        quality_results = {}
        if self.quality_checker:
            quality_results = self.quality_checker.check_quality(
                file_path=file_path,
                content=content,
                language=language
            )

        # Update statistics
        self.review_statistics["files_reviewed"] += 1
        if security_results.get("total", 0) > 0:
            self.review_statistics["vulnerabilities_found"] += security_results["total"]
        if quality_results.get("total", 0) > 0:
            self.review_statistics["quality_issues"] += quality_results["total"]

        return {
            "file_path": file_path,
            "language": language,
            "security": security_results,
            "quality": quality_results,
            "overall_status": self._get_overall_status(security_results, quality_results),
            "reviewed_at": datetime.now().isoformat()
        }

    def review_changes(
            self,
            base_branch: str = "main",
            head_branch: str = "HEAD"
    ) -> Dict:
        """
        Review git changes (diff)

        Args:
            base_branch: Base branch to compare against
            head_branch: Head branch (commit/branch)

        Returns:
            Review results for all changed files
        """
        print(f"    [CodeReviewAgent] Reviewing changes from {base_branch}...{head_branch}")

        # Get list of changed files
        changed_files = self._get_changed_files(base_branch, head_branch)

        results = {
            "base_branch": base_branch,
            "head_branch": head_branch,
            "total_files": len(changed_files),
            "files": [],
            "summary": {
                "critical_issues": 0,
                "high_issues": 0,
                "medium_issues": 0,
                "low_issues": 0
            }
        }

        for file_path in changed_files:
            review = self.review_file(file_path)
            results["files"].append(review)

            # Update summary
            if review.get("security", {}).get("by_severity"):
                for severity, count in review["security"]["by_severity"].items():
                    if f"{severity}_issues" in results["summary"]:
                        results["summary"][f"{severity}_issues"] += count

        return results

    def review_commit(
            self,
            commit_hash: str
    ) -> Dict:
        """
        Review a specific commit

        Args:
            commit_hash: Git commit hash

        Returns:
            Review results
        """
        print(f"    [CodeReviewAgent] Reviewing commit {commit_hash}")

        # Get changed files in commit
        changed_files = self._get_commit_files(commit_hash)

        results = {
            "commit_hash": commit_hash,
            "total_files": len(changed_files),
            "files": [],
            "summary": {
                "critical_issues": 0,
                "high_issues": 0,
                "medium_issues": 0,
                "low_issues": 0
            }
        }

        for file_path in changed_files:
            review = self.review_file(file_path)
            results["files"].append(review)

        return results

    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension"""
        ext = Path(file_path).suffix.lower()

        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php'
        }

        return language_map.get(ext, 'text')

    def _get_changed_files(self, base_branch: str, head_branch: str) -> List[str]:
        """Get list of changed files between branches"""
        try:
            result = subprocess.run(
                ['git', '-C', str(self.project_path), 'diff', '--name-only', f'{base_branch}...{head_branch}'],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                files = result.stdout.strip().split('\n')
                return [f for f in files if f and not f.startswith('.')]

            return []
        except Exception as e:
            print(f"    [CodeReviewAgent] Warning: Failed to get changed files: {e}")
            return []

    def _get_commit_files(self, commit_hash: str) -> List[str]:
        """Get list of changed files in commit"""
        try:
            result = subprocess.run(
                ['git', '-C', str(self.project_path), 'diff-tree', '--no-commit-id', '--name-only', '-r', commit_hash],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                files = result.stdout.strip().split('\n')
                return [f for f in files if f and not f.startswith('.')]

            return []
        except Exception as e:
            print(f"    [CodeReviewAgent] Warning: Failed to get commit files: {e}")
            return []

    def _get_overall_status(self, security: Dict, quality: Dict) -> str:
        """Get overall review status"""
        critical_security = security.get("by_severity", {}).get("critical", 0)
        high_security = security.get("by_severity", {}).get("high", 0)

        if critical_security > 0:
            return "reject"  # Critical security issues
        elif high_security > 0:
            return "request_changes"  # High severity issues
        else:
            return "approve"  # Safe to proceed

    def generate_review_report(self, review_results: Dict) -> str:
        """
        Generate human-readable review report

        Args:
            review_results: Review results

        Returns:
            Formatted report text
        """
        report = []
        report.append("=" * 80)
        report.append("CODE REVIEW REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # Summary
        if "files" in review_results:
            total_files = len(review_results["files"])
            report.append(f"Files Reviewed: {total_files}")
            report.append("")

            # Security summary
            total_vulns = sum(
                f.get("security", {}).get("total", 0)
                for f in review_results["files"]
            )
            report.append(f"Security Vulnerabilities: {total_vulns}")

            # Quality summary
            total_issues = sum(
                f.get("quality", {}).get("total", 0)
                for f in review_results["files"]
            )
            report.append(f"Quality Issues: {total_issues}")
            report.append("")

        # File-by-file details
        for file_review in review_results.get("files", []):
            report.append("-" * 80)
            report.append(f"File: {file_review['file_path']}")
            report.append(f"Language: {file_review['language']}")
            report.append(f"Status: {file_review.get('overall_status', 'unknown').upper()}")
            report.append("")

            # Security details
            if file_review.get("security", {}).get("vulnerabilities"):
                report.append("  Security Issues:")
                for vuln in file_review["security"]["vulnerabilities"][:5]:  # Limit output
                    report.append(f"    - [{vuln['severity'].upper()}] Line {vuln['line']}: {vuln.get('message', vuln['type'])}")
                    if vuln.get("fix_suggestions"):
                        for suggestion in vuln["fix_suggestions"][:2]:
                            report.append(f"      → {suggestion}")
                report.append("")

            # Quality details
            if file_review.get("quality", {}).get("issues"):
                report.append("  Quality Issues:")
                for issue in file_review["quality"]["issues"][:5]:
                    report.append(f"    - [{issue['severity'].upper()}] Line {issue['line']}: {issue['message']}")
                report.append("")

        # Overall recommendation
        report.append("=" * 80)
        report.append("OVERALL RECOMMENDATION:")
        report.append("=" * 80)

        # Count issues by severity
        critical = sum(
            f.get("security", {}).get("by_severity", {}).get("critical", 0)
            for f in review_results.get("files", [])
        )
        high = sum(
            f.get("security", {}).get("by_severity", {}).get("high", 0)
            for f in review_results.get("files", [])
        )

        if critical > 0:
            report.append("❌ REJECT - Critical security vulnerabilities found")
        elif high > 0:
            report.append("⚠️  REQUEST CHANGES - High severity issues found")
        else:
            report.append("✅ APPROVE - No critical issues found")

        return "\n".join(report)

    def save_review_report(
            self,
            review_results: Dict,
            output_path: Optional[str] = None
    ):
        """
        Save review report to file

        Args:
            review_results: Review results
            output_path: Output file path (default: project_path/code_review_report.txt)
        """
        if output_path is None:
            output_path = self.project_path / "code_review_report.txt"

        report_text = self.generate_review_report(review_results)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_text)

        # Also save JSON
        json_path = str(output_path).replace('.txt', '.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(review_results, f, indent=2, ensure_ascii=False)

        print(f"    [CodeReviewAgent] Reports saved:")
        print(f"      Text: {output_path}")
        print(f"      JSON: {json_path}")
