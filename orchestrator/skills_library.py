"""
Skills Library - 可复用技能模式库

职责：
1. 管理常见开发任务的技能模式
2. 提供技能发现和推荐
3. 技能版本管理和兼容性检查
4. 与 Coding Agent 集成

基于 Gemini Pro 3 的建议：
- 完善"技能库"系统
- 可复用的模式库
- 智能推荐相关技能
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class SkillPattern:
    """技能模式定义"""

    def __init__(self, skill_id: str, metadata: Dict):
        self.skill_id = skill_id
        self.name = metadata.get("name", skill_id)
        self.category = metadata.get("category", "general")
        self.description = metadata.get("description", "")
        self.pattern = metadata.get("pattern", {})
        self.examples = metadata.get("examples", [])
        self.compatibility = metadata.get("compatibility", {})
        self.version = metadata.get("version", "1.0.0")
        self.tags = metadata.get("tags", [])

    def matches_feature(self, feature: Dict) -> float:
        """
        计算技能与功能的匹配度 (0-1)

        Args:
            feature: 功能定义

        Returns:
            匹配分数 (0-1)
        """
        score = 0.0

        # 1. 类别匹配
        if self.category == feature.get("category"):
            score += 0.3

        # 2. 标签匹配
        feature_tags = feature.get("tags", [])
        tag_overlap = set(self.tags) & set(feature_tags)
        if tag_overlap:
            score += 0.3 * (len(tag_overlap) / max(len(self.tags), 1))

        # 3. 描述相似度（简单关键词匹配）
        feature_desc = feature.get("description", "").lower()
        for keyword in self.pattern.get("keywords", []):
            if keyword.lower() in feature_desc:
                score += 0.1

        # 4. 复杂度匹配
        if self.pattern.get("complexity_level") == feature.get("logical_requirements", {}).get("complexity_level"):
            score += 0.2

        # 5. 集成点匹配
        skill_integrations = set(self.pattern.get("integration_points", []))
        feature_integrations = set(feature.get("logical_requirements", {}).get("integration_points", []))

        if skill_integrations and feature_integrations:
            integration_overlap = skill_integrations & feature_integrations
            score += 0.1 * (len(integration_overlap) / max(len(skill_integrations), 1))

        return min(score, 1.0)


class SkillsLibrary:
    """技能库管理系统"""

    def __init__(self, library_path: Optional[str] = None):
        """
        初始化技能库

        Args:
            library_path: 技能库文件路径（默认为 orchestrator/skills/）
        """
        if library_path is None:
            library_path = Path(__file__).parent / "skills"

        self.library_path = Path(library_path)
        self.skills: Dict[str, SkillPattern] = {}
        self._load_skills()

    def _load_skills(self):
        """加载所有技能模式"""
        if not self.library_path.exists():
            self.library_path.mkdir(parents=True, exist_ok=True)
            self._create_default_skills()
            return

        for skill_file in self.library_path.glob("*.json"):
            try:
                with open(skill_file, 'r', encoding='utf-8') as f:
                    skill_data = json.load(f)
                    skill_id = skill_file.stem

                    self.skills[skill_id] = SkillPattern(skill_id, skill_data)
            except Exception as e:
                print(f"  ⚠️  Failed to load skill {skill_file}: {e}")

        print(f"  📚 Loaded {len(self.skills)} skills from library")

    def _create_default_skills(self):
        """创建默认技能模式"""
        default_skills = {
            "api_rest_crud": {
                "name": "RESTful CRUD API",
                "category": "api",
                "description": "创建 RESTful CRUD 端点（Create, Read, Update, Delete）",
                "tags": ["api", "crud", "rest", "database"],
                "version": "1.0.0",
                "pattern": {
                    "complexity_level": "medium",
                    "keywords": ["crud", "api", "rest", "create", "read", "update", "delete"],
                    "integration_points": ["database", "validation", "error handling"],
                    "forbidden_patterns": ["禁止硬编码SQL", "禁止没有验证的输入"]
                },
                "examples": [
                    {
                        "description": "创建用户管理 API",
                        "endpoints": ["/api/users (GET, POST)", "/api/users/{id} (GET, PUT, DELETE)"],
                        "tech_stack": ["FastAPI", "SQLAlchemy", "Pydantic"]
                    }
                ],
                "compatibility": {
                    "templates": ["api", "webapp"],
                    "python_version": ">=3.8",
                    "dependencies": ["fastapi", "sqlalchemy", "pydantic"]
                }
            },

            "ui_form_validation": {
                "name": "表单验证 UI 组件",
                "category": "ui",
                "description": "创建带验证的表单组件（客户端 + 服务端验证）",
                "tags": ["ui", "form", "validation", "input"],
                "version": "1.0.0",
                "pattern": {
                    "complexity_level": "medium",
                    "keywords": ["form", "validation", "input", "submit"],
                    "integration_points": ["state management", "error handling", "API integration"],
                    "forbidden_patterns": ["禁止只在客户端验证", "禁止没有错误提示"]
                },
                "examples": [
                    {
                        "description": "用户注册表单",
                        "fields": ["email", "password", "confirm_password"],
                        "validations": ["email格式", "密码强度", "密码确认"],
                        "tech_stack": ["React Hook Form", "Zod", "Tailwind CSS"]
                    }
                ],
                "compatibility": {
                    "templates": ["webapp"],
                    "dependencies": ["react-hook-form", "zod"]
                }
            },

            "auth_jwt": {
                "name": "JWT 认证系统",
                "category": "authentication",
                "description": "实现基于 JWT 的用户认证（注册、登录、令牌刷新）",
                "tags": ["auth", "jwt", "authentication", "security"],
                "version": "1.0.0",
                "pattern": {
                    "complexity_level": "high",
                    "keywords": ["auth", "authentication", "jwt", "login", "register", "token"],
                    "integration_points": ["database", "password hashing", "middleware", "API"],
                    "forbidden_patterns": [
                        "禁止明文存储密码",
                        "禁止在 localStorage 存储敏感信息",
                        "禁止没有过期时间的令牌"
                    ]
                },
                "examples": [
                    {
                        "description": "用户认证流程",
                        "flow": ["注册 → 哈希密码 → 存储", "登录 → 验证密码 → 生成 JWT", "API 调用 → 验证 JWT → 返回数据"],
                        "tech_stack": ["bcrypt", "PyJWT", "httpx", "cookies"]
                    }
                ],
                "compatibility": {
                    "templates": ["api", "webapp"],
                    "dependencies": ["bcrypt", "pyjwt", "python-jose"]
                }
            },

            "state_management_zustand": {
                "name": "Zustand 状态管理",
                "category": "data",
                "description": "使用 Zustand 实现全局状态管理",
                "tags": ["state", "store", "zustand", "global"],
                "version": "1.0.0",
                "pattern": {
                    "complexity_level": "medium",
                    "keywords": ["state", "store", "global", "management"],
                    "integration_points": ["ui components", "persistence"],
                    "forbidden_patterns": ["禁止在多个组件中重复状态", "禁止没有类型定义"]
                },
                "examples": [
                    {
                        "description": "用户状态管理",
                        "store": ["user", "token", "loginAction", "logoutAction"],
                        "persistence": "localStorage sync",
                        "tech_stack": ["zustand", "TypeScript"]
                    }
                ],
                "compatibility": {
                    "templates": ["webapp"],
                    "dependencies": ["zustand"]
                }
            },

            "llm_integration": {
                "name": "LLM API 集成",
                "category": "api",
                "description": "集成 LLM API（如 GLM-5, Claude）进行智能处理",
                "tags": ["llm", "ai", "api", "optimization"],
                "version": "1.0.0",
                "pattern": {
                    "complexity_level": "high",
                    "keywords": ["llm", "ai", "optimization", "智能", "glm", "claude"],
                    "integration_points": ["API", "error handling", "retry logic", "fallback"],
                    "forbidden_patterns": [
                        "禁止简单字符串拼接",
                        "禁止没有错误处理的 API 调用",
                        "禁止没有重试机制的 API 调用"
                    ]
                },
                "examples": [
                    {
                        "description": "提示词优化 API",
                        "flow": ["接收输入 → 构建 prompt → 调用 LLM → 返回优化结果"],
                        "retry": "3次重试，指数退避",
                        "fallback": "智能规则系统",
                        "tech_stack": ["httpx", "GLM-5 API", "规则引擎"]
                    }
                ],
                "compatibility": {
                    "templates": ["api", "webapp"],
                    "dependencies": ["httpx"]
                }
            },

            "testing_e2e_playwright": {
                "name": "Playwright E2E 测试",
                "category": "testing",
                "description": "使用 Playwright 编写端到端测试",
                "tags": ["testing", "e2e", "playwright", "automation"],
                "version": "1.0.0",
                "pattern": {
                    "complexity_level": "medium",
                    "keywords": ["test", "e2e", "testing", "playwright"],
                    "integration_points": ["ui components", "API", "fixtures"],
                    "forbidden_patterns": [
                        "禁止测试实现细节",
                        "禁止没有断言的测试",
                        "禁止硬编码等待时间"
                    ]
                },
                "examples": [
                    {
                        "description": "用户登录流程测试",
                        "steps": ["导航到登录页", "输入凭证", "点击提交", "验证重定向"],
                        "tech_stack": ["Playwright", "pytest"]
                    }
                ],
                "compatibility": {
                    "templates": ["webapp"],
                    "dependencies": ["playwright", "pytest"]
                }
            },

            "error_boundary": {
                "name": "React 错误边界",
                "category": "ui",
                "description": "实现错误边界组件捕获运行时错误",
                "tags": ["error", "boundary", "ui", "react"],
                "version": "1.0.0",
                "pattern": {
                    "complexity_level": "low",
                    "keywords": ["error", "boundary", "fallback", "crash"],
                    "integration_points": ["ui components", "logging"],
                    "forbidden_patterns": ["禁止静默失败", "禁止没有错误日志"]
                },
                "examples": [
                    {
                        "description": "全局错误边界",
                        "features": ["捕获子组件错误", "显示友好错误页", "上报错误日志"],
                        "tech_stack": ["React", "Error Boundary"]
                    }
                ],
                "compatibility": {
                    "templates": ["webapp"],
                    "dependencies": ["react"]
                }
            },

            "file_upload_s3": {
                "name": "文件上传到 S3",
                "category": "api",
                "description": "实现文件上传到 S3（预签名 URL + 直传）",
                "tags": ["upload", "file", "s3", "storage"],
                "version": "1.0.0",
                "pattern": {
                    "complexity_level": "high",
                    "keywords": ["upload", "file", "s3", "storage", "image"],
                    "integration_points": ["API", "S3", "validation", "progress tracking"],
                    "forbidden_patterns": [
                        "禁止通过后端中转大文件",
                        "禁止没有文件类型验证",
                        "禁止没有文件大小限制"
                    ]
                },
                "examples": [
                    {
                        "description": "图片上传流程",
                        "flow": ["前端选择文件 → 调用 API 获取预签名 URL → 直传 S3 → 返回文件路径"],
                        "validations": ["文件类型（image/*）", "文件大小（<5MB）"],
                        "tech_stack": ["boto3", "S3", "预签名 URL"]
                    }
                ],
                "compatibility": {
                    "templates": ["api", "webapp"],
                    "dependencies": ["boto3"]
                }
            }
        }

        # 保存默认技能
        for skill_id, skill_data in default_skills.items():
            skill_file = self.library_path / f"{skill_id}.json"
            with open(skill_file, 'w', encoding='utf-8') as f:
                json.dump(skill_data, f, indent=2, ensure_ascii=False)

            self.skills[skill_id] = SkillPattern(skill_id, skill_data)

        print(f"  📚 Created {len(self.skills)} default skills")

    def recommend_skills(
        self,
        feature: Dict,
        top_k: int = 3,
        min_score: float = 0.3
    ) -> List[Tuple[str, SkillPattern, float]]:
        """
        为功能推荐相关技能

        Args:
            feature: 功能定义
            top_k: 返回前 k 个技能
            min_score: 最低匹配分数

        Returns:
            [(skill_id, skill_pattern, score), ...] 按分数降序排列
        """
        scores = []

        for skill_id, skill in self.skills.items():
            score = skill.matches_feature(feature)

            if score >= min_score:
                scores.append((skill_id, skill, score))

        # 按分数降序排序
        scores.sort(key=lambda x: x[2], reverse=True)

        return scores[:top_k]

    def get_skill_by_id(self, skill_id: str) -> Optional[SkillPattern]:
        """根据 ID 获取技能"""
        return self.skills.get(skill_id)

    def get_skills_by_category(self, category: str) -> List[SkillPattern]:
        """根据类别获取技能"""
        return [skill for skill in self.skills.values() if skill.category == category]

    def get_all_categories(self) -> List[str]:
        """获取所有类别"""
        categories = set(skill.category for skill in self.skills.values())
        return sorted(categories)

    def check_compatibility(
        self,
        skill_id: str,
        template: str,
        dependencies: List[str]
    ) -> Tuple[bool, List[str]]:
        """
        检查技能兼容性

        Args:
            skill_id: 技能 ID
            template: 项目模板
            dependencies: 项目依赖列表

        Returns:
            (is_compatible, missing_dependencies)
        """
        skill = self.get_skill_by_id(skill_id)

        if not skill:
            return False, ["Skill not found"]

        # 检查模板兼容性
        compatible_templates = skill.compatibility.get("templates", [])
        if compatible_templates and template not in compatible_templates:
            return False, [f"Template '{template}' not supported"]

        # 检查依赖
        required_deps = skill.compatibility.get("dependencies", [])
        missing_deps = [dep for dep in required_deps if dep not in dependencies]

        is_compatible = len(missing_deps) == 0

        return is_compatible, missing_deps

    def add_skill(self, skill_id: str, metadata: Dict) -> bool:
        """
        添加新技能

        Args:
            skill_id: 技能 ID
            metadata: 技能元数据

        Returns:
            是否成功
        """
        try:
            # 验证必需字段
            required_fields = ["name", "category", "description", "pattern"]
            for field in required_fields:
                if field not in metadata:
                    raise ValueError(f"Missing required field: {field}")

            # 保存到文件
            skill_file = self.library_path / f"{skill_id}.json"
            with open(skill_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            # 添加到内存
            self.skills[skill_id] = SkillPattern(skill_id, metadata)

            return True

        except Exception as e:
            print(f"  ❌ Failed to add skill {skill_id}: {e}")
            return False

    def import_skill_from_session(
        self,
        session_transcript: str,
        feature: Dict,
        skill_id: Optional[str] = None
    ) -> bool:
        """
        从会话记录中提取并保存技能模式

        Args:
            session_transcript: 会话记录文本
            feature: 相关功能
            skill_id: 技能 ID（可选，自动生成）

        Returns:
            是否成功
        """
        # 生成技能 ID（如果没有提供）
        if skill_id is None:
            # 基于功能 ID 和内容哈希生成
            content_hash = hashlib.md5(session_transcript.encode()).hexdigest()[:8]
            skill_id = f"{feature.get('category', 'general')}-{content_hash}"

        # TODO: 使用 LLM 提取技能模式
        # 这里可以调用 GLM-5 分析会话记录，提取可复用的模式
        print(f"  🔍 Analyzing session for skill extraction...")

        # 暂时返回 False，等待 LLM 集成
        return False


# 全局函数
def get_skills_library(library_path: Optional[str] = None) -> SkillsLibrary:
    """
    获取技能库实例

    Args:
        library_path: 技能库路径（可选）

    Returns:
        SkillsLibrary 实例
    """
    return SkillsLibrary(library_path)


def recommend_skills_for_feature(
    feature: Dict,
    top_k: int = 3
) -> List[Dict]:
    """
    为功能推荐技能的便捷函数

    Args:
        feature: 功能定义
        top_k: 返回前 k 个技能

    Returns:
        推荐技能列表
    """
    library = get_skills_library()
    recommendations = library.recommend_skills(feature, top_k=top_k)

    results = []
    for skill_id, skill, score in recommendations:
        results.append({
            "skill_id": skill_id,
            "name": skill.name,
            "category": skill.category,
            "description": skill.description,
            "match_score": score,
            "pattern": skill.pattern,
            "examples": skill.examples
        })

    return results
