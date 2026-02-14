#!/usr/bin/env python3
"""
Code Review Agent Test

测试专业化 Code Review Agent 的功能
"""

import sys
import os
from pathlib import Path
import tempfile
import shutil

# Add orchestrator directory to path
orchestrator_dir = Path(__file__).parent / "orchestrator"
sys.path.insert(0, str(orchestrator_dir))

from code_review_agent import SecurityScanner, CodeQualityChecker, CodeReviewAgent


# Test code samples with various issues
INSECURE_CODE_SAMPLES = {
    "python": '''
import sqlite3
import pickle
from flask import request

def login(username, password):
    # SQL injection vulnerability
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    cursor.execute(query)

    # Hardcoded secret
    api_key = "sk-1234567890abcdefghijklmnopqrstuv"

    # Command injection
    user_input = request.args.get('cmd')
    result = os.system(user_input)

    # Insecure deserialization
    data = pickle.loads(user_data)

    return query

def get_user(user_id):
    # Path traversal
    filename = f"../data/{user_id}.json"
    with open(filename, 'r') as f:
        return f.read()
''',

    "javascript": '''
import React from 'react';
import request from 'request';

function Login(props) {
  const [username, setUsername] = React.useState('');
  const [password, setPassword] = React.useState('');

  const handleSubmit = () => {
    // XSS vulnerability
    const html = `<div>Welcome, {username}</div>`;
    document.getElementById('welcome').innerHTML = html;

    // Hardcoded API key
    const apiKey = "sk-1234567890abcdefghijklmnopqrstuv";

    fetch('/api/login', {
      headers: {
        'Authorization': `Bearer ${apiKey}`
      },
      body: JSON.stringify({ username, password })
    });
  };

  return (
    <form onSubmit={handleSubmit}>
      <input value={username} onChange={(e) => setUsername(e.target.value)} />
      <button type="submit">Login</button>
    </form>
  );
}
'''
}

QUALITY_CODE_SAMPLES = {
    "python": '''
# This is a very long function that does too many things
# It should be refactored into smaller functions
def process_user_data(user_id, user_data, action_type, config_options, metadata, cache_manager):
    """
    Process user data with multiple concerns
    """
    # TODO: Fix this later
    # FIXME: This is buggy
    result = None

    # Deep nesting example
    if user_id:
        if user_data:
            if action_type == "create":
                if config_options:
                    if metadata:
                        if cache_manager:
                            result = cache_manager.get(user_id)
                            if not result:
                                if user_data.get('name'):
                                    if user_data.get('email'):
                                        # Magic number
                                        max_attempts = 100

    # Console log in production
    console.log(f"Processing user {user_id}")

    # More magic numbers
    timeout = 30000
    retry_count = 5

    return result

def another_function():
    # TODO: Implement this
    pass
''',

    "javascript": '''
// Long function with quality issues
function processUserData(userId, userData, actionType, configOptions, metadata, cacheManager) {
    // TODO: Implement error handling
    // FIXME: This is incomplete
    let result = null;

    // Deep nesting
    if (userId) {
        if (userData) {
            if (actionType === 'create') {
                if (configOptions) {
                    if (metadata) {
                        if (cacheManager) {
                            result = cacheManager.get(userId);
                            if (!result) {
                                if (userData.name) {
                                    if (userData.email) {
                                        // Magic number
                                        const maxAttempts = 100;
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    // Console log
    console.log(`Processing user ${userId}`);

    // More magic numbers
    const timeout = 30000;
    const retryCount = 5;

    return result;
}
'''
}


def test_security_scanner():
    """测试安全扫描器"""
    print("=" * 80)
    print("Testing SecurityScanner")
    print("=" * 80)

    try:
        from llm_clients import get_llm_client
        llm_client = get_llm_client("glm-5")

        scanner = SecurityScanner(llm_client)

        # Test Python code
        print("\nTest 1: Python Security Scan")
        print("-" * 80)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(INSECURE_CODE_SAMPLES['python'])
            temp_path = f.name

        try:
            result = scanner.scan_code(
                file_path=temp_path,
                content=INSECURE_CODE_SAMPLES['python'],
                language='python'
            )

            print(f"\nScan Results:")
            print(f"  Total Vulnerabilities: {result['total']}")
            print(f"  By Severity:")
            for severity, count in result['by_severity'].items():
                if count > 0:
                    print(f"    {severity.upper()}: {count}")

            print(f"\nFirst 5 Vulnerabilities:")
            for i, vuln in enumerate(result['vulnerabilities'][:5], 1):
                print(f"\n  {i}. [{vuln['severity'].upper()}] {vuln['type']}")
                print(f"     Line {vuln['line']}: {vuln['code_snippet'][:60]}...")

                if 'llm_analysis' in vuln:
                    print(f"     LLM Analysis Available")

        finally:
            os.unlink(temp_path)

        # Test JavaScript code
        print("\n\nTest 2: JavaScript Security Scan")
        print("-" * 80)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(INSECURE_CODE_SAMPLES['javascript'])
            temp_path = f.name

        try:
            result = scanner.scan_code(
                file_path=temp_path,
                content=INSECURE_CODE_SAMPLES['javascript'],
                language='javascript'
            )

            print(f"\nScan Results:")
            print(f"  Total Vulnerabilities: {result['total']}")
            print(f"  By Severity:")
            for severity, count in result['by_severity'].items():
                if count > 0:
                    print(f"    {severity.upper()}: {count}")

        finally:
            os.unlink(temp_path)

        return True

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_code_quality_checker():
    """测试代码质量检查器"""
    print("\n" + "=" * 80)
    print("Testing CodeQualityChecker")
    print("=" * 80)

    try:
        from llm_clients import get_llm_client
        llm_client = get_llm_client("glm-5")

        checker = CodeQualityChecker(llm_client)

        # Test Python code
        print("\nTest 1: Python Quality Check")
        print("-" * 80)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(QUALITY_CODE_SAMPLES['python'])
            temp_path = f.name

        try:
            result = checker.check_quality(
                file_path=temp_path,
                content=QUALITY_CODE_SAMPLES['python'],
                language='python'
            )

            print(f"\nQuality Check Results:")
            print(f"  Total Issues: {result['total']}")
            print(f"  Lines: {result['lines']}")
            print(f"  By Severity:")
            for severity, count in result['by_severity'].items():
                if count > 0:
                    print(f"    {severity.upper()}: {count}")

            print(f"\nFirst 5 Issues:")
            for i, issue in enumerate(result['issues'][:5], 1):
                print(f"\n  {i}. [{issue['severity'].upper()}] {issue['type']}")
                print(f"     Line {issue['line']}: {issue['message']}")

                if 'llm_analysis' in issue:
                    print(f"     LLM Refactoring Suggestions Available")

        finally:
            os.unlink(temp_path)

        # Test JavaScript code
        print("\n\nTest 2: JavaScript Quality Check")
        print("-" * 80)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(QUALITY_CODE_SAMPLES['javascript'])
            temp_path = f.name

        try:
            result = checker.check_quality(
                file_path=temp_path,
                content=QUALITY_CODE_SAMPLES['javascript'],
                language='javascript'
            )

            print(f"\nQuality Check Results:")
            print(f"  Total Issues: {result['total']}")
            print(f"  Lines: {result['lines']}")
            print(f"  By Severity:")
            for severity, count in result['by_severity'].items():
                if count > 0:
                    print(f"    {severity.upper()}: {count}")

        finally:
            os.unlink(temp_path)

        return True

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_code_review_agent():
    """测试代码审查代理"""
    print("\n" + "=" * 80)
    print("Testing CodeReviewAgent")
    print("=" * 80)

    project_path = Path(__file__).parent / "workspace" / "demo-todo-app"

    if not project_path.exists():
        print(f"Project path not found: {project_path}")
        print("Using current directory for testing")
        project_path = Path(__file__).parent

    print(f"\nProject path: {project_path}")

    try:
        from llm_clients import get_llm_client

        agent = CodeReviewAgent(
            project_path=str(project_path),
            llm_provider="glm-5"
        )

        # Test 1: Review a single file
        print("\nTest 1: Review Single File")
        print("-" * 80)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, dir=str(project_path)) as f:
            f.write(INSECURE_CODE_SAMPLES['python'])
            temp_path = f.name

        try:
            result = agent.review_file(temp_path)

            print(f"\nReview Result:")
            print(f"  File: {result['file_path']}")
            print(f"  Language: {result['language']}")
            print(f"  Overall Status: {result['overall_status'].upper()}")

            if 'security' in result:
                print(f"  Security Vulnerabilities: {result['security'].get('total', 0)}")

            if 'quality' in result:
                print(f"  Quality Issues: {result['quality'].get('total', 0)}")

        finally:
            os.unlink(temp_path)

        # Test 2: Review git changes (if available)
        print("\n\nTest 2: Review Git Changes")
        print("-" * 80)

        try:
            result = agent.review_changes(base_branch='main', head_branch='HEAD')

            print(f"\nReview Result:")
            print(f"  Total Files: {result['total_files']}")
            print(f"  Summary:")
            print(f"    Critical Issues: {result['summary']['critical_issues']}")
            print(f"    High Issues: {result['summary']['high_issues']}")
            print(f"    Medium Issues: {result['summary']['medium_issues']}")
            print(f"    Low Issues: {result['summary']['low_issues']}")

        except Exception as e:
            print(f"  Warning: Git review skipped: {e}")

        return True

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_review_report_generation():
    """测试审查报告生成"""
    print("\n" + "=" * 80)
    print("Testing Review Report Generation")
    print("=" * 80)

    try:
        from llm_clients import get_llm_client

        # Create mock review results
        review_results = {
            "base_branch": "main",
            "head_branch": "feature/add-todo",
            "total_files": 2,
            "files": [
                {
                    "file_path": "src/app.tsx",
                    "language": "typescript",
                    "overall_status": "request_changes",
                    "security": {
                        "total": 1,
                        "vulnerabilities": [
                            {
                                "type": "xss",
                                "severity": "critical",
                                "line": 42,
                                "code_snippet": "innerHTML = userInput",
                                "fix_suggestions": [
                                    "Use React's built-in escaping",
                                    "Sanitize input before rendering"
                                ]
                            }
                        ]
                    },
                    "quality": {
                        "total": 3,
                        "issues": [
                            {
                                "type": "magic_numbers",
                                "severity": "low",
                                "line": 15,
                                "message": "Magic number detected"
                            }
                        ]
                    }
                },
                {
                    "file_path": "src/utils/api.ts",
                    "language": "typescript",
                    "overall_status": "approve",
                    "security": {
                        "total": 0,
                        "vulnerabilities": []
                    },
                    "quality": {
                        "total": 1,
                        "issues": [
                            {
                                "type": "console_log",
                                "severity": "low",
                                "line": 28,
                                "message": "Console.log statement found"
                            }
                        ]
                    }
                }
            ],
            "summary": {
                "critical_issues": 1,
                "high_issues": 0,
                "medium_issues": 2,
                "low_issues": 1
            }
        }

        agent = CodeReviewAgent(project_path="/tmp/test")
        report = agent.generate_review_report(review_results)

        print("\nGenerated Report:")
        print(report)

        print("\n\nTest 2: Save Report to File")
        print("-" * 80)

        with tempfile.TemporaryDirectory() as tmpdir:
            agent.project_path = Path(tmpdir)
            agent.save_review_report(review_results)

            report_path = Path(tmpdir) / "code_review_report.txt"
            json_path = Path(tmpdir) / "code_review_report.json"

            if report_path.exists() and json_path.exists():
                print(f"  Text report: {report_path}")
                print(f"  JSON report: {json_path}")
                print(f"  ✅ Reports saved successfully")

                # Read and display part of text report
                with open(report_path, 'r') as f:
                    content = f.read()
                    print(f"\n  First 500 chars of text report:")
                    print("  " + "=" * 76)
                    print("  " + content[:500])
                    print("  " + "=" * 76)
            else:
                print(f"  ❌ Report files not created")
                return False

        return True

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🔍 Code Review Agent Integration Test\n")

    results = {
        "SecurityScanner": False,
        "CodeQualityChecker": False,
        "CodeReviewAgent": False,
        "ReportGeneration": False
    }

    # Test 1: SecurityScanner
    try:
        results["SecurityScanner"] = test_security_scanner()
    except Exception as e:
        print(f"SecurityScanner test failed: {e}")

    # Test 2: CodeQualityChecker
    try:
        results["CodeQualityChecker"] = test_code_quality_checker()
    except Exception as e:
        print(f"CodeQualityChecker test failed: {e}")

    # Test 3: CodeReviewAgent
    try:
        results["CodeReviewAgent"] = test_code_review_agent()
    except Exception as e:
        print(f"CodeReviewAgent test failed: {e}")

    # Test 4: Report Generation
    try:
        results["ReportGeneration"] = test_review_report_generation()
    except Exception as e:
        print(f"ReportGeneration test failed: {e}")

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    for component, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {component}: {status}")

    all_passed = all(results.values())

    print("\n" + "=" * 80)
    if all_passed:
        print("✅ ALL TESTS PASSED")
        print("=" * 80)
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED")
        print("=" * 80)
        sys.exit(1)
