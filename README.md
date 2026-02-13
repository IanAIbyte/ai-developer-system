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

# 初始化新项目
python orchestrator/initializer_agent.py \
  --prompt "Build a clone of claude.ai" \
  --template webapp

# 启动自主开发循环
python orchestrator/scheduler.py \
  --project ./workspace/claude-ai-clone \
  --mode autonomous
```

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

## 🚨 故障排除

### 问题：功能列表未生成
```bash
# 检查 Initializer Agent 输出
ls -la feature_list.json

# 重新运行初始化
python -m orchestrator.initializer_agent \
    --project . \
    --prompt "Your requirements here" \
    --template webapp
```

### 问题：测试失败
```bash
# 检查开发服务器是否运行
./init.sh

# 手动测试功能
# 然后检查 feature_list.json 中的步骤

# 查看测试日志
cat logs/e2e-test-*.log
```

### 问题：Git 冲突
```bash
# 查看状态
git status

# 如果需要重置
git reset --hard HEAD

# 恢复到已知良好状态
python -c "
from orchestrator.state_manager import StateManager
sm = StateManager('.')
checkpoints = sm.list_checkpoints()
if checkpoints:
    sm.restore_checkpoint(checkpoints[-1]['checkpoint_id'])
"
```

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
