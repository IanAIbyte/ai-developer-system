# AI Developer System - Autonomous Development Environment

## 🎯 项目愿景

构建一个能够自主运行、自我迭代的 AI 开发环境，基于 Anthropic 的长运行代理框架。

## 🏗️ 架构设计

### 核心组件

```
ai-developer-system/
├── .claude/                    # Claude Code 配置
│   ├── agents/                 # 专用代理定义
│   ├── hooks/                  # 生命周期钩子
│   └── skills/                 # 技能定义
├── orchestrator/               # 调度器核心
│   ├── initializer_agent.py    # 初始化代理
│   ├── coding_agent.py         # 编码代理
│   ├── scheduler.py            # 任务调度器
│   └── state_manager.py        # 状态管理器
├── runtime/                    # 运行时环境
│   ├── workspace/              # 动态工作空间
│   ├── logs/                   # 会话日志
│   └── checkpoints/            # 检查点
├── tools/                      # 工具集成
│   ├── mcp_servers/            # MCP 服务器集成
│   ├── testing/                # 自动化测试工具
│   └── validators/             # 代码验证器
├── templates/                  # 项目模板
│   ├── webapp/                # Web 应用模板
│   ├── api/                   # API 服务模板
│   └── library/               # 库项目模板
└── config/                     # 配置文件
    ├── agent_prompts.json      # 代理提示词
    └── feature_schemas.json    # 功能模式定义
```

## 🔄 工作流程

### 1. Initializer Agent Phase
```python
初始化步骤：
1. 分析用户需求
2. 生成 feature_list.json（200+ 细粒度功能）
3. 创建项目骨架
4. 编写 init.sh（开发服务器启动脚本）
5. 初始化 git 仓库
6. 创建 claude-progress.txt
7. 配置测试环境
```

### 2. Coding Agent Phase
```python
每个会话循环：
1. 快速上手（Get Up to Speed）
   - pwd → 确认工作目录
   - 读取 git log → 了解最近工作
   - 读取 claude-progress.txt → 理解进度
   - 读取 feature_list.json → 选择下一个功能
   - 运行 init.sh → 启动开发服务器
   - 运行基础测试 → 验证当前状态

2. 增量开发（Incremental Progress）
   - 选择单个高优先级功能
   - 实现/测试该功能
   - 使用浏览器自动化工具进行 E2E 测试
   - 验证功能完全可用

3. 清理状态（Clean State）
   - git commit（详细的提交信息）
   - 更新 claude-progress.txt
   - 更新 feature_list.json 中的 passes 字段
   - 确保环境处于可合并状态
```

## 📋 关键文件格式

### feature_list.json
```json
{
  "features": [
    {
      "id": "auth-login-001",
      "category": "authentication",
      "priority": "critical",
      "description": "User can enter credentials and successfully log in",
      "steps": [
        "Navigate to login page",
        "Enter valid username",
        "Enter valid password",
        "Click login button",
        "Verify redirect to dashboard",
        "Verify session token stored"
      ],
      "passes": false,
      "dependencies": [],
      "estimated_complexity": "medium"
    }
  ]
}
```

### claude-progress.txt
```
=== AI Developer System Progress Log ===
Project: Todo App with AI Features
Started: 2025-02-14

[Session 1] 2025-02-14 09:00-10:30
Agent: Initializer
Completed:
- Set up Next.js project with TypeScript
- Configured Tailwind CSS
- Generated 247 feature requirements
- Set up Playwright for E2E testing
- Created init.sh script
Git commit: feat: initial project setup with feature list

[Session 2] 2025-02-14 10:35-12:00
Agent: Coding
Feature: auth-login-001
Status: COMPLETED
Changes:
- Implemented login form component
- Added JWT authentication
- Created /api/auth/login endpoint
- Added session management
Testing:
- E2E tests passing (3/3)
- Screenshot verification passed
Git commit: feat: implement user login with JWT authentication

Next priorities:
1. auth-logout-002
2. auth-register-003
3. todos-create-001
```

## 🤖 专用代理系统

基于 Anthropic 的未来工作方向，实现多代理架构：

### 1. Initializer Agent
- **职责**: 项目初始化、环境设置
- **触发**: 项目创建时
- **输出**: feature_list.json, init.sh, git repo

### 2. Coding Agent
- **职责**: 功能实现、增量开发
- **触发**: 每次会话
- **输出**: git commits, progress updates

### 3. Testing Agent
- **职责**: 自动化测试、质量保证
- **触发**: Coding Agent 完成功能后
- **输出**: 测试报告、bug 发现

### 4. Code Review Agent
- **职责**: 代码审查、安全检查
- **触发**: 每个 git commit
- **输出**: 审查报告、改进建议

### 5. Cleanup Agent
- **职责**: 代码清理、重构
- **触发**: 每日/每周
- **输出**: 重构 commits、文档更新

### 6. QA Agent
- **职责**: 最终质量验证
- **触发**: 功能完成时
- **输出**: 验证报告、发布就绪确认

## 🔧 技术栈

### 核心框架
- **Claude Agent SDK**: 代理编排
- **MCP (Model Context Protocol)**: 工具集成
- **Git**: 版本控制和状态管理
- **JSON**: 结构化数据存储

### 测试工具
- **Playwright/Puppeteer**: E2E 测试
- **pytest/Jest**: 单元测试
- **MCP Server**: 测试自动化

### 状态管理
- **Git commits**: 主要状态快照
- **Progress files**: 会话间状态传递
- **Feature list JSON**: 功能跟踪

## 📊 成功指标

1. **功能完成率**: feature_list.json 中 passes=true 的百分比
2. **测试覆盖率**: E2E 测试通过率 >95%
3. **代码质量**: 每个 commit 都可合并到 main
4. **会话效率**: 每次会话至少完成 1 个功能
5. **bug 率**: 基础测试通过率 >90%

## 🚀 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 配置 API Key（必需）
export ZHIPUAI_API_KEY=your_api_key_here

# 测试 API 连接
python3 test_glm5_connection.py

# 初始化新项目
python3 -m orchestrator.initializer_agent \
  --prompt "Build a clone of claude.ai" \
  --template webapp

# 启动自主开发循环
python3 -m orchestrator.scheduler \
  --project ./workspace/claude-ai-clone \
  --mode autonomous
```

## 📖 完整使用方法

AI Developer System 提供多种使用方式，从简单命令行到编程接口，满足不同场景需求。

---

### 方法 1: 命令行直接传递（最简单）

适用于：快速原型、简单项目

```bash
python3 -m orchestrator.initializer_agent \
    --project ./workspace/my-app \
    --template webapp \
    --prompt "构建一个待办事项应用"
```

**优点**: 一行命令，快速启动
**缺点**: 提示词过长时不便阅读

---

### 方法 2: 从文件读取提示词（⭐ 推荐）

适用于：复杂需求、需要版本控制的项目

```bash
# 步骤 1: 创建需求文件
mkdir -p ./workspace/prompt-generator-pro
cat > ./workspace/prompt-generator-pro/user_prompt.txt << 'EOF'
构建一个专业级提示词工程平台 'Prompt Lab Pro'。

核心功能：
1. 提示词工作台 - 编辑、测试、优化提示词
2. 多模型适配 - 支持 GPT-4、Claude、GLM-5
3. 版本控制 - Git 集成
4. 自动化测评 - LLM-as-a-Judge
5. 视觉排版对比

技术栈：
- 前端：Next.js + TypeScript
- 后端：FastAPI + Python
EOF

# 步骤 2: 运行初始化
python3 -m orchestrator.initializer_agent \
    --project ./workspace/prompt-generator-pro \
    --template webapp \
    --prompt "$(cat ./workspace/prompt-generator-pro/user_prompt.txt)"
```

**优点**:
- 需求文档可读性强
- 可以用 Git 版本控制
- 便于团队协作和评审

---

### 方法 3: 使用示例脚本

适用于：快速体验系统

```bash
# 直接运行系统提供的示例脚本
./examples/setup_new_project.sh
```

这会创建一个 Todo App 示例项目。

---

### 方法 4: Python API 编程方式

适用于：集成到其他应用、自定义工作流

```python
#!/usr/bin/env python3
from orchestrator.initializer_agent import InitializerAgent

# 从文件读取需求
with open("./workspace/my-app/user_prompt.txt", "r") as f:
    prompt = f.read()

# 创建并运行初始化代理
agent = InitializerAgent(
    project_path="./workspace/my-app",
    user_prompt=prompt,
    template="webapp"
)

result = agent.initialize()
print(f"✅ 成功生成 {result['feature_count']} 个功能")
```

运行：
```bash
python3 init_my_project.py
```

---

### 方法 5: 批量创建多个项目

适用于：微服务架构、多个相似项目

```bash
#!/bin/bash
# batch_init.sh

declare -A PROJECTS=(
    ["user-service"]="用户认证服务，使用 FastAPI + JWT"
    ["order-service"]="订单管理系统，支持 CRUD 操作"
    ["payment-service"]="支付网关集成，支持多渠道"
)

for project in "${!PROJECTS[@]}"; do
    echo "🚀 Creating $project..."

    mkdir -p "./workspace/$project"
    echo "${PROJECTS[$project]}" > "./workspace/$project/user_prompt.txt"

    python3 -m orchestrator.initializer_agent \
        --project "./workspace/$project" \
        --template api \
        --prompt "${PROJECTS[$project]}"

    echo "✅ $project created!"
done
```

运行：
```bash
chmod +x batch_init.sh
./batch_init.sh
```

---

### 方法 6: 交互式方式

适用于：不确定需求、探索性开发

```bash
#!/bin/bash
# interactive_init.sh

echo "🚀 AI Developer System - 交互式项目创建"
echo ""

read -p "项目名称: " project_name
read -p "项目类型 (webapp/api/library): " template
read -p "需求描述: " prompt

PROJECT_DIR="./workspace/$project_name"
mkdir -p "$PROJECT_DIR"

echo "$prompt" > "$PROJECT_DIR/user_prompt.txt"

python3 -m orchestrator.initializer_agent \
    --project "$PROJECT_DIR" \
    --template "$template" \
    --prompt "$prompt"

echo ""
echo "✅ 项目创建完成！"
echo "   目录: $PROJECT_DIR"
```

运行：
```bash
chmod +x interactive_init.sh
./interactive_init.sh
```

---

### 方法 7: 从现有文档读取

适用于：已有 Markdown 需求文档

```bash
# 从 README 或需求文档读取
python3 -m orchestrator.initializer_agent \
    --project ./workspace/my-app \
    --template webapp \
    --prompt "$(cat docs/requirements.md)"
```

---

## 📋 参数说明

### 初始化代理参数

| 参数 | 必需 | 说明 | 示例 |
|------|------|------|------|
| `--project` | ✅ | 项目目录路径 | `./workspace/my-app` |
| `--prompt` | ✅ | 用户需求描述 | `"构建一个博客系统"` |
| `--template` | ✅ | 项目模板类型 | `webapp`, `api`, `library` |

### 模板类型

| 模板 | 适用场景 | 技术栈示例 |
|------|----------|-----------|
| `webapp` | Web 应用 | Next.js, React, Vue |
| `api` | API 服务 | FastAPI, Express, Django |
| `library` | 工具库 | Python 包, npm 包 |

---

## 🎯 开发模式选择

初始化完成后，选择开发模式：

### 模式 1: 单功能开发（推荐调试）

```bash
python3 -m orchestrator.scheduler --project . --mode single-feature
```

完成一个功能后自动停止，适合调试和验证。

### 模式 2: 手动单次会话

```bash
python3 -m orchestrator.scheduler --project . --mode manual
```

运行单个会话，适合学习和理解系统行为。

### 模式 3: 自主开发（无人值守）

```bash
python3 -m orchestrator.scheduler --project . --mode autonomous
```

持续运行直到所有功能完成，适合生产环境。

---

## ✅ 验证初始化结果

```bash
cd ./workspace/your-project

# 查看生成的功能数量
cat feature_list.json | jq '.features | length'

# 查看高优先级功能
cat feature_list.json | jq '.features[] | select(.priority == "critical")'

# 查看进度日志
cat claude-progress.txt

# 检查项目结构
tree -L 2

# 查看初始化脚本
cat init.sh

# 检查测试配置
cat .claude/test_config.json
```

---

## 🔧 环境配置

### 配置 API Key

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，添加你的 API Keys
# ZHIPUAI_API_KEY=your_api_key_here
```

### 测试 API 连接

```bash
# 运行测试脚本
python3 test_glm5_connection.py
```

这会检查：
- ✅ 环境变量配置
- ✅ API 连接状态
- ✅ 功能生成能力

---

## 📊 方法对比

| 方法 | 适用场景 | 优点 | 缺点 |
|------|---------|------|------|
| 1. 命令行直接 | 快速测试 | 简单快速 | 提示词长时不便 |
| 2. 文件读取 ⭐ | 正式项目 | 可版本控制、易维护 | 需要额外文件 |
| 3. 示例脚本 | 快速体验 | 开箱即用 | 只能创建示例 |
| 4. Python API | 编程集成 | 灵活可扩展 | 需要写代码 |
| 5. 批量脚本 | 多个项目 | 自动化批量 | 配置较复杂 |
| 6. 交互式 | 不确定需求 | 友好交互 | 效率较低 |
| 7. 文档读取 | 已有文档 | 复用现有文档 | 需要格式化 |

## 📚 参考资料

- [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [Building Effective AI Agents](https://www.anthropic.com/research/building-effective-agents)
- [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

## 🎓 设计原则

1. **增量进步**: 每次会话只做一件事
2. **清晰状态**: 每次会话结束必须是干净状态
3. **完整测试**: 功能必须经过 E2E 测试
4. **可追溯性**: Git + Progress 文件双重记录
5. **自我修复**: 会话开始时先修复现有 bug

## 🔄 自我迭代机制

系统会自动：
1. 监控每次会话的效率
2. 识别常见失败模式
3. 调整代理提示词
4. 优化功能优先级
5. 进化项目模板

## 📖 架构详解

### 核心设计理念

本系统基于 Anthropic 的《Effective harnesses for long-running agents》研究，采用以下原则：

#### 1. 双代理解决方案
- **Initializer Agent**: 设置初始环境（功能列表、脚本、git）
- **Coding Agent**: 每次会话增量推进 + 清晰状态传递

#### 2. 四大失败模式预防

| 问题 | Initializer Agent | Coding Agent |
|------|------------------|---------------|
| 过早宣布完成 | 生成 200+ 细粒度功能列表 | 每次只选一个功能工作 |
| 留下 bug 环境 | 初始化 git + 进度文件 | 会话开始先运行基础测试 |
| 未测试就标记完成 | 创建功能列表 | 必须 E2E 测试通过才标记 |
| 浪费时间理解如何运行 | 编写 init.sh | 会话开始运行 init.sh |

#### 3. 快速上手标准步骤

每个 Coding Agent 会话开始时：
```bash
pwd                          # 确认工作目录
cat claude-progress.txt        # 了解进度
cat feature_list.json         # 了解功能列表
git log --oneline -20        # 了解最近工作
./init.sh                     # 启动开发服务器
# 运行基础测试               # 验证当前状态
```

#### 4. 增量开发 + 干净状态

```python
# ✅ 正确：单功能聚焦
session.work_on(feature="auth-login-001")
# → 实现
# → E2E 测试
# → Git commit
# → 更新进度
# → 结束（干净状态）

# ❌ 错误：一次做太多
session.work_on(features=["auth", "database", "ui", "api"])
# → 容易超时
# → 半完成状态
# → 下次会话无法恢复
```

### 与 Claude Code 集成

本系统设计为与 Claude Code 完美协作：

#### 当前实现（简化框架）
```python
# orchestrator/coding_agent.py
def _implement_feature(self, feature, context):
    # TODO: 集成 Claude Code API
    # 目前返回模拟结果
    return {"success": True}
```

#### 完整实现目标
```python
import anthropic

def _implement_feature(self, feature, context):
    # 使用 Claude Code 进行实际开发
    agent = Agent(
        model="claude-sonnet-4-5-20250929",
        tools=["read", "write", "bash", "browser"]
    )

    result = agent.run(f"""
Implement feature: {feature['id']}
Description: {feature['description']}
Context: {context['progress']}
""")

    return result
```

## 💡 常见使用场景

### 场景 1: 快速原型开发

```bash
# 一行命令创建项目
python3 -m orchestrator.initializer_agent \
    --project ./workspace/prototype \
    --template webapp \
    --prompt "快速原型：简单的 CRUD 应用，包含增删改查功能"

# 单功能模式验证
python3 -m orchestrator.scheduler --project ./workspace/prototype --mode single-feature
```

### 场景 2: 正式项目开发

```bash
# 1. 准备详细需求文档
mkdir -p ./workspace/my-project
cat > ./workspace/my-project/requirements.md << 'EOF'
# 企业级博客系统

## 功能需求
- 文章管理：创建、编辑、删除、发布
- 用户系统：注册、登录、权限管理
- 评论系统：支持回复、点赞
- 标签分类：多级分类、标签管理

## 技术栈
- 前端：Next.js 14 + TypeScript + Tailwind CSS
- 后端：FastAPI + PostgreSQL
- 部署：Docker + Nginx
EOF

# 2. 运行初始化
python3 -m orchestrator.initializer_agent \
    --project ./workspace/my-project \
    --template webapp \
    --prompt "$(cat ./workspace/my-project/requirements.md)"

# 3. 检查生成的功能列表
cat ./workspace/my-project/feature_list.json | jq '.features | length'
cat ./workspace/my-project/claude-progress.txt

# 4. 自主开发
python3 -m orchestrator.scheduler --project ./workspace/my-project --mode autonomous
```

### 场景 3: 微服务架构

```bash
# 批量创建多个微服务
for service in "user-service:用户认证和授权" \
               "order-service:订单管理系统" \
               "payment-service:支付网关集成" \
               "notification-service:消息通知服务"; do
    IFS=':' read -r name desc <<< "$service"
    mkdir -p "./workspace/$name"
    echo "$desc" > "./workspace/$name/user_prompt.txt"

    python3 -m orchestrator.initializer_agent \
        --project "./workspace/$name" \
        --template api \
        --prompt "$desc"
done
```

---

## 🎯 使用示例

### 示例 1: 创建 Todo App

```bash
# 1. 创建项目目录
mkdir my-todo-app
cd my-todo-app

# 2. 创建用户需求文件
cat > user_prompt.txt << 'EOF'
Build a simple todo app:
- Add new todos
- Mark todos complete
- Delete todos
- Filter by status
- Use Next.js + TypeScript
- Use localStorage for persistence
EOF

# 3. 运行初始化代理
python -m orchestrator.initializer_agent \
    --project . \
    --prompt "$(cat user_prompt.txt)" \
    --template webapp

# 4. 检查生成的功能列表
cat feature_list.json | jq '.features | length'

# 5. 运行自主开发
python -m orchestrator.scheduler \
    --project . \
    --mode autonomous
```

### 示例 2: 单功能开发（调试模式）

```bash
# 只完成一个功能后停止
python -m orchestrator.scheduler \
    --project ./my-todo-app \
    --mode single-feature

# 检查进度
cat claude-progress.txt

# 查看功能状态
cat feature_list.json | jq '.features[] | select(.passes == true)'
```

### 示例 3: 手动会话（学习模式）

```bash
# 运行单个会话，然后停止
python -m orchestrator.scheduler \
    --project ./my-todo-app \
    --mode manual

# 检查做了什么
git log --oneline -5
git show HEAD --stat
```

## 🔧 调试与监控

### 查看实时进度
```bash
# 功能完成进度
cat feature_list.json | jq '
  {
    total: .features | length,
    completed: [.features[] | select(.passes == true)] | length,
    percentage: ([.features[] | select(.passes == true)] | length / .features | length * 100)
  }
'

# 最近会话历史
tail -50 claude-progress.txt

# Git 提交历史
git log --oneline --graph -20
```

### 检查点管理
```python
from orchestrator.state_manager import StateManager

sm = StateManager("./my-todo-app")

# 创建检查点
checkpoint_id = sm.save_checkpoint(
    session_id="20250214-123000",
    description="Before implementing feature X"
)

# 列出所有检查点
checkpoints = sm.list_checkpoints()
for cp in checkpoints:
    print(f"{cp['checkpoint_id']}: {cp['description']}")

# 恢复到检查点
sm.restore_checkpoint(checkpoint_id)
```

### 进度指标
```python
from orchestrator.state_manager import StateManager

sm = StateManager("./my-todo-app")
metrics = sm.get_progress_metrics()

print(f"完成度: {metrics['completion_percentage']}%")
print(f"已完成: {metrics['completed_features']}/{metrics['total_features']}")
print(f"预计剩余会话: {metrics['estimated_sessions_remaining']}")
```

## 💎 最佳实践

### 1. 需求描述原则

**好的需求描述**：
```
构建一个电商平台的订单管理模块。

核心功能：
1. 订单创建 - 从购物车生成订单
2. 订单查询 - 支持多条件筛选
3. 订单状态管理 - 待支付、已发货、已完成等
4. 退款处理 - 支持全额和部分退款

技术要求：
- 使用 TypeScript + React
- 状态管理：Zustand
- API 通信：React Query
- 表单验证：Zod
```

**不好的需求描述**：
```
做一个订单系统
```

### 2. 项目组织建议

```bash
# 推荐的项目结构
workspace/
├── project-a/              # 项目 A
│   ├── user_prompt.txt     # 原始需求
│   ├── feature_list.json   # 功能列表
│   ├── claude-progress.txt # 进度日志
│   └── src/                # 源代码
├── project-b/              # 项目 B
└── shared/                 # 共享资源
    └── templates/          # 可复用模板
```

### 3. 版本控制建议

```bash
# 1. 初始化项目后立即创建 Git 仓库
cd ./workspace/my-project
git init
git add .
git commit -m "feat: initial project setup by AI Developer System"

# 2. 将原始需求纳入版本控制
git add user_prompt.txt feature_list.json
git commit -m "docs: add project requirements and feature list"

# 3. 定期备份进度
cp claude-progress.txt claude-progress-backup-$(date +%Y%m%d).txt
git add claude-progress-backup-*.txt
git commit -m "backup: progress checkpoint"
```

### 4. 开发工作流

```bash
# 步骤 1: 初始化项目（一次性）
python3 -m orchestrator.initializer_agent \
    --project ./workspace/my-project \
    --template webapp \
    --prompt "$(cat requirements.md)"

# 步骤 2: 验证功能列表
cat ./workspace/my-project/feature_list.json | jq '.features | length'
cat ./workspace/my-project/feature_list.json | jq '.features[:3]'

# 步骤 3: 单功能测试（推荐先运行）
python3 -m orchestrator.scheduler \
    --project ./workspace/my-project \
    --mode single-feature

# 步骤 4: 检查第一个功能的实现
cd ./workspace/my-project
git log --oneline -5
git show HEAD --stat

# 步骤 5: 如果一切正常，切换到自主模式
python3 -m orchestrator.scheduler \
    --project ./workspace/my-project \
    --mode autonomous
```

### 5. 监控和调试

```bash
# 实时监控进度（在另一个终端）
watch -n 10 'cat feature_list.json | jq ".features | map(select(.passes == true)) | length"'

# 查看最近的会话记录
tail -f claude-progress.txt

# 检查 Git 提交历史
git log --oneline --graph -10

# 查看功能依赖关系
python3 -c "
from orchestrator.coding_agent import CodingAgent
from orchestrator.state_manager import StateManager
import json

sm = StateManager('.')
with open('feature_list.json') as f:
    data = json.load(f)

agent = CodingAgent('.')
print(agent._visualize_dependency_graph(data['features']))
"
```

### 6. 质量保证

```bash
# 运行基础测试
cd ./workspace/my-project
./init.sh  # 启动开发服务器

# 手动验证关键功能
# 1. 检查生成的代码是否符合预期
cat src/app/page.tsx

# 2. 检查测试是否通过
npm test

# 3. 检查代码质量
npm run lint

# 4. 检查构建是否成功
npm run build
```

---

## 🚨 故障排除

### 问题 1: API 调用时间过长

**症状**：`[Initializer] Using GLM-5 API to generate features...` 后长时间无响应

**原因**：
- 复杂提示词需要更多推理时间
- 网络连接较慢
- API 服务器负载较高

**解决方案**：

```bash
# 1. 首先测试 API 连接
python3 test_glm5_connection.py

# 2. 检查网络连接
ping open.bigmodel.cn

# 3. 如果连接正常，等待完成（可能需要 2-5 分钟）
# 终端会显示进度：
# [GLM-5] Sending request to API...
# [GLM-5] Response received in 68.3s

# 4. 如果仍然超时，尝试简化需求描述
# 或者分阶段创建项目（先核心功能，后扩展功能）
```

---

### 问题 2: 功能列表未生成

**症状**：初始化完成后，`feature_list.json` 不存在或为空

**诊断**：
```bash
# 检查 Initializer Agent 输出
ls -la feature_list.json

# 查看进度日志
cat claude-progress.txt

# 检查是否有错误
cat logs/initializer-*.log
```

**解决方案**：
```bash
# 1. 确认 API Key 正确配置
echo $ZHIPUAI_API_KEY

# 2. 重新运行初始化
python3 -m orchestrator.initializer_agent \
    --project . \
    --prompt "Your requirements here" \
    --template webapp

# 3. 如果仍然失败，检查 API quota
# 登录 https://open.bigmodel.cn/usercenter/apikeys
```

---

### 问题 3: 测试失败

**症状**：功能实现后测试不通过

**诊断**：
```bash
# 1. 检查开发服务器是否运行
./init.sh

# 2. 手动测试功能
# 打开浏览器访问 http://localhost:3000

# 3. 查看 test_config.json
cat .claude/test_config.json

# 4. 查看测试日志
cat logs/e2e-test-*.log
cat logs/coding-agent-*.log
```

**解决方案**：
```bash
# 1. 重启开发服务器
pkill -f "npm run dev"
./init.sh

# 2. 清理缓存重新测试
rm -rf .next node_modules/.cache
npm install

# 3. 手动验证功能步骤
# 根据 feature_list.json 中的 e2e_steps 逐一验证

# 4. 如果功能正常但测试失败，可能是测试配置问题
# 检查 .claude/test_config.json
```

---

### 问题 4: Git 冲突或状态问题

**症状**：`git status` 显示冲突或未提交的更改

**诊断**：
```bash
# 查看状态
git status

# 查看最近的提交
git log --oneline -5

# 查看当前分支
git branch -a
```

**解决方案**：
```bash
# 方案 A: 轻微问题 - 直接重置
git status
git add .
git commit -m "fix: resolve merge conflicts"

# 方案 B: 严重问题 - 回退到上一个干净状态
git reset --hard HEAD

# 方案 C: 恢复到检查点
python3 -c "
from orchestrator.state_manager import StateManager
sm = StateManager('.')
checkpoints = sm.list_checkpoints()
if checkpoints:
    latest = checkpoints[-1]
    print(f'Restoring to: {latest[\"checkpoint_id\"]}')
    sm.restore_checkpoint(latest['checkpoint_id'])
else:
    print('No checkpoints found')
"

# 方案 D: 完全重新初始化（最后手段）
cd ..
rm -rf ./workspace/broken-project
# 重新运行初始化命令
```

---

### 问题 5: 依赖安装失败

**症状**：Python 包安装失败或版本冲突

**解决方案**：
```bash
# 1. 使用虚拟环境
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows

# 2. 升级 pip
pip install --upgrade pip

# 3. 重新安装依赖
pip install -r requirements.txt

# 4. 如果仍有问题，尝试逐个安装
pip install anthropic
pip install gitpython
pip install python-dotenv
pip install pydantic

# 5. 检查 Python 版本（需要 3.8+）
python3 --version
```

---

### 问题 6: 功能依赖问题

**症状**：某些功能一直处于 blocked 状态

**诊断**：
```bash
# 查看依赖关系
python3 -c "
from orchestrator.coding_agent import CodingAgent
import json

with open('feature_list.json') as f:
    data = json.load(f)

agent = CodingAgent('.')
print(agent._visualize_dependency_graph(data['features']))
"

# 查看被阻塞的功能
cat feature_list.json | jq '.features[] | select(.passes == false) | {id, priority, dependencies}'
```

**解决方案**：
```bash
# 1. 查看阻塞原因
# 输出会显示哪些依赖未满足

# 2. 手动调整依赖关系（如果确实有误）
# 编辑 feature_list.json，修正 dependencies 字段

# 3. 如果是循环依赖，需要打破循环
# 例如：功能 A 依赖 B，B 又依赖 A
# 解决：创建中间功能 C，A→C→B

# 4. 重新运行
python3 -m orchestrator.scheduler --project . --mode manual
```

---

### 问题 7: 循环依赖检测

**症状**：输出显示 "Circular dependencies detected"

**示例输出**：
```
❌ Circular dependencies detected:
   auth-login-001 → auth-session-002 → auth-login-001 → (cycle)
```

**解决方案**：
```bash
# 1. 查看 feature_list.json 中的依赖关系
cat feature_list.json | jq '.features[] | select(.id == "auth-login-001" or .id == "auth-session-002")'

# 2. 手动修复循环依赖
# 编辑 feature_list.json
# 移除或重构依赖关系

# 3. 验证修复
python3 -c "
from orchestrator.coding_agent import CodingAgent
import json

with open('feature_list.json') as f:
    data = json.load(f)

agent = CodingAgent('.')
cycles = agent._detect_circular_dependencies(data['features'])
if cycles:
    print('Still has cycles:', cycles)
else:
    print('✅ No circular dependencies')
"
```

---

## 📞 获取帮助

如果遇到未在上述列出的问题：

1. **查看日志文件**
   ```bash
   tail -100 logs/*.log
   ```

2. **运行诊断脚本**
   ```bash
   python3 test_glm5_connection.py
   ```

3. **检查系统状态**
   ```bash
   # Python 版本
   python3 --version

   # 依赖版本
   pip list | grep -E "anthropic|gitpython|pydantic"

   # Git 版本
   git --version

   # 磁盘空间
   df -h
   ```

4. **查看项目文档**
   - README.md（本文件）
   - CLAUDE.md（架构指南）
   - examples/ 目录中的示例

## 🔮 未来路线图

### Phase 1: 基础框架（当前）
- [x] Initializer Agent
- [x] Coding Agent
- [x] Scheduler
- [x] State Manager
- [ ] Claude Code API 集成
- [ ] MCP 服务器集成

### Phase 2: 多代理架构
- [ ] Testing Agent（专注 E2E 测试）
- [ ] Code Review Agent（安全 + 质量）
- [ ] Cleanup Agent（重构 + 文档）
- [ ] QA Agent（发布前验证）

### Phase 3: 高级特性
- [ ] 自我优化（监控效率，调整提示词）
- [ ] 并行功能开发（依赖无关的功能）
- [ ] 回归测试自动化
- [ ] 性能基准测试

### Phase 4: 领域扩展
- [ ] 科学计算自动化
- [ ] 金融建模代理
- [ ] 数据工程 Pipeline
- [ ] DevOps 自动化

## 📚 更多资源

---

## 📖 快速参考

### 常用命令速查

```bash
# === 环境配置 ===
# 配置 API Key
export ZHIPUAI_API_KEY=your_key_here

# 测试 API 连接
python3 test_glm5_connection.py

# 安装依赖
pip install -r requirements.txt

# === 项目初始化 ===
# 命令行方式
python3 -m orchestrator.initializer_agent \
    --project ./workspace/my-app \
    --template webapp \
    --prompt "项目需求"

# 文件方式（推荐）
cat > ./workspace/my-app/user_prompt.txt << 'EOF'
项目需求详细描述
EOF

python3 -m orchestrator.initializer_agent \
    --project ./workspace/my-app \
    --template webapp \
    --prompt "$(cat ./workspace/my-app/user_prompt.txt)"

# === 开发模式 ===
# 单功能模式（调试）
python3 -m orchestrator.scheduler --project . --mode single-feature

# 手动模式（学习）
python3 -m orchestrator.scheduler --project . --mode manual

# 自主模式（生产）
python3 -m orchestrator.scheduler --project . --mode autonomous

# === 进度查看 ===
# 功能总数
cat feature_list.json | jq '.features | length'

# 已完成功能
cat feature_list.json | jq '.features[] | select(.passes == true)'

# 完成进度
cat feature_list.json | jq '
  {
    total: .features | length,
    completed: [.features[] | select(.passes == true)] | length,
    percentage: ([.features[] | select(.passes == true)] | length / .features | length * 100)
  }
'

# 进度日志
cat claude-progress.txt

# Git 历史
git log --oneline -10

# === 测试和验证 ===
# 启动开发服务器
./init.sh

# 运行测试
npm test
# 或
pytest

# 代码检查
npm run lint
# 或
black . && isort .

# === 故障排除 ===
# 查看 API 调用进度
# 终端会显示：[GLM-5] Response received in XX.Xs

# 查看依赖关系
python3 -c "
from orchestrator.coding_agent import CodingAgent
import json
with open('feature_list.json') as f:
    data = json.load(f)
agent = CodingAgent('.')
print(agent._visualize_dependency_graph(data['features']))
"

# 恢复到检查点
python3 -c "
from orchestrator.state_manager import StateManager
sm = StateManager('.')
checkpoints = sm.list_checkpoints()
if checkpoints:
    sm.restore_checkpoint(checkpoints[-1]['checkpoint_id'])
"
```

### 文件结构速查

```
项目根目录/
├── feature_list.json          # 功能列表（核心）
├── claude-progress.txt        # 进度日志
├── init.sh                    # 开发服务器启动脚本
├── .claude/
│   ├── test_config.json       # 测试配置
│   ├── state.json             # 系统状态
│   └── checkpoints/           # 检查点目录
├── src/                       # 源代码
├── tests/                     # 测试代码
├── screenshots/               # 视觉测试截图
│   ├── baseline/              # 基准截图
│   ├── actual/                # 实际截图
│   └── diff/                  # 差异截图
└── logs/                      # 日志文件
```

### 优先级顺序

```
critical → high → medium → low

实现顺序：
1. 先实现所有 critical 功能（核心功能）
2. 再实现 high 功能（重要功能）
3. 然后实现 medium 功能（常规功能）
4. 最后实现 low 功能（增强功能）
```

### 状态标记

- `passes: false` - 待实现
- `passes: true` - 已完成并测试通过
- `dependencies: [...]` - 依赖的功能 ID 列表

### 项目模板对比

| 模板 | 适用场景 | 默认技术栈 | init.sh 行为 |
|------|---------|-----------|-------------|
| `webapp` | Web 应用 | Next.js, React, Vue | `npm run dev` |
| `api` | API 服务 | FastAPI, Express | `uvicorn main:app` |
| `library` | 工具库 | Python, npm 包 | `pytest --watch` |

---

## 🚀 最近优化 (2025-02-16)

基于 Gemini Pro 3 的建议，实施了完整的优化方案：

### ✅ P0 优化（关键）

1. **增强 init.sh 生成** - 自动脚手架、预检查、详细错误消息
2. **环境完整性验证器** - 防止"空城计"，检测占位符，验证实际代码
3. **智能规则优化** - 从 1/10 提升到 7-8/10 质量

### ✅ P1 优化（高优先级）

1. **深度逻辑推理** - `logical_requirements` 字段，包含数据流、错误处理、禁止模式
2. **LLM-as-a-Judge 质量审计器** - 5 维度评分（1-10），严厉但公正
3. **三重验证系统** - E2E + 质量审计 + 环境验证

### ✅ P2 优化（低优先级）

1. **技能库系统** - 8 个预定义技能（API、认证、状态管理、测试等）
2. **反向测试系统** - 10 个默认测试（空输入、注入、超时、边界值）

**Git 提交**:
- `0576df2` feat: implement P2 optimizations - skills library & reverse testing
- `cbc5578` feat: implement P1 optimizations - logical depth & quality audit
- `f607100` feat: implement Gemini Pro 3 optimization recommendations (Part 1)

**效果对比**:

| 指标 | 优化前 | 优化后 |
|------|--------|--------|
| 提示词优化质量 | 1/10 | 7-9/10 |
| 功能描述深度 | 表面行为 | 深度逻辑推理 |
| 质量验证 | 仅 E2E | 三重验证 |
| 技能复用 | 无 | 8 个预定义技能 |
| 反向测试 | 无 | 10 个测试用例 |

---

## 📚 更多资源

### Anthropic 官方文档
- [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [Building Effective AI Agents](https://www.anthropic.com/research/building-effective-agents)
- [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)

### Claude Agent SDK
- [GitHub Repository](https://github.com/anthropics/claude-agent-sdk)
- [API Reference](https://docs.anthropic.com/claude-agent-sdk)
- [Examples](https://github.com/anthropics/claude-agent-sdk/tree/main/examples)

### MCP (Model Context Protocol)
- [MCP Specification](https://modelcontextprotocol.io/)
- [Puppeteer MCP Server](https://github.com/anthropics/puppeteer-mcp)
- [MCP Servers Directory](https://github.com/modelcontextprotocol)

---

**Status**: 🟢 Basic Framework Implemented
**Next Steps**:
1. Test Initializer Agent with real project
2. Integrate with Claude Code API
3. Implement Puppeteer MCP for E2E testing
4. Add Testing Agent specialization
