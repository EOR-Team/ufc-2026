# 项目技术架构与重构模板

> 本文档为前后端分离项目的通用技术架构模板，提取自 UFC-2026 实战项目。适用于新项目结构设计与重构参考。

---

## 1. 项目概述

### 1.1 项目定位

```
┌─────────────────────────────────────────────────────┐
│                   应用层（Application）                │
│         语音交互 / 视觉感知 / 智能决策 / 导航控制       │
├─────────────────────────────────────────────────────┤
│                   服务层（Service）                   │
│         状态管理 / 业务编排 / 工作流引擎 / 规则引擎    │
├─────────────────────────────────────────────────────┤
│                   协议层（Protocol）                  │
│         REST API / WebSocket / STT-TTS / HTTP       │
├─────────────────────────────────────────────────────┤
│                   模型层（Model）                     │
│       LLM推理 / 路径规划 / 视觉分割 / 人脸识别        │
├─────────────────────────────────────────────────────┤
│                   基础设施（Infrastructure）           │
│         数据库 / 缓存 / 文件存储 / 日志监控            │
└─────────────────────────────────────────────────────┘
```

### 1.2 核心功能域

| 功能域 | 描述 | 涉及层级 |
|--------|------|----------|
| **感知域** | 语音识别（STT）、视觉感知、人脸识别 | 模型层 → 协议层 |
| **认知域** | LLM 推理、意图分析、决策生成 | 模型层 |
| **执行域** | 导航控制、语音合成（TTS）、指令执行 | 服务层 → 协议层 |
| **会话域** | 多轮对话、状态管理、上下文保持 | 服务层 → 应用层 |

---

## 2. 前端架构设计（Vue 3 SPA）

### 2.1 整体目录结构

```
frontend/src/
├── views/                         # 页面级组件（路由页面）
│   ├── {Domain}View.vue          # 按业务域命名（如 HomeView, DashboardView）
│   └── {Feature}View.vue
│
├── components/                    # 可复用组件
│   ├── layout/                   # 布局组件
│   │   ├── FixedAspectContainer.vue   # 固定比例容器（核心）
│   │   ├── AppTopBar.vue
│   │   └── AppBottomNav.vue
│   │
│   ├── ui/                       # 基础 UI 组件（原子/分子）
│   │   ├── {Component}.vue       # 按职责命名（如 Button, Card, Avatar）
│   │   └── ...
│   │
│   ├── {feature}/                # 特性组件（按业务域聚合）
│   │   ├── {Feature}Panel.vue
│   │   ├── {Feature}List.vue
│   │   └── {Feature}Card.vue
│   │
│   └── {shared}/                 # 跨域共享组件
│       ├── message-bubbles/      # 四层消息气泡架构
│       │   ├── MessageBubble.vue      # 路由层（按 name 分发）
│       │   ├── BasicMessageBubble.vue  # 通用基类
│       │   ├── AssistantBubble.vue     # Assistant 包装
│       │   ├── UserBubble.vue         # User 包装
│       │   └── SkeletonBubble.vue     # 加载骨架屏
│       │
│       ├── map/                  # 地图可视化
│       └── navigation/           # 导航控制
│
├── composables/                  # 组合式函数（可复用逻辑）
│   ├── use{Feature}.js          # 按功能命名（如 useLongPress, useCamera）
│   └── ...
│
├── stores/                       # 状态管理（Pinia）
│   ├── api.js                   # HTTP 客户端封装
│   ├── workflow.js              # 状态机工作流
│   └── {domain}.js              # 按域命名的独立 store
│
├── utils/                        # 纯工具函数
│   ├── {category}.js            # 按类别（tts, streaming, route...）
│   └── ...
│
├── router/
│   └── index.js                  # Vue Router（懒加载）
│
└── styles/
    ├── tokens.css               # 设计令牌
    ├── typography.css           # 字体规范
    └── global.css               # 全局样式
```

### 2.2 前端核心架构模式

#### 模式 1：四层组件架构（消息气泡示例）

```
┌──────────────────────────────────────────────┐
│            Layer 1: Router                   │
│   MessageBubble.vue                          │
│   → 根据 name prop 分发到对应组件             │
└────────────────────┬───────────────────────┘
                     │
┌────────────────────▼───────────────────────┐
│           Layer 2: Generic Base            │
│   BasicMessageBubble.vue                   │
│   → 左对齐（Assistant）/ 右对齐（User）     │
│   → 统一背景色、圆角、间距                  │
└────────────────────┬───────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
┌────────▼────────┐    ┌─────────▼────────┐
│ Layer 3:        │    │ Layer 3:         │
│ AssistantBubble │    │ UserBubble       │
│ (icon='bot')    │    │ (灰色背景)       │
└─────────────────┘    └──────────────────┘
         │
┌────────▼──────────────────────────────────────┐
│              Layer 4: Skeleton                │
│         SkeletonMessageBubble.vue             │
│         (加载中状态)                          │
└───────────────────────────────────────────────┘
```

#### 模式 2：固定比例容器（核心布局约束）

```
┌─────────────────────────────────────┐
│         #app (100vw × 100vh)        │
│         flex centered               │
├─────────────────────────────────────┤
│      #main-display-block            │
│      ┌─────────────────────────┐     │
│      │                         │     │
│      │   FixedAspectContainer  │     │
│      │   (固定宽高比)          │     │
│      │                         │     │
│      │   - default: 300×600    │     │
│      │   - planned: 332×774.66 │     │
│      │                         │     │
│      └─────────────────────────┘     │
└─────────────────────────────────────┘
```

#### 模式 3：Composable 组合式逻辑

```
┌──────────────────────────────────────────────────┐
│                  Composables                      │
│                                                   │
│  useLongPress(250ms) → 录音触发                   │
│  ├── isActive: boolean                           │
│  ├── start(): void                               │
│  └── end(): void                                 │
│                                                   │
│  useViewportOverflow() → 内容溢出检测              │
│  ├── isOverflowing: boolean                       │
│  └── detect(): void                              │
│                                                   │
│  useCamera() → 摄像头权限                         │
│  ├── stream: MediaStream                          │
│  └── permission: 'granted'|'denied'|'prompt'    │
│                                                   │
│  useVoiceRecorder() → 音频录制                    │
│  └── start/stop: () => void                      │
└──────────────────────────────────────────────────┘
```

#### 模式 4：Pinia Store 分层

```
┌──────────────────────────────────────────────────┐
│                   Pinia Stores                    │
│                                                   │
│  api.js (HTTP Client)                            │
│  ├── request() - 基础 fetch 封装                  │
│  ├── {entity}Api - 按实体命名的 API 方法集         │
│  └── workflowApi - 工作流相关 API                 │
│                                                   │
│  workflow.js (State Machine)                      │
│  ├── states: IDLE → RUNNING → COMPLETED/ERROR    │
│  ├── context: 状态机上下文数据                     │
│  └── transitions: 状态转换方法                     │
│                                                   │
│  {domain}.js (Business Store)                     │
│  ├── state: 响应式状态                            │
│  └── actions: 业务操作方法                        │
└──────────────────────────────────────────────────┘
```

---

## 3. 后端架构设计（FastAPI）

### 3.1 整体目录结构

```
backend/src/
├── config/                          # 配置中心（集中化管理）
│   └── general.py                  # 全局常量、路径、模型配置
│
├── router/                          # API 路由层
│   ├── __init__.py                 # 主路由聚合（统一挂载点）
│   └── {feature}/                  # 按功能域拆分的子路由
│       ├── __init__.py             # 子路由定义
│       ├── {handler}.py            # 处理器函数
│       └── {handler}_router.py     # 可选：独立 router 文件
│
├── {domain}/                        # 业务领域模块（智能分诊示例）
│   ├── agent/                      # Agent 实现
│   │   ├── {sub_agent}.py         # 子 Agent（如 condition_collector）
│   │   └── workflow.py            # 工作流编排
│   │
│   ├── typedef.py                  # Pydantic 类型定义（输入/输出）
│   └── tools.py                   # 领域工具函数
│
├── llm/                            # LLM 协议层
│   ├── online/                    # 在线模型客户端（OpenAI 兼容）
│   │   └── client.py
│   └── offline/                   # 离线模型客户端（llama-cpp）
│       └── client.py
│
├── {service}/                      # 基础设施服务
│   ├── voice_interaction/          # 语音服务（STT/TTS）
│   │   ├── voice_interaction.py   # Facade 单例
│   │   ├── speech2text.py
│   │   └── text2speech.py
│   │
│   ├── vision/                    # 视觉服务
│   │   ├── segmenter.py
│   │   ├── ocr.py
│   │   └── verifier.py
│   │
│   ├── map/                       # 导航服务
│   │   ├── tools.py              # 路径算法
│   │   └── typedef.py
│   │
│   ├── user/                      # 用户服务
│   │   ├── database.py           # 数据库访问
│   │   └── typedef.py
│   │
│   └── car_control/               # 设备控制
│
├── utils/                          # 共享工具
│   ├── build_logit_bias.py        # LLM logit 调整
│   └── ...
│
└── main.py                         # 应用入口（预加载、初始化）
```

### 3.2 后端核心架构模式

#### 模式 1：API Router 聚合模式

```
┌─────────────────────────────────────────────────────────────┐
│                     API 路由架构                             │
│                                                             │
│  /api                                                       │
│  ├── /triager          → 智能分诊路由                        │
│  ├── /voice            → 语音交互路由                       │
│  ├── /navigation       → 导航控制路由                       │
│  ├── /medical          → 医疗咨询路由                       │
│  └── /user             → 用户管理路由                       │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  __init__.py (主路由聚合)                            │    │
│  │  api_router = APIRouter(prefix="/api")               │    │
│  │  api_router.include_router(triager_router)            │    │
│  │  api_router.include_router(voice_router)              │    │
│  │  ...                                                 │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

#### 模式 2：LLM Agent 6 层结构

```
┌─────────────────────────────────────────────────────────────┐
│              LLM Agent 文件标准模板                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  # Layer 1: 文件头注释                                      │
│  """                                                        │
│  {domain}/{agent}.py                                        │
│  [功能描述]                                                  │
│  """                                                        │
│                                                             │
│  # Layer 2: System Prompt (7 个标准章节)                     │
│  {agent}_instructions = """                                 │
│  ## Background   [背景上下文]                                │
│  ## Role         [角色定义]                                 │
│  ## Input        [输入格式]                                 │
│  ## Output       [输出格式]                                 │
│  ## Criteria     [评估标准]                                 │
│  ## Requirements [技术约束]                                 │
│  ## Example      [示例]                                     │
│  """                                                        │
│                                                             │
│  # Layer 3: logit_bias 配置                                 │
│  logit_bias = build_logit_bias([...])                       │
│                                                             │
│  # Layer 4: 异步 API 函数（online/offline 双版本）           │
│  async def {agent}_online(...) -> {OutputModel}:            │
│      ...                                                    │
│                                                             │
│  async def {agent}_offline(...) -> {OutputModel}:           │
│      ...                                                    │
│                                                             │
│  # Layer 5: Pydantic 模型解析（raw output → typed model）    │
│  # Layer 6: __all__ 导出                                     │
│  __all__ = ["{agent}_online", "{agent}_offline", ...]       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### 模式 3：多阶段工作流管道

```
┌─────────────────────────────────────────────────────────────┐
│                4 阶段工作流管道模式                           │
│                                                             │
│  User Input                                                │
│      │                                                     │
│      ▼                                                     │
│  ┌───────────────────┐                                    │
│  │  Stage 1          │  症状收集                           │
│  │  {Collector}      │  → 结构化症状输出                    │
│  └────────┬──────────┘                                    │
│           │                                                │
│           ▼                                                │
│  ┌───────────────────┐                                    │
│  │  Stage 2          │  科室选择                            │
│  │  {Selector}       │  → 科室 ID                          │
│  └────────┬──────────┘                                    │
│           │                                                │
│           ▼                                                │
│  ┌───────────────────┐                                    │
│  │  Stage 3          │  需求收集                            │
│  │  {Collector}      │  → 个性化需求列表                    │
│  └────────┬──────────┘                                    │
│           │                                                │
│           ▼                                                │
│  ┌───────────────────┐                                    │
│  │  Stage 4          │  路线优化                            │
│  │  {Patcher}        │  → 优化后路线                        │
│  └────────┬──────────┘                                    │
│           │                                                │
│           ▼                                                │
│  ┌───────────────────┐                                    │
│  │  Output           │  命令解析 + 执行                      │
│  │  {Parser/Runner}  │  → 可执行指令                        │
│  └───────────────────┘                                    │
│                                                             │
│  Retry Logic: 每个阶段 max 3 次重试，失败返回 None           │
└─────────────────────────────────────────────────────────────┘
```

#### 模式 4：Online/Offline 双模式 LLM 客户端

```
┌─────────────────────────────────────────────────────────────┐
│                 LLM 客户端双模式                             │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Caller                                              │   │
│  │  result = await agent_online(...)  if online_model   │   │
│  │          else await agent_offline(...)               │   │
│  └────────────────────┬────────────────────────────────┘   │
│                       │                                      │
│          ┌────────────┴────────────┐                         │
│          │                         │                         │
│          ▼                         ▼                         │
│  ┌───────────────┐       ┌───────────────┐                  │
│  │ Online Client │       │ Offline Client│                  │
│  │ (OpenAI 兼容) │       │(llama-cpp-py) │                  │
│  │               │       │               │                  │
│  │ DeepSeek API │       │ GGUF 模型     │                  │
│  │ Azure OpenAI │       │ 本地加载      │                  │
│  └───────────────┘       └───────┬───────┘                  │
│                                  │                          │
│                    ┌─────────────┼─────────────┐             │
│                    │  asyncio.to_thread     │  // 非阻塞    │
│                    │  (避免阻塞事件循环)      │             │
│                    └─────────────────────────┘             │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. API 响应格式规范

### 4.1 统一响应封装

```python
# 成功响应
JSONResponse(
    content={
        "success": True,
        "data": <PydanticModel>   # 结构化数据
    },
    status_code=200
)

# 失败响应
JSONResponse(
    content={
        "success": False,
        "error": "错误描述"
    },
    status_code=500
)

# 带分页的响应
JSONResponse(
    content={
        "success": True,
        "data": <List[PydanticModel]>,
        "pagination": {
            "total": 100,
            "page": 1,
            "limit": 20
        }
    },
    status_code=200
)
```

---

## 5. 状态机工作流设计

### 5.1 状态机模式

```
┌─────────────────────────────────────────────────────────────┐
│              Frontend Workflow State Machine                 │
│                                                             │
│     IDLE ──────────────────────────────► COMPLETED           │
│      │                                    ▲                 │
│      │                                    │                 │
│      ▼                                    │                 │
│  COLLECTING ─────────────────────► ERROR ─┘                 │
│      │                                                     │
│      ▼                                                     │
│  SELECTING                                                  │
│      │                                                     │
│      ▼                                                     │
│  COLLECTING_REQUIREMENTS                                    │
│      │                                                     │
│      ▼                                                     │
│  PATCHING ─────────────────────────────────────────────────►│
│                                                             │
│  每个状态:                                                  │
│  - entry action: 进入状态时的操作（如发送 API 请求）         │
│  - exit action: 退出状态时的操作（如保存上下文）             │
│  - transition: 状态转换条件                                  │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 状态机上下文

```javascript
// workflow.js 状态机上下文结构
{
  // 业务上下文
  conditions: [],           // 已收集的症状
  selectedClinic: null,     // 选中的科室
  requirements: [],         // 用户需求列表
  originalRoute: null,     // 原始路线
  modifiedRoute: null,      // 优化后路线

  // 导航上下文
  commands: [],            // 解析后的指令
  currentCommandIndex: 0,   // 当前执行位置
  verificationPending: false, // 等待位置验证

  // 消息上下文
  messages: [],            // 对话历史
  isPlaying: false,        // TTS 播放中
  autoAdvance: true         // TTS 完成后自动下一步
}
```

---

## 6. 重构方法论

### 6.1 重构优先级矩阵

```
        高业务价值
            ▲
            │
     P1     │    P0
  功能完善   │   核心问题
 ───────────┼───────────► 低实施难度
            │
     P2     │    P3
  架构优化   │   缓处理
            │
            ▼
        低业务价值
```

| 优先级 | 类型 | 示例 | 处置 |
|--------|------|------|------|
| **P0** | 核心问题（阻塞） | 无测试框架、严重性能瓶颈 | 立即修复 |
| **P1** | 功能完善 | 页面实现不完整、状态未连接 | 尽快完成 |
| **P2** | 架构优化 | 类型共享、模块解耦 | 规划中处理 |
| **P3** | 缓处理 | 代码美化、注释完善 | 有余力时处理 |

### 6.2 重构检查清单

#### 代码质量
```
□ 函数 < 50 行
□ 文件 < 800 行
□ 无深层嵌套（> 4 层）
□ 不可变数据模式（创建新对象 > 修改现有对象）
□ 错误显式处理（无静默吞掉）
□ 无魔法数字（使用常量）
□ 命名语义化
```

#### 安全
```
□ 无硬编码密钥（API Key、密码、Token）
□ SQL 注入防护（参数化查询）
□ XSS 防护（用户输入转义）
□ 输入验证（系统边界）
□ 认证/授权验证
□ 速率限制（Rate Limiting）
```

#### 性能
```
□ 离线模型无并发调用同一实例（使用锁或实例池）
□ 数据库查询有索引
□ 前端无不必要重渲染
□ 图片/资源有懒加载
□ 地图数据预加载/缓存
□ LLM 推理有超时控制
```

#### 可维护性
```
□ 配置集中化（禁止硬编码路径/常量）
□ Pydantic/TypeScript 类型全覆盖
□ API 文档完整（OpenAPI/Swagger）
□ 错误日志有上下文
□ 单一数据源（无重复状态）
```

### 6.3 重构工作流

```
┌─────────────────────────────────────────────────────────────┐
│                    重构工作流                                │
│                                                             │
│  1. 识别问题                                                 │
│     ├── 静态分析（ESLint, mypy, ruff）                      │
│     ├── 动态分析（性能 Profiling）                           │
│     └── 代码审查（agent 或人工）                             │
│                                                             │
│  2. 规划方案                                                 │
│     ├── 影响范围分析                                         │
│     ├── 依赖关系梳理                                         │
│     └── 实施步骤拆分                                         │
│                                                             │
│  3. 实施重构                                                 │
│     ├── TDD：先写测试                                       │
│     ├── 增量修改（小步快跑）                                 │
│     └── 每次修改后运行测试                                   │
│                                                             │
│  4. 验证与回归                                               │
│     ├── 单元测试通过                                         │
│     ├── 集成测试通过                                         │
│     ├── E2E 测试通过                                        │
│     └── 手动验证关键路径                                     │
│                                                             │
│  5. 提交与合并                                               │
│     ├── 遵循约定式提交格式                                   │
│     └── 包含测试计划                                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 7. 技术选型决策树

```
┌─────────────────────────────────────────────────────────────┐
│                   前端框架选型                               │
│                                                             │
│  需要快速开发 + Material Design + 复杂表单                    │
│      └── Vuetify 3                                         │
│                                                             │
│  需要极致性能 + 定制化设计系统                               │
│      └── Vue 3 + Tailwind CSS + Headless UI                │
│                                                             │
│  需要多页应用 + SEO 优先                                     │
│      └── Nuxt 3                                            │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                   状态管理选型                               │
│                                                             │
│  简单状态 + 小型应用                                         │
│      └── Pinia（Setup Store 风格）                          │
│                                                             │
│  复杂状态 + 需要 DevTools                                   │
│      └── Pinia + 持久化插件                                  │
│                                                             │
│  需要 RTK Query 般的能力                                     │
│      └── Pinia + TanStack Query                            │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                   后端框架选型                               │
│                                                             │
│  LLM/AI 优先 + 需要快速原型                                  │
│      └── FastAPI（类型安全 + 自动文档 + 异步优先）           │
│                                                             │
│  传统 CRUD + 团队熟悉 Django                                │
│      └── Django + DRF                                      │
│                                                             │
│  微服务 + 需要高并发                                         │
│      └── FastAPI / Flask + 异步 workers                     │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                   LLM 方案选型                              │
│                                                             │
│  需要高质量推理 + 可接受 API 成本                             │
│      └── OpenAI / DeepSeek / Anthropic                     │
│                                                             │
│  需要离线部署 + 隐私敏感                                     │
│      └── llama-cpp-python / Ollama（GGUF 模型）            │
│                                                             │
│  需要本地推理 + 性能优先                                     │
│      └── llama-cpp-python（C++ 实现 + BLAS 加速）          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 8. 架构决策记录（ADR）模板

当进行重要架构决策时，建议记录在 `docs/adr/NNNN-*.md`：

```markdown
# ADR-XXXX: [决策标题]

## 状态
[Proposed | Accepted | Deprecated | Superseded]

## 背景
[描述促使此决策的问题或上下文]

## 决策
[描述所采取的决策]

## 后果
### 正面
- ...

### 负面
- ...

### 中性
- ...

## 替代方案
[考虑过的其他方案及放弃原因]
```

---

## 9. 通用约束与红线

### 9.1 前端红线

```
🚫 禁止
├── 在组件内直接调用 axios/fetch（使用 store 或 composable 封装）
├── 在模板中使用复杂计算（使用 computed 缓存）
├── 直接修改 prop（单向数据流原则）
├── 在 v-for 中使用 index 作为 key
└── 在 async/await 中不使用 try-catch
```

### 9.2 后端红线

```
🚫 禁止
├── 在同步函数中执行长时间 IO 操作（使用 async）
├── 直接返回字典而非 Pydantic 模型
├── 在应用启动时加载大模型到内存（使用懒加载 + 单例）
├── 在生产环境输出详细错误堆栈
└── 使用字符串拼接构建 SQL
```

### 9.3 LLM 集成红线

```
🚫 禁止
├── 信任 LLM 输出的 JSON（必须通过 Pydantic 验证）
├── 超出模型上下文窗口（system + user + max_tokens ≤ n_ctx）
├── 并发调用同一 Llama 实例（使用锁或实例池）
└── 在 prompt 中泄露敏感信息
```

---

## 10. 项目启动模板

### 10.1 目录结构快速生成

```
mkdir -p frontend/src/{views,components/{ui,layout,shared},composables,stores,utils,router,styles}
mkdir -p backend/src/{config,router/{feature},domain/{agent,typedef},llm/{online,offline},service/{voice,vision,map},utils}
mkdir -p frontend/docs backend/docs
touch frontend/src/main.js backend/src/main.py
```

### 10.2 核心文件清单

| 层级 | 文件 | 说明 |
|------|------|------|
| 前端入口 | `src/main.js` | Vue 应用初始化 |
| 前端路由 | `src/router/index.js` | 路由配置 + 懒加载 |
| 状态管理 | `src/stores/api.js` | HTTP 客户端 |
| 状态管理 | `src/stores/workflow.js` | 状态机（可选） |
| 后端入口 | `src/main.py` | FastAPI 应用 + 预加载 |
| 主路由 | `src/router/__init__.py` | API 路由聚合 |
| 配置中心 | `src/config/general.py` | 常量 + 路径 |
| LLM 基础 | `src/llm/base.py` | 在线/离线客户端基类 |

---

> 本文档为通用架构模板，具体项目请根据业务需求裁剪使用。
