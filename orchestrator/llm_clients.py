"""
LLM Clients - 大语言模型客户端集成

支持多个 LLM 提供商：
- GLM-5 (智谱AI)
- Claude (Anthropic)
- OpenAI (可选）
"""

import os
import json
import httpx
from typing import Dict, List, Optional, Any
from pathlib import Path

# 自动加载 .env 文件
try:
    from dotenv import load_dotenv
    # 尝试从当前目录和工作目录加载 .env
    load_dotenv()
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
except ImportError:
    pass  # 如果没有安装 python-dotenv，忽略


class GLM5Client:
    """
    GLM API 客户端（支持 GLM Coding Plan Pro/Max 套餐）

    文档: https://docs.bigmodel.cn/cn/api/introduction
    套餐: https://www.bigmodel.cn/glm-coding

    支持的套餐和模型（更新于 2026-02-14）：
    - Pro 套餐：glm-5（推荐）、glm-4.7、glm-4.6、glm-4.5、glm-4.5-air
    - Max 套餐：glm-5（推荐）、glm-4.7 等
    - Lite 套餐：glm-4.7 等（glm-5 支持即将上线）

    端点说明：
    - 通用 API: https://open.bigmodel.cn/api/paas/v4 (对话、分析等)
    - Coding API: https://open.bigmodel.cn/api/coding/paas/v4 (仅代码生成)
    """

    # 通用 API 端点（用于对话、需求分析等）
    API_GENERAL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

    # Coding API 端点（仅用于代码生成）
    API_CODING = "https://open.bigmodel.cn/api/coding/paas/v4/chat/completions"

    # 根据套餐选择合适的模型（更新于 2026-02-14）
    # Pro/Max 套餐推荐使用 glm-5（最新旗舰模型，编程体感逼近 Claude 4.5/4.6）
    # Pro/Max 套餐也可以使用 glm-4.7、glm-4.6、glm-4.5
    MODEL_NAME = "glm-5"  # 默认使用 GLM-5（与官方示例一致）

    # 可选模型列表（更新于 2026-02-14）
    AVAILABLE_MODELS = {
        "glm-5": "GLM-5（推荐）- Pro/Max 套餐，最新旗舰模型",
        "glm-4.7": "GLM-4.7 - Pro/Max 套餐，代码生成优化",
        "glm-4.6": "GLM-4.6 - Pro/Max 套餐",
        "glm-4.5": "GLM-4.5 - Pro/Max 套餐",
        "glm-4.5-air": "GLM-4.5-Air - 轻量级，所有套餐"
    }

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化 GLM-5 客户端

        Args:
            api_key: 智谱AI API Key (可以从环境变量读取）
        """
        self.api_key = api_key or os.getenv("ZHIPUAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API Key not found. Please set ZHIPUAI_API_KEY "
                "environment variable or pass api_key parameter."
            )

        # 从环境变量读取超时配置
        timeout_general = float(os.getenv("GLM5_TIMEOUT", "90"))
        timeout_coding = float(os.getenv("GLM5_CODING_TIMEOUT", "120"))

        # 通用 API 客户端（用于对话、需求分析等）
        self.client_general = httpx.Client(
            base_url=self.API_GENERAL,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=timeout_general
        )

        # Coding API 客户端（仅用于代码生成）
        self.client_coding = httpx.Client(
            base_url=self.API_CODING,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=timeout_coding
        )

    def chat_completion(
            self,
            messages: List[Dict],
            tools: Optional[List[Dict]] = None,
            temperature: float = 0.7,
            max_tokens: int = 4096,
            stream: bool = False,
            show_progress: bool = False
    ) -> Dict:
        """
        调用 GLM 通用对话补全 API

        用于：需求分析、对话交互等通用场景

        Args:
            messages: 对话消息列表
                [{"role": "user", "content": "..."}]
            tools: 工具列表（Function Calling）
            temperature: 温度参数 (0-1)
            max_tokens: 最大 token 数
            stream: 是否流式输出
            show_progress: 是否显示进度信息

        Returns:
            API 响应字典
        """
        payload = {
            "model": self.MODEL_NAME,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }

        if tools:
            payload["tools"] = tools

        try:
            if show_progress:
                import sys
                import time
                print("[GLM-5] Sending request to API...", file=sys.stderr, flush=True)
                start_time = time.time()

            # 使用通用 API 端点
            response = self.client_general.post("", json=payload)
            response.raise_for_status()

            if show_progress:
                elapsed = time.time() - start_time
                print(f"[GLM-5] Response received in {elapsed:.1f}s", file=sys.stderr, flush=True)

            if stream:
                # 流式响应
                return {
                    "stream": response.iter_bytes()
                }

            return response.json()

        except httpx.HTTPStatusError as e:
            return {
                "error": True,
                "status_code": e.response.status_code,
                "message": str(e)
            }
        except Exception as e:
            return {
                "error": True,
                "message": str(e)
            }

    def coding_completion(
            self,
            messages: List[Dict],
            temperature: float = 0.3,
            max_tokens: int = 8192,
            stream: bool = False
    ) -> Dict:
        """
        调用 GLM Coding API（专用端点）

        用于：代码生成、代码优化等 Coding 场景

        注意：此端点仅限 Coding 场景使用，不适用于通用对话

        Args:
            messages: 对话消息列表
                [{"role": "user", "content": "..."}]
            temperature: 温度参数 (0-1)
            max_tokens: 最大 token 数
            stream: 是否流式输出

        Returns:
            API 响应字典
        """
        payload = {
            "model": self.MODEL_NAME,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }

        try:
            # 使用 Coding API 端点
            response = self.client_coding.post("", json=payload)
            response.raise_for_status()

            if stream:
                # 流式响应
                return {
                    "stream": response.iter_bytes()
                }

            return response.json()

        except httpx.HTTPStatusError as e:
            return {
                "error": True,
                "status_code": e.response.status_code,
                "message": str(e)
            }
        except Exception as e:
            return {
                "error": True,
                "message": str(e)
            }

    def generate_code(
            self,
            prompt: str,
            context: Optional[str] = None,
            file_structure: Optional[Dict] = None,
            temperature: float = 0.3,
            max_tokens: int = 8192
    ) -> str:
        """
        生成代码（专用方法）

        Args:
            prompt: 代码生成提示
            context: 额外的上下文信息
            file_structure: 项目文件结构

        Returns:
            生成的代码字符串
        """
        system_prompt = """你是一个专业的软件开发 AI 助手，擅长以下任务：

1. 分析代码需求并生成高质量代码
2. 理解现有代码结构并进行增量修改
3. 遵循最佳实践和设计模式
4. 确保代码的可维护性和可扩展性

重要原则：
- 优先使用不可变（immutable）数据结构
- 函数保持小而专注（<50 行）
- 文件保持聚焦（<800 行）
- 完整的错误处理
- 系统边界验证输入
- 清晰的命名和注释
"""

        messages = [
            {"role": "system", "content": system_prompt}
        ]

        # 构建完整提示
        full_prompt = prompt

        if context:
            full_prompt = f"""
## 项目上下文

{context}

## 任务

{prompt}
"""

        if file_structure:
            full_prompt += f"""

## 当前项目结构

```json
{json.dumps(file_structure, indent=2, ensure_ascii=False)}
```
"""

        messages.append({"role": "user", "content": full_prompt})

        # 使用 Coding API 端点进行代码生成
        response = self.coding_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        if response.get("error"):
            raise Exception(f"API Error: {response['message']}")

        # 提取生成的内容
        message = response["choices"][0]["message"]
        content = message.get("content", "")

        # 如果 content 为空，检查 reasoning_content（GLM-4.7 推理模型）
        if not content and "reasoning_content" in message:
            content = message["reasoning_content"]

        return content

    def analyze_requirements(
            self,
            user_prompt: str,
            max_features: int = 30,
            show_progress: bool = True
    ) -> List[Dict]:
        """
        分析用户需求，生成功能列表

        Args:
            user_prompt: 用户的原始需求描述
            max_features: 最大功能数量（默认 30）
            show_progress: 是否显示进度信息

        Returns:
            功能列表，每个功能包含：
            {
                "id": "category-action-001",
                "category": "authentication",
                "priority": "critical/high/medium/low",
                "description": "User can ...",
                "e2e_steps": ["step 1", "step 2", ...],
                "verification_step": "验证页面跳转到 /dashboard 且显示用户名",
                "passes": false,
                "dependencies": []
            }
        """
        system_prompt = """你是一个专业的产品经理和技术架构师 AI，擅长深度逻辑推理。

任务：将用户的需求分解为细粒度的、可测试的功能。

## 🎯 核心原则：逻辑深度推理

**严禁**只描述表面行为！你必须推理出：
1. **核心算法逻辑**：不只是"创建输入框"，而是"数据如何流动、处理、验证"
2. **非直观依赖**：需要什么隐藏的条件判断、状态管理、错误处理
3. **禁止简化实现**：明确禁止哪些偷懒的实现方式
4. **真实业务逻辑**：考虑实际使用场景中的复杂情况

## ❌ 错误示例（表面描述）：
{
  "id": "ui-input-001",
  "description": "创建输入框组件",  // ❌ 太表面！
  "e2e_steps": ["创建输入框", "显示输入框"]  // ❌ 没有逻辑！
}

## ✅ 正确示例（深度推理）：
{
  "id": "api-optimize-001",
  "description": "实现提示词优化 API 端点",
  "logical_requirements": {
    "must_call_llm": "必须调用 LLM API（GLM-5 或 Claude）进行智能优化",
    "forbidden_patterns": ["禁止简单字符串拼接", "禁止只返回模板"],
    "data_flow": "前端发送 CO-STAR 数据 → 后端构建提示词 → 调用 LLM API → 返回优化结果",
    "error_handling": "API 超时必须有重试机制（3次），失败时返回智能规则的优化结果",
    "complexity_level": "high",
    "integration_points": ["后端 API 集成", "LLM API 调用", "错误处理", "加载状态"]
  },
  "e2e_steps": [
    "输入测试数据（Context, Objective等字段）",
    "点击优化按钮",
    "等待 API 响应（显示加载状态）",
    "验证返回的是优化后的提示词（不是简单拼接）",
    "验证包含改进建议和质量评分"
  ]
}

## 深度推理检查清单

对每个功能，问自己：
- ✅ 是否说明了**数据如何流动**？
- ✅ 是否说明了**如何验证逻辑正确性**？
- ✅ 是否考虑了**错误情况**（API 失败、网络超时、空输入）？
- ✅ 是否说明了**状态管理**（加载中、成功、失败）？
- ✅ 是否**明确禁止了简化实现**？

每个功能应该：
1. 聚焦于单个用户行为或系统功能（开发时间不超过 15 分钟）
2. 包含清晰的 verification_step（验证步骤）
3. 包含 logical_requirements（逻辑需求）
4. 有明确的优先级
5. 标注依赖关系

功能 ID 格式：category-action-001 (例如：auth-login-001)

分类：
- setup: 项目设置和配置
- ui: 用户界面组件
- data: 数据结构和状态管理
- api: API 端点和业务逻辑
- testing: 测试相关
- style: 样式和布局

优先级：
- critical: 核心功能，没有它应用无法使用
- high: 重要功能
- medium: 常规功能
- low: 增强功能

输出格式：JSON 数组，每个功能包含：
{
  "id": "category-action-001",
  "category": "authentication",
  "priority": "critical",
  "description": "用户可以登录系统",
  "logical_requirements": {
    "data_flow": "数据如何流动和处理",
    "forbidden_patterns": ["禁止的简化实现"],
    "error_handling": "错误处理要求",
    "complexity_level": "low/medium/high",
    "integration_points": ["需要集成的其他模块"]
  },
  "e2e_steps": ["步骤1", "步骤2", ...],
  "verification_step": "验证页面跳转到 /dashboard 且显示用户名",
  "dependencies": [],
  "passes": false
}
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"""请将以下用户需求分解为详细的功能列表：

{user_prompt}

要求：
1. 生成 {max_features} 个左右的功能（不必超过）
2. 每个功能必须包含 e2e_steps（端到端测试步骤）和 verification_step（具体验证步骤）
3. verification_step 必须明确、可执行、可验证（包含具体的预期结果）
4. 如果涉及 UI，请注明具体的视觉验证要求（如颜色、位置、尺寸）
5. 使用 JSON 格式输出
6. 功能 ID 按分类和编号命名
7. 确保依赖关系准确无误"""
            }
        ]

        response = self.chat_completion(
            messages=messages,
            temperature=0.5,
            max_tokens=8192,  # 减少 token 数量，避免超时
            show_progress=show_progress
        )

        if response.get("error"):
            raise Exception(f"API Error: {response['message']}")

        # 提取 JSON 内容
        message = response["choices"][0]["message"]
        content = message.get("content", "")

        # 如果 content 为空，检查 reasoning_content（GLM-4.7 推理模型）
        if not content and "reasoning_content" in message:
            content = message["reasoning_content"]

        # 尝试解析 JSON（可能包裹在 markdown 代码块中）
        try:
            # 直接解析
            features = json.loads(content)
        except json.JSONDecodeError:
            # 尝试提取 markdown 代码块
            import re
            json_match = re.search(r'```json\s*([\s\S]*?)\s*```', content)
            if json_match:
                features = json.loads(json_match.group(1))
            else:
                # 尝试提取普通代码块
                code_match = re.search(r'```\s*([\s\S]*?)\s*```', content)
                if code_match:
                    features = json.loads(code_match.group(1))
                else:
                    raise ValueError("无法从响应中提取有效的 JSON")

        return features


class ClaudeClient:
    """
    Claude API 客户端（备选）

    如果用户有 Anthropic API Key，可以使用 Claude
    """

    API_BASE = "https://api.anthropic.com/v1/messages"

    def __init__(self, api_key: Optional[str] = None):
        """初始化 Claude 客户端"""
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found")

        self.client = httpx.Client(
            base_url=self.API_BASE,
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            },
            timeout=120.0
        )

    def chat_completion(self, messages: List[Dict], **kwargs) -> Dict:
        """调用 Claude API"""
        # 类似 GLM-5 的实现
        payload = {
            "model": "claude-sonnet-4-5-20250929",
            "max_tokens": 4096,
            "messages": messages,
            **kwargs
        }

        response = self.client.post("/v1/messages", json=payload)
        return response.json()


def get_llm_client(provider: str = "glm-5", **kwargs) -> Any:
    """
    工厂函数：根据提供商返回客户端

    Args:
        provider: "glm-5" 或 "claude"
        **kwargs: 传递给客户端构造函数的参数

    Returns:
        LLM 客户端实例
    """
    providers = {
        "glm-5": GLM5Client,
        "claude": ClaudeClient
    }

    client_class = providers.get(provider.lower())
    if not client_class:
        raise ValueError(f"Unknown provider: {provider}. Available: {list(providers.keys())}")

    return client_class(**kwargs)
