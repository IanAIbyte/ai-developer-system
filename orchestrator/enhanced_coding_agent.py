"""
Enhanced Coding Agent - 增强的编码代理（集成 GLM-5 API）

职责：
1. 使用真实的 LLM API 进行代码生成
2. 智能分析项目结构
3. 自动生成代码文件
4. 提供代码审查建议
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from .llm_clients import GLM5Client, get_llm_client


class EnhancedCodingAgent:
    """
    增强的编码代理

    使用 GLM-5 API 进行真实的代码生成和项目开发
    """

    def __init__(
            self,
            project_path: str,
            llm_provider: str = "glm-5",
            session_id: Optional[str] = None
    ):
        """
        初始化增强的编码代理

        Args:
            project_path: 项目路径
            llm_provider: LLM 提供商 ("glm-5" 或 "claude")
            session_id: 会话 ID
        """
        self.project_path = Path(project_path).absolute()
        self.llm_provider = llm_provider
        self.session_id = session_id or self._generate_session_id()
        self.timestamp = datetime.now().isoformat()

        # 初始化 LLM 客户端
        try:
            self.llm_client = get_llm_client(llm_provider)
            print(f"[EnhancedCodingAgent] Using {llm_provider.upper()} for code generation")
        except Exception as e:
            print(f"[EnhancedCodingAgent] ⚠️  LLM client initialization failed: {e}")
            print(f"[EnhancedCodingAgent] Will use simulation mode")
            self.llm_client = None

    def implement_feature_real(
            self,
            feature: Dict,
            context: Dict
    ) -> Dict:
        """
        使用真实的 LLM API 实现功能

        Args:
            feature: 要实现的功能
            context: 项目上下文

        Returns:
            实现结果字典
        """
        if not self.llm_client:
            # Fallback 到模拟模式
            return self._implement_feature_simulation(feature, context)

        print(f"    [GLM-5] Generating code for: {feature['description']}")
        print(f"    [GLM-5] Feature ID: {feature['id']}")

        # 1. 分析项目结构
        print(f"    [GLM-5] Analyzing project structure...")
        project_structure = self._analyze_project_structure()

        # 2. 构建代码生成提示
        code_gen_prompt = self._build_code_generation_prompt(
            feature=feature,
            context=context,
            project_structure=project_structure
        )

        # 3. 调用 LLM 生成代码
        try:
            generated_code = self.llm_client.generate_code(
                prompt=code_gen_prompt,
                context=context.get("progress", ""),
                file_structure=project_structure
            )

            print(f"    [GLM-5] ✅ Code generation complete ({len(generated_code)} chars)")

            # 4. 解析并保存生成的代码
            files_created = self._save_generated_code(
                generated_code=generated_code,
                feature_id=feature["id"]
            )

            print(f"    [GLM-5] ✅ Created/modified {len(files_created)} files")

            return {
                "success": True,
                "files_created": files_created,
                "generation_method": "glm-5-api",
                "feature_id": feature["id"]
            }

        except Exception as e:
            print(f"    [GLM-5] ❌ Code generation failed: {e}")
            print(f"    [GLM-5] Falling back to simulation mode")

            return self._implement_feature_simulation(feature, context)

    def _analyze_project_structure(self) -> Dict:
        """分析项目结构"""
        structure = {
            "root": str(self.project_path),
            "directories": [],
            "files": []
        }

        # 扫描目录
        for item in self.project_path.rglob("*"):
            if item.is_dir():
                # 排除隐藏目录和 node_modules
                if not item.name.startswith(".") and item.name != "node_modules":
                    rel_path = item.relative_to(self.project_path)
                    structure["directories"].append(str(rel_path))
            else:
                # 只包含源代码文件
                if item.suffix in [".js", ".ts", ".tsx", ".jsx", ".py", ".json"]:
                    rel_path = item.relative_to(self.project_path)
                    structure["files"].append(str(rel_path))

        return structure

    def _build_code_generation_prompt(
            self,
            feature: Dict,
            context: Dict,
            project_structure: Dict
    ) -> str:
        """构建代码生成的提示词"""
        prompt = f"""
## 功能需求

**功能 ID**: {feature['id']}
**类别**: {feature.get('category', 'unknown')}
**优先级**: {feature.get('priority', 'medium')}
**描述**: {feature['description']}

## E2E 测试步骤
"""
        for i, step in enumerate(feature.get("steps", []), 1):
            prompt += f"{i}. {step}\n"

        prompt += f"""

## 技术栈

根据项目模板使用相应的技术栈：
- **前端**: React/Next.js + TypeScript
- **样式**: Tailwind CSS
- **状态管理**: React Hooks (useState, useEffect)
- **数据持久化**: localStorage 或 API

## 实现要求

请提供完整的实现代码，包括：

1. **组件代码** (如果有 UI)
   - TypeScript 类型定义
   - React Hooks 使用
   - Props 接口定义

2. **样式代码** (如果需要)
   - Tailwind CSS 类名
   - 响应式设计

3. **数据处理逻辑**
   - 输入验证
   - 错误处理
   - 用户反馈

4. **集成说明**
   - 如何将此功能集成到现有代码
   - 需要修改哪些现有文件

## 代码质量要求

- ✅ 不可变数据结构（immutable）
- ✅ 完整的错误处理
- ✅ TypeScript 类型安全
- ✅ 可访问性（ARIA 标签）
- ✅ 清晰的命名和注释
- ✅ 单一职责原则

请按照以下格式输出：

```markdown
# 实现方案

## 1. 新增文件

### 文件路径: `src/components/...`
\`\`\`typescript
// 代码
\`\`\`

## 2. 修改文件

### 文件路径: `src/pages/...`
- 添加 import
- 修改组件

## 3. 集成步骤

1. ...
2. ...
```
"""

        return prompt

    def _save_generated_code(
            self,
            generated_code: str,
            feature_id: str
    ) -> List[str]:
        """
        解析并保存生成的代码

        Args:
            generated_code: LLM 生成的代码文本
            feature_id: 功能 ID

        Returns:
            创建或修改的文件路径列表
        """
        files_created = []

        # 简化实现：将生成的代码保存到文件
        # 实际应该解析 markdown 格式的输出

        # 创建功能实现目录
        impl_dir = self.project_path / "src" / "features" / feature_id
        impl_dir.mkdir(parents=True, exist_ok=True)

        # 保存生成的代码
        impl_file = impl_dir / f"{feature_id}.md"
        with open(impl_file, 'w', encoding='utf-8') as f:
            f.write(f"# {feature_id} - Generated Implementation\n\n")
            f.write(generated_code)

        files_created.append(str(impl_file))

        # TODO: 解析 markdown 中的代码块并创建实际文件
        # TODO: 提取 TypeScript 代码并保存为 .ts/.tsx 文件
        # TODO: 提取样式代码并整合到现有组件

        return files_created

    def _implement_feature_simulation(self, feature: Dict, context: Dict) -> Dict:
        """模拟实现（fallback）"""
        print(f"    [Simulation] Implementing: {feature['description']}")

        # 创建模拟实现文件
        impl_dir = self.project_path / "src" / "features" / feature["id"]
        impl_dir.mkdir(parents=True, exist_ok=True)

        impl_file = impl_dir / "implementation.md"
        with open(impl_file, 'w', encoding='utf-8') as f:
            f.write(f"# {feature['id']} - Implementation\n\n")
            f.write(f"## Description\n{feature['description']}\n\n")
            f.write(f"## Steps\n")
            for i, step in enumerate(feature.get("steps", []), 1):
                f.write(f"{i}. {step}\n")

        return {
            "success": True,
            "files_created": [str(impl_file)],
            "generation_method": "simulation",
            "feature_id": feature["id"]
        }

    def _generate_session_id(self) -> str:
        """生成会话 ID"""
        return datetime.now().strftime("%Y%m%d-%H%M%S")
