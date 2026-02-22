# Copilot Instructions — ufc-2026

> U Create Future 2026 | Backend: FastAPI + llama-cpp-python + DeepSeek | Frontend: Vue3 + Pinia + Vuetify + Tailwind CSS

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

### Tech stack
Vue 3 Composition API · Pinia (setup-store style) · Vuetify 3 (Material Design) · Tailwind CSS v4 · Vue Router

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

---

## Frontend Layout & Component Principles

### Fixed Aspect Ratio Container Pattern
All page-level components must use the `FixedAspectContainer` component with these specifications:
1. **统一尺寸**: All pages use fixed dimensions of `332 × 774.66px` (9:21 aspect ratio)
2. **标识ID**: The container has `id="main-display-block"` for consistent targeting
3. **视觉一致性**: All containers use `bg-white` background and `shadow-2xl` shadow
4. **溢出控制**: Content must NOT overflow outside the container. Use `overflow-y: auto` for scrollable content within the container bounds.

### Component Reusability Guidelines
1. **提取通用样式**: When similar styling appears across multiple components, extract it into a reusable component
2. **参数化配置**: Make components configurable via props (e.g., `width`, `height`, `bg-color-class`, `shadow`)
3. **统一接口**: Similar components should have consistent prop interfaces
4. **文档化原则**: Document the design decisions and constraints in this file

### Layout Architecture
```
div#app (100vw × 100vh, flex centered)
└── div#main-display-block (332 × 774.66px, fixed aspect ratio)
    ├── Header (sticky if needed)
    ├── Main content (scrollable if exceeds height)
    └── Footer (optional)
```

### Development Workflow for Layout Changes
1. **验证尺寸**: Always check that container dimensions match `332 × 774.66px`
2. **检查溢出**: Ensure content does not overflow to `div#app` (use browser devtools)
3. **测试响应性**: Verify layout works at different viewport sizes
4. **更新静态文件**: Remember to update corresponding HTML files in `/_page_*/` directories

### Browser Automation & Debugging Guidelines
When making frontend changes, use these verification steps:
1. **尺寸验证**: Use `mcp_io_github_chr_evaluate_script` to check container dimensions and overflow status
2. **样式检查**: Verify computed styles match expected values (background, shadow, etc.)
3. **导航测试**: Test page transitions and ensure consistent layout across routes
4. **实时重载**: Use browser navigation tools to see changes immediately

### Code Change Patterns
Based on our collaboration, follow these patterns:
1. **组件优先**: Create reusable components before duplicating code
2. **渐进增强**: Start with basic functionality, then add features incrementally
3. **验证驱动**: Make changes, then immediately verify with browser tools
4. **文档同步**: Update instructions when establishing new patterns

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
| [frontend/src/main.js](../frontend/src/main.js) | Plugin registration (Pinia, Router, Vuetify) |
| [frontend/src/components/FixedAspectContainer.vue](../frontend/src/components/FixedAspectContainer.vue) | Reusable fixed-size container component for all pages |
| [frontend/src/views/HomeView.vue](../frontend/src/views/HomeView.vue) | Reference implementation of page using FixedAspectContainer |
| [frontend/src/views/SettingsView.vue](../frontend/src/views/SettingsView.vue) | Settings page implementation with consistent layout |
| [frontend/src/style.css](../frontend/src/style.css) | Global styles and div#app layout configuration |
