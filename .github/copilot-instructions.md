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
