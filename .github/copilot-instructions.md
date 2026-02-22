# Copilot Instructions — ufc-2026

> U Create Future 2026 | Backend: FastAPI + llama-cpp-python + DeepSeek | Frontend: Vue3 + Vuetify 3 + Tailwind CSS v4

## 技术栈版本信息

### 后端技术栈
- **FastAPI**: 现代Python Web框架
- **llama-cpp-python**: 本地LLM推理
- **DeepSeek**: 在线LLM API
- **Pydantic**: 数据验证和序列化

### 前端技术栈（具体版本）
- **Vue 3**: 3.5.25 (Composition API)
- **Vuetify**: 3.12.0 (Material Design 3)
- **Tailwind CSS**: v4.2.0 (最新版本)
- **Vite**: 7.3.1 (构建工具)
- **Vue Router**: 5.0.3
- **Pinia**: 3.0.4 (状态管理，当前未使用)
- **Material Design Icons**: @mdi/font 7.4.47

---

## Architecture Overview

```
ufc-2026/
├── backend/   FastAPI server — LLM inference, face recognition, navigation, smart triage
└── frontend/  Vite + Vue3 SPA — talks to backend /api/* endpoints
```

The backend exposes a single `APIRouter` at `/api` (defined in `backend/src/router/__init__.py`). Feature routers are sub-routers included into it. The frontend calls these endpoints directly; no BFF layer exists.

**Core data flows:**
1. **Smart triage** (`/api/triager/get_route_patch/`): user text → `workflow.py` → Agent pipeline (condition_collector → requirement_collector → route_patcher) → patched route JSON
2. **Face-based medical records** (`recorder/recoder.py`): LLM tool-calls → `IntegratedSystem` → `FaceRecognitionSystem` + `MedicalRecordSystem`
3. **Navigation** (`map/tools.py`): `small1.map.json` loaded at module import time; Dijkstra pathfinding, tree translation for LLM consumption

---

## Backend Conventions

### Routing pattern
Each feature gets its own `APIRouter` with a `prefix`:
```python
# router/triager.py
triager_router = APIRouter(prefix="/triager")
# mounted in router/__init__.py: api_router.include_router(triager_router)
```
Simple one-file routes go directly in `router/`. Complex multi-stage routes get a sub-folder with an `__init__.py` that defines the sub-router.

### Configuration
All constants and paths live in `backend/src/config/general.py`. Always import from there — never hardcode paths. Key globals:
- `BACKEND_ROOT_DIR` — absolute path to `backend/`
- `OFFLINE_CHAT_MODEL_PATH`, `OFFLINE_REASONING_MODEL_PATH`
- `DEFAULT_ONLINE_MODEL`, `ONLINE_MODEL_HOST` (DeepSeek API)
- `MAP_PATH` → `assets/small1.map.json`

### LLM Agent file structure
Each agent file is structured in 6 layers (see `backend/docs/llm_designing.md`):
1. Imports + file comment
2. System prompt (`instructions` variable) — sections: `## Background`, `## Role`, `## Input`, `## Output`, `## Criteria`, `## Requirements`, `## Example`
3. `logit_bias` config (via `utils.build_logit_bias`)
4. Async API functions — `*_online(...)` and `*_offline(...)` variants
5. Raw output post-processing (Pydantic model parsing)
6. `__all__` export

Online LLM uses **DeepSeek** via the OpenAI-compatible client in `llm/online/client.py`. Offline uses **llama-cpp-python** (`llm/offline/`). Every Agent exposes both variants; callers pick via `online_model: bool`.

### Pydantic everywhere
Request bodies, response data, LLM output schemas, and map structures all use Pydantic models. Typedef files (`*/typedef.py`) define shared models for a feature. Always validate LLM JSON output through a Pydantic model.

### Testing
No automated test framework. Ad-hoc scripts go in `backend/src/test/`. Run them directly with the venv active. For route testing use Postman or the browser.

### Startup behaviour
`main.py` lifecycle preloads the offline chat model on startup (`offline.get_offline_chat_model()`). Also calls `remove_os_environ_proxies()` to prevent local API calls from being intercepted by system proxies.

---

## Frontend Conventions

### Tech stack (具体版本)
- **Vue 3**: 3.5.25 (Composition API)
- **Vuetify**: 3.12.0 (Material Design 3)
- **Tailwind CSS**: v4.2.0 (最新版本)
- **Vite**: 7.3.1 (构建工具)
- **Vue Router**: 5.0.3
- **Pinia**: 3.0.4 (状态管理，当前未使用)
- **Material Design Icons**: @mdi/font 7.4.47

### 项目状态说明
- ✅ **基础架构**: 完整的前端技术栈已搭建
- ✅ **核心组件**: 完整的UI组件系统已实现
- ✅ **路由系统**: 主页 + 设置页，支持懒加载
- ✅ **语音交互**: 长按录音 + 完整视觉反馈
- ⏳ **状态管理**: Pinia stores目录为空，待实现
- ⏳ **后端集成**: 当前使用mock数据，需要连接后端API
- ⏳ **语音功能**: 语音识别和合成待集成

### Store pattern — setup-store style
```js
// src/stores/counter.js
export const useCounterStore = defineStore('counter', () => {
  const count = ref(0)
  const doubleCount = computed(() => count.value * 2)
  function increment() { count.value++ }
  return { count, doubleCount, increment }
})
```

### Component structure
- `src/views/` — page-level components (mapped from router)
- `src/components/` — reusable components
- `src/stores/` — Pinia stores
- `src/router/index.js` — route definitions; use lazy-load (`() => import(...)`) for all non-home views

### Styling approach
Use **Vuetify components** (`v-btn`, `v-card`, etc.) for structure and interactions. Use **Tailwind utility classes** for spacing, typography, layout that falls outside Vuetify. Do not mix custom CSS where utilities suffice.

### UI Design Documentation
For comprehensive UI design guidelines, refer to:
- **[ui_design_aesthetics.md](../frontend/docs/ui_design_aesthetics.md)** - 完整的UI设计系统，包含视觉规范和技术栈详情
- **[ui_design_principles.md](../frontend/docs/ui_design_principles.md)** - 核心设计原则和开发指南

#### 文档状态（2026年2月22日更新）
- ✅ **版本**: 1.1.0（基于实际代码分析更新）
- ✅ **技术栈**: 更新为实际使用的版本信息
- ✅ **组件规范**: 反映实际实现的四层消息气泡架构
- ✅ **交互细节**: 更新长按阈值为实际使用的250ms
- ✅ **尺寸说明**: 区分默认尺寸和规划尺寸
- ✅ **项目状态**: 添加详细的完成状态和待完善功能

这些文档涵盖色彩系统、排版、间距、组件规范、交互模式以及实际项目状态。

---

## Frontend Layout & Component Principles

### Fixed Aspect Ratio Container Pattern
All page-level components must use the `FixedAspectContainer` component with these specifications:

#### 尺寸规范
1. **规划尺寸**: `332 × 774.66px` (9:21 aspect ratio) - 设计规范中的目标尺寸
2. **默认尺寸**: `300 × 600px` - 组件实际默认值
3. **当前状态**: `HomeView` 和 `SettingsView` 使用默认尺寸，静态HTML文件使用规划尺寸

#### 实现规范
1. **标识ID**: 容器必须设置 `id="main-display-block"` 用于样式和脚本定位
2. **视觉一致性**: 所有容器使用 `bg-white` 背景和 `shadow-2xl` 阴影
3. **溢出控制**: 内容不能溢出容器外部，使用 `overflow-y: auto` 实现内部滚动
4. **响应式适配**: 通过 `useViewportOverflow` composable 自动检测和适配视口溢出

#### 使用示例
```vue
<!-- 使用默认尺寸（300×600px） -->
<FixedAspectContainer
  bg-color-class="bg-white"
  extra-class="font-display"
  :shadow="true"
>
  <!-- 页面内容 -->
</FixedAspectContainer>

<!-- 使用规划尺寸（332×774.66px） -->
<FixedAspectContainer
  :width="332"
  :height="774.66"
  bg-color-class="bg-white"
  extra-class="font-display"
  :shadow="true"
>
  <!-- 页面内容 -->
</FixedAspectContainer>
```

### Component Reusability Guidelines
1. **提取通用样式**: When similar styling appears across multiple components, extract it into a reusable component
2. **参数化配置**: Make components configurable via props (e.g., `width`, `height`, `bg-color-class`, `shadow`)
3. **统一接口**: Similar components should have consistent prop interfaces
4. **文档化原则**: Document the design decisions and constraints in this file

### Layout Architecture
```
div#app (100vw × 100vh, flex centered)
└── div#main-display-block (300 × 600px 默认 / 332 × 774.66px 规划, fixed aspect ratio)
    ├── Header (sticky if needed)
    ├── Main content (scrollable if exceeds height)
    └── Footer (optional)
```

#### 布局说明
1. **#app容器**: 100%视口，flex居中布局，通过 `useViewportOverflow` 智能适配
2. **主显示块**: 固定尺寸容器，当前使用默认300×600px
3. **内部结构**: 头部（固定）+ 主内容（滚动）+ 底部（固定）
4. **响应式处理**: 内容超出时自动切换为顶部对齐，确保内容可见

### Development Workflow for Layout Changes
1. **验证尺寸**: 检查容器尺寸是否符合预期（默认300×600px或规划332×774.66px）
2. **检查溢出**: 确保内容不溢出到 `div#app`（使用浏览器开发者工具）
3. **测试响应性**: 验证布局在不同视口尺寸下的表现
4. **更新静态文件**: 更新 `/_page_*/` 目录中的对应HTML文件（使用规划尺寸）
5. **测试Composables**: 验证 `useViewportOverflow` 是否正确处理视口溢出
6. **检查交互**: 测试长按交互（250ms阈值）和视觉反馈

### Browser Automation & Debugging Guidelines
When making frontend changes, use these verification steps:
1. **尺寸验证**: Use `mcp_io_github_chr_evaluate_script` to check container dimensions and overflow status
2. **样式检查**: Verify computed styles match expected values (background, shadow, etc.)
3. **导航测试**: Test page transitions and ensure consistent layout across routes
4. **实时重载**: Use browser navigation tools to see changes immediately

### Code Change Patterns
Based on our collaboration, follow these patterns:
1. **组件优先**: 创建可复用组件，避免代码重复
2. **渐进增强**: 从基础功能开始，逐步添加特性
3. **验证驱动**: 修改后立即使用浏览器工具验证
4. **文档同步**: 建立新模式时更新文档
5. **尺寸一致**: 保持FixedAspectContainer尺寸一致性
6. **交互优化**: 确保长按交互（250ms）和视觉反馈正常工作
7. **状态管理**: 为未来Pinia集成预留接口

#### 实际开发模式
- **Composables模式**: 使用 `useLongPress` 和 `useViewportOverflow` 封装复杂逻辑
- **四层组件架构**: MessageBubble → BasicMessageBubble → Assistant/UserMessageBubble
- **自定义阴影系统**: 使用自定义阴影值增强Material Design 3效果
- **响应式适配**: 通过composables智能处理布局适配

---

## Developer Workflows

### Backend setup (Ubuntu 24.04 / Python 3.10)
```bash
cd backend
python -m venv ./venv && source ./venv/bin/activate
# CPU inference (recommended):
CMAKE_ARGS="-DGGML_BLAS=ON -DGGML_BLAS_VENDOR=OpenBLAS" pip install -r requirements.txt --timeout 300
```
Copy `.env.example` → `.env` and set `DEEPSEEK_API_KEY` for online models.

Run the server:
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
# or: bash start_offline_chat_server.sh
```

### Frontend setup
```bash
cd frontend
npm install
npm run dev      # http://localhost:5173
npm run build
```

---

## Key Files to Read First
| File | Why |
|---|---|
| [backend/docs/backend_designing.md](../backend/docs/backend_designing.md) | Routing patterns, config philosophy, overall file layout rules |
| [backend/docs/llm_designing.md](../backend/docs/llm_designing.md) | Agent authoring standard, prompt structure, online/offline pattern |
| [backend/src/config/general.py](../backend/src/config/general.py) | All path/model constants |
| [backend/src/smart_triager/triager/workflow.py](../backend/src/smart_triager/triager/workflow.py) | Reference implementation of a multi-agent workflow |
| [backend/src/router/triager.py](../backend/src/router/triager.py) | Reference implementation of a feature router |
| [frontend/src/main.js](../frontend/src/main.js) | 应用入口，插件注册（Pinia, Router, Vuetify） |
| [frontend/src/components/FixedAspectContainer.vue](../frontend/src/components/FixedAspectContainer.vue) | 固定尺寸页面容器组件，所有页面必须使用 |
| [frontend/src/views/HomeView.vue](../frontend/src/views/HomeView.vue) | 主页实现，包含语音交互和消息对话 |
| [frontend/src/views/SettingsView.vue](../frontend/src/views/SettingsView.vue) | 设置页面实现，包含完整设置组件 |
| [frontend/src/style.css](../frontend/src/style.css) | 全局样式和div#app布局配置 |
| [frontend/src/router/index.js](../frontend/src/router/index.js) | 路由配置，主页+设置页懒加载 |
| [frontend/src/composables/useLongPress.js](../frontend/src/composables/useLongPress.js) | 长按交互逻辑封装，250ms阈值 |
| [frontend/src/composables/useViewportOverflow.js](../frontend/src/composables/useViewportOverflow.js) | 视口溢出检测和智能适配 |
| [frontend/src/components/AppBottomNav.vue](../frontend/src/components/AppBottomNav.vue) | 底部导航栏+FAB麦克风按钮 |
| [frontend/src/components/message-bubbles/](../frontend/src/components/message-bubbles/) | 四层消息气泡组件架构 |
| [frontend/src/components/settings/](../frontend/src/components/settings/) | 设置页面专用组件库 |
| [frontend/docs/ui_design_aesthetics.md](../frontend/docs/ui_design_aesthetics.md) | 完整的UI设计系统文档（版本1.1.0） |
| [frontend/docs/ui_design_principles.md](../frontend/docs/ui_design_principles.md) | 核心设计原则和开发指南（版本1.1.0） |

### 前端架构关键点
1. **固定尺寸容器模式**: 所有页面使用 `FixedAspectContainer`，默认300×600px，规划332×774.66px
2. **Composables模式**: `useLongPress`（250ms长按）和 `useViewportOverflow`（视口适配）
3. **四层组件架构**: MessageBubble → BasicMessageBubble → Assistant/UserMessageBubble
4. **自定义阴影系统**: 增强Material Design 3效果，区分交互状态
5. **响应式适配**: 智能检测内容溢出，自动调整布局对齐方式
