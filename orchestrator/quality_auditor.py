"""
Quality Auditor - LLM-as-a-Judge 质量审计器

职责：
1. 使用 LLM 审计代码质量
2. 评估功能实现的真实性（不是表面工作）
3. 判断是否可以通过质量门禁
4. 提供改进建议

基于 Gemini Pro 3 的建议：
- 升级验证机制：从"可用性"到"质量感官"
- LLM-as-a-Judge 验证器
- 双重验证逻辑
"""

import os
import json
import httpx
from pathlib import Path
from typing import Dict, List, Optional


class QualityAuditor:
    """质量审计器 - 使用 LLM 判断代码质量"""

    def __init__(self):
        self.api_key = os.getenv("ZHIPUAI_API_KEY", "")
        self.api_url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

    async def audit_feature_implementation(
        self,
        feature: Dict,
        code_files: List[str],
        project_path: str
    ) -> Dict:
        """
        审计功能实现质量

        Args:
            feature: 功能定义
            code_files: 代码文件路径列表
            project_path: 项目路径

        Returns:
            {
                "passed": bool,
                "score": int (1-10),
                "reasoning": str,
                "issues": List[str],
                "improvements": List[str]
            }
        """
        print(f"  🔍 [Quality Auditor] Auditing feature {feature['id']}...")

        # 读取代码内容
        code_contents = {}
        for file_path in code_files:
            full_path = Path(project_path) / file_path
            if full_path.exists():
                code_contents[file_path] = full_path.read_text()

        if not code_contents:
            return {
                "passed": False,
                "score": 1,
                "reasoning": "No code files found to audit",
                "issues": ["No implementation detected"],
                "improvements": ["Implement actual code"]
            }

        # 构建 audit prompt
        audit_prompt = self._build_audit_prompt(feature, code_contents)

        # 调用 LLM 进行审计
        try:
            result = await self._call_llm_for_audit(audit_prompt)
            return self._parse_audit_result(result)
        except Exception as e:
            print(f"  ⚠️  LLM audit failed: {e}, using rule-based audit")
            return self._rule_based_audit(feature, code_contents)

    def _build_audit_prompt(self, feature: Dict, code_contents: Dict[str, str]) -> str:
        """构建审计提示词"""

        # 读取逻辑需求（如果有）
        logical_reqs = feature.get("logical_requirements", {})

        prompt = f"""你是资深的代码质量审计专家。请审计以下功能的实现质量。

## 功能信息
- **ID**: {feature['id']}
- **描述**: {feature['description']}
- **类别**: {feature.get('category', 'unknown')}
- **优先级**: {feature.get('priority', 'unknown')}

## 逻辑需求
"""

        if logical_reqs:
            prompt += f"""
- **数据流**: {logical_reqs.get('data_flow', 'Not specified')}
- **禁止模式**: {', '.join(logical_reqs.get('forbidden_patterns', ['None']))}
- **错误处理**: {logical_reqs.get('error_handling', 'Not specified')}
- **复杂度**: {logical_reqs.get('complexity_level', 'unknown')}
"""
        else:
            prompt += "\n(未提供详细逻辑需求)"

        prompt += f"""

## 实现代码
```markdown
{self._format_code_contents(code_contents)}
```

## 审计维度

请从以下维度审计（每项 1-10 分）：

1. **逻辑真实性** (1-10)
   - 是否实现了真实的业务逻辑（不是表面工作）？
   - 是否有深度思考的设计（不是简单拼接）？
   - 是否考虑了边界情况？

2. **实现复杂度** (1-10)
   - 代码复杂度是否与功能匹配？
   - 是否避免了过度简化（如纯字符串拼接）？
   - 是否包含了必要的错误处理？

3. **集成完整性** (1-10)
   - 是否正确集成了所有必需的模块？
   - API 调用、状态管理是否正确实现？
   - 是否有加载状态、错误提示？

4. **代码质量** (1-10)
   - 代码是否清晰、易维护？
   - 是否有适当的命名和结构？
   - 是否符合最佳实践？

5. **用户价值** (1-10)
   - 实现是否真正解决了用户问题？
   - 用户体验是否良好？

## 输出要求

请以 JSON 格式输出审计结果：
```json
{{
  "score": <总体评分 1-10>,
  "passed": <是否通过质量门禁 (score >= 7)>,
  "reasoning": "<详细的评分理由，指出优点和问题>",
  "dimension_scores": {{
    "logic_authenticity": <1-10>,
    "implementation_complexity": <1-10>,
    "integration_integrity": <1-10>,
    "code_quality": <1-10>,
    "user_value": <1-10>
  }},
  "issues": ["<发现的问题1>", "<发现的问题2>", ...],
  "improvements": ["<改进建议1>", "<改进建议2>", ...]
}}
```

**重要**：
- 严厉但公正：如果只是表面工作（如简单拼接），必须给低分（1-3分）
- 如果逻辑需求明确要求"禁止简单拼接"但代码仍使用拼接，直接不通过（score < 7）
- 如果看到 TODO、PLACEHOLDER 等占位符，直接不通过
"""
        return prompt

    def _format_code_contents(self, code_contents: Dict[str, str]) -> str:
        """格式化代码内容用于 prompt"""
        formatted = []
        for file_path, content in code_contents.items():
            formatted.append(f"### {file_path}\n")
            # 限制每个文件显示的字符数
            preview = content if len(content) < 2000 else content[:2000] + "\n... (truncated)"
            formatted.append(f"```\n{preview}\n```\n")
        return "\n".join(formatted)

    async def _call_llm_for_audit(self, prompt: str) -> str:
        """调用 LLM 进行审计"""
        if not self.api_key:
            raise Exception("No API key available")

        messages = [
            {
                "role": "system",
                "content": "你是一位资深的代码质量审计专家，以严格、公正的态度评估代码质量。"
            },
            {"role": "user", "content": prompt}
        ]

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "glm-5",
                    "messages": messages,
                    "temperature": 0.3,  # 低温度以保持一致性
                    "max_tokens": 3000
                }
            )

            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                raise Exception(f"API error: {response.status_code}")

    def _parse_audit_result(self, llm_output: str) -> Dict:
        """解析 LLM 审计结果"""
        try:
            # 尝试直接解析 JSON
            result = json.loads(llm_output)
            return result
        except json.JSONDecodeError:
            # 尝试提取 JSON 代码块
            import re
            json_match = re.search(r'```json\s*([\s\S]*?)\s*```', llm_output)
            if json_match:
                result = json.loads(json_match.group(1))
                return result
            else:
                # 如果无法解析，返回保守估计
                return {
                    "passed": False,
                    "score": 5,
                    "reasoning": "Failed to parse LLM output",
                    "issues": ["Unable to parse audit result"],
                    "improvements": ["Manual review required"]
                }

    def _rule_based_audit(self, feature: Dict, code_contents: Dict[str, str]) -> Dict:
        """
        基于规则的审计（fallback）

        当 LLM 不可用时使用
        """
        issues = []
        score = 10  # 初始满分，发现一个问题扣分
        passed = True

        # 检查 1: 是否有代码
        if not code_contents:
            return {
                "passed": False,
                "score": 1,
                "reasoning": "No code files found",
                "issues": ["No implementation"],
                "improvements": ["Implement the feature"]
            }

        all_code = "\n".join(code_contents.values())

        # 检查 2: 占位符检测
        placeholder_patterns = ["TODO", "PLACEHOLDER", "NOT IMPLEMENTED", "Required"]
        for pattern in placeholder_patterns:
            if pattern in all_code:
                score = min(score, 3)
                issues.append(f"Contains placeholder: {pattern}")
                passed = False
                break

        # 检查 3: 简单拼接检测
        if "optimize" in feature["description"].lower():
            # 检查是否只有字符串拼接
            if "result +=" in all_code or "result &" in all_code:
                if "llm." not in all_code and "api." not in all_code and "fetch" not in all_code:
                    score = min(score, 2)
                    issues.append("Simple string concatenation detected (no LLM API call)")
                    passed = False

        # 检查 4: 文件大小
        total_size = sum(len(content) for content in code_contents.values())
        if total_size < 200:
            score = min(score, 4)
            issues.append(f"Code files too small ({total_size} bytes)")
            passed = False

        # 检查 5: 错误处理
        if "try {" not in all_code and "try:" not in all_code:
            score -= 2
            issues.append("No error handling found")

        # 检查 6: 集成点验证
        logical_reqs = feature.get("logical_requirements", {})
        if logical_reqs.get("must_call_llm") == "必须调用 LLM API":
            if "llm." not in all_code and "api." not in all_code and "fetch" not in all_code:
                score = min(score, 2)
                issues.append("Requires LLM API call but none found")
                passed = False

        # 确保分数在 1-10 范围内
        score = max(1, min(10, score))

        return {
            "passed": passed and score >= 7,
            "score": score,
            "reasoning": f"Rule-based audit: {len(issues)} issues found, score={score}/10",
            "issues": issues,
            "improvements": self._generate_improvements(issues, feature)
        }

    def _generate_improvements(self, issues: List[str], feature: Dict) -> List[str]:
        """根据问题生成改进建议"""
        improvements = []

        for issue in issues:
            if "placeholder" in issue.lower():
                improvements.append("Replace placeholder code with actual implementation")
            elif "string concatenation" in issue.lower():
                improvements.append("Implement intelligent optimization logic instead of simple string joining")
            elif "error handling" in issue.lower():
                improvements.append("Add try-catch blocks for error handling")
            elif "too small" in issue.lower():
                improvements.append("Add more implementation details and logic")
            elif "no api call" in issue.lower():
                improvements.append("Integrate with LLM API for intelligent processing")

        if not improvements:
            improvements.append("Review and enhance implementation based on requirements")

        return improvements


# 全局函数
async def audit_feature_quality(
    feature: Dict,
    project_path: str
) -> Dict:
    """
    便捷函数：审计功能质量

    Returns:
        审计结果字典
    """
    auditor = QualityAuditor()

    # 查找相关代码文件
    project = Path(project_path)
    code_files = []

    # 根据功能类别查找相关文件
    category = feature.get("category", "")
    if category in ["ui", "frontend"]:
        code_files.extend([str(p.relative_to(project)) for p in project.rglob("*.tsx")])
        code_files.extend([str(p.relative_to(project)) for p in project.rglob("*.ts")])
    elif category in ["api", "backend"]:
        code_files.extend([str(p.relative_to(project)) for p in project.rglob("*.py")])

    return await auditor.audit_feature_implementation(feature, code_files, str(project_path))
