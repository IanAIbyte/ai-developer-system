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


class GLM5Client:
    """
    GLM API 客户端（支持 GLM Coding Plan Pro 套餐）

    文档: https://docs.bigmodel.cn/cn/api/introduction
    套餐: https://www.bigmodel.cn/glm-coding

    支持的套餐和模型：
    - Pro 套餐：glm-4.7（推荐）、glm-4.6、glm-4.5、glm-4.5-air
    - Max 套餐：glm-5、glm-4.7 等
    """

    API_BASE = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

    # 根据套餐选择合适的模型
    # Pro 套餐推荐使用 glm-4.7（专为代码生成优化）
    # Max 套餐可以使用 glm-5
    MODEL_NAME = "glm-4.7"  # 默认使用 GLM-4.7（Pro 套餐最佳选择）

    # 可选模型列表
    AVAILABLE_MODELS = {
        "glm-4.7": "GLM-4.7（推荐）- Pro/Max 套餐，代码生成优化",
        "glm-4.6": "GLM-4.6 - Pro/Max 套餐",
        "glm-4.5": "GLM-4.5 - Pro/Max 套餐",
        "glm-4.5-air": "GLM-4.5-Air - 轻量级，所有套餐",
        "glm-5": "GLM-5 - 仅 Max 套餐"
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

        self.client = httpx.Client(
            base_url=self.API_BASE,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=120.0
        )

    def chat_completion(
            self,
            messages: List[Dict],
            tools: Optional[List[Dict]] = None,
            temperature: float = 0.7,
            max_tokens: int = 4096,
            stream: bool = False
    ) -> Dict:
        """
        调用 GLM-5 对话补全 API

        Args:
            messages: 对话消息列表
                [{"role": "user", "content": "..."}]
            tools: 工具列表（Function Calling）
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

        if tools:
            payload["tools"] = tools

        try:
            # base_url 已经包含完整路径，直接传空字符串
            response = self.client.post("", json=payload)
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

        response = self.chat_completion(
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
            user_prompt: str
    ) -> List[Dict]:
        """
        分析用户需求，生成功能列表

        Args:
            user_prompt: 用户的原始需求描述

        Returns:
            功能列表，每个功能包含：
            {
                "id": "category-action-001",
                "category": "authentication",
                "priority": "critical/high/medium/low",
                "description": "User can ...",
                "steps": ["step 1", "step 2", ...],
                "passes": false,
                "dependencies": []
            }
        """
        system_prompt = """你是一个专业的产品经理和技术架构师 AI。

任务：将用户的需求分解为 200+ 个细粒度的、可测试的功能。

每个功能应该：
1. 聚焦于单个用户行为或系统功能
2. 包含清晰的 E2E 测试步骤
3. 有明确的优先级
4. 标注依赖关系

功能 ID 格式：category-action-number (例如：auth-login-001)

分类：
- setup: 项目设置和配置
- auth: 认证和授权
- ui: 用户界面组件
- api: API 端点
- database: 数据模型和操作
- testing: 测试相关
- deployment: 部署和运维

优先级：
- critical: 核心功能，没有它应用无法使用
- high: 重要功能
- medium: 常规功能
- low: 增强功能

输出格式：JSON 数组
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"""请将以下用户需求分解为详细的功能列表：

{user_prompt}

要求：
1. 生成 200+ 个功能
2. 每个功能都包含 E2E 测试步骤
3. 使用 JSON 格式输出
4. 功能 ID 按分类和编号命名"""
            }
        ]

        response = self.chat_completion(
            messages=messages,
            temperature=0.5,
            max_tokens=16384  # 功能列表可能很长
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
