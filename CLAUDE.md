# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

For more detailed architectural information and development conventions, see `.github/copilot-instructions.md`.

## Common Commands

### Backend Setup (Ubuntu 24.04 / Python 3.10.13)
```bash
cd backend
# Install dependencies (includes CPU-optimized llama-cpp-python with OpenBLAS)
CMAKE_ARGS="-DGGML_BLAS=ON -DGGML_BLAS_VENDOR=OpenBLAS" pip install -r requirements.txt --timeout 300

# Or use the installation script
bash install_deps.sh
```

### Backend Development
```bash
cd backend
source venv/bin/activate  # Activate virtual environment

# Run FastAPI server with auto-reload
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# Start llama.cpp server for offline chat models (separate process)
bash start_offline_chat_server.sh
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev      # Development server at http://localhost:5173
npm run build    # Production build
npm run preview  # Preview production build
```

### Environment Configuration
1. Copy `.env.example` to `.env` in the backend root
2. Set `DEEPSEEK_API_KEY` for online LLM API access
3. Other environment variables are loaded via `python-dotenv`

## Architecture Overview

### Project Structure
```
ufc-2026/
├── backend/          # FastAPI server with LLM inference, face recognition, navigation, smart triage
│   ├── src/
│   │   ├── config/          # Configuration constants (general.py)
│   │   ├── router/          # API routes (APIRouter pattern)
│   │   ├── smart_triager/   # Multi-agent workflow for route patching
│   │   ├── llm/             # Online/offline LLM clients
│   │   ├── map/             # Navigation with Dijkstra pathfinding
│   │   └── recorder/        # Face recognition and medical records
│   ├── assets/              # Static assets (maps, face images)
│   └── docs/                # Design documentation
└── frontend/         # Vue 3 SPA with Vuetify 3 and Tailwind CSS v4
    ├── src/
    │   ├── views/           # Page-level components (HomeView, SettingsView)
    │   ├── components/      # Reusable components
    │   │   ├── message-bubbles/  # Four-layer message bubble architecture
    │   │   └── settings/         # Settings page components
    │   ├── composables/     # useLongPress, useViewportOverflow
    │   ├── stores/          # Pinia stores (currently empty)
    │   └── router/          # Vue Router with lazy loading
    └── docs/                # UI design system and solved issues
```

### Backend Architecture
- **Single API Router**: All routes are mounted under `/api` via `backend/src/router/__init__.py`
- **Feature Routers**: Each feature gets its own `APIRouter` with a prefix (e.g., `triager_router = APIRouter(prefix="/triager")`)
- **Configuration Centralization**: All constants and paths in `backend/src/config/general.py` (never hardcode paths)
- **LLM Agent Pattern**: Six-layer structure defined in `backend/docs/llm_designing.md`:
  1. Imports + file comment
  2. System prompt (`instructions` variable) with sections: `## Background`, `## Role`, `## Input`, `## Output`, `## Criteria`, `## Requirements`, `## Example`
  3. `logit_bias` config (via `utils.build_logit_bias`)
  4. Async API functions - `*_online()` and `*_offline()` variants
  5. Raw output post-processing (Pydantic model parsing)
  6. `__all__` export
- **Pydantic Everywhere**: Request bodies, response data, LLM output schemas, and map structures all use Pydantic models
- **LLM Clients**: Online uses DeepSeek via OpenAI-compatible client (`llm/online/client.py`); offline uses llama-cpp-python (`llm/offline/`)

### Frontend Architecture
- **Fixed Aspect Container Pattern**: All page-level components must use `FixedAspectContainer` component
  - Default size: `300 × 600px`
  - Planned size: `332 × 774.66px` (9:21 aspect ratio)
  - Must have `id="main-display-block"` for styling and scripting
- **Four-Layer Component Architecture**: MessageBubble → BasicMessageBubble → Assistant/UserMessageBubble
- **Composables Pattern**: `useLongPress` (250ms threshold) and `useViewportOverflow` (viewport adaptation)
- **Custom Shadow System**: Enhanced Material Design 3 effects with custom shadow values
- **Responsive Adaptation**: Smart detection of content overflow with automatic layout adjustment
- **Tech Stack Versions**: Vue 3.5.25, Vuetify 3.12.0, Tailwind CSS v4.2.0, Vite 7.3.1, Vue Router 5.0.3

### Core Data Flows
1. **Smart Triage** (`/api/triager/get_route_patch/`): User text → `workflow.py` → Agent pipeline (condition_collector → requirement_collector → route_patcher) → patched route JSON
2. **Face-based Medical Records** (`recorder/recoder.py`): LLM tool-calls → `IntegratedSystem` → `FaceRecognitionSystem` + `MedicalRecordSystem`
3. **Navigation** (`map/tools.py`): `small1.map.json` loaded at module import time; Dijkstra pathfinding, tree translation for LLM consumption

## Key Files to Read First

| File | Purpose |
|------|---------|
| `backend/docs/backend_designing.md` | Routing patterns, config philosophy, overall file layout rules |
| `backend/docs/llm_designing.md` | Agent authoring standard, prompt structure, online/offline pattern |
| `backend/src/config/general.py` | All path/model constants (BACKEND_ROOT_DIR, OFFLINE_CHAT_MODEL_PATH, etc.) |
| `backend/src/smart_triager/triager/workflow.py` | Reference implementation of a multi-agent workflow |
| `backend/src/router/triager.py` | Reference implementation of a feature router |
| `frontend/docs/ui_design_aesthetics.md` | Complete UI design system (v1.1.0) with visual specifications |
| `frontend/docs/ui_design_principles.md` | Core design principles and development guidelines |
| `frontend/src/components/FixedAspectContainer.vue` | Fixed-size page container component (all pages must use) |
| `frontend/src/views/HomeView.vue` | Home page implementation with voice interaction and message dialogs |
| `frontend/src/composables/useLongPress.js` | Long-press interaction logic (250ms threshold) |
| `frontend/src/composables/useViewportOverflow.js` | Viewport overflow detection and smart adaptation |

## Development Conventions

### Backend
- **Routing**: Simple routes go directly in `router/`. Complex multi-stage routes get a sub-folder with `__init__.py` defining a sub-router.
- **Testing**: No automated test framework. Ad-hoc scripts in `backend/src/test/` (run directly with venv active). Route testing via Postman or browser.
- **Startup Behavior**: `main.py` preloads offline chat model on startup and calls `remove_os_environ_proxies()` to prevent local API calls from being intercepted by system proxies.
- **LLM Concurrency**: `llama-cpp-python` doesn't support concurrent calls on same `Llama` instance. Shared instances must be called sequentially; different model instances can run concurrently.

### Frontend
- **Component Structure**: Use Vuetify components for structure/interactions, Tailwind utilities for spacing/typography/layout.
- **Store Pattern**: Setup-store style with `defineStore` and Composition API.
- **Layout Architecture**: `div#app` (100vw × 100vh, flex centered) → `div#main-display-block` (fixed aspect ratio container).
- **Solved Issues**: Check `frontend/docs/solved_issues.md` for known problems and solutions (e.g., CSS animation vs. scrolling conflicts).

### Git Workflow
- Current branch: `feature-guide-improve`
- Main branch: `main`
- Recent changes: Smart triager refactoring, face recognition updates, voice interaction async conversion

## Important Constraints

1. **Offline LLM Context Limits**: `system prompt tokens + user input tokens + max_tokens` must not exceed `n_ctx` (Llama context window) to avoid segfault.
2. **Fixed Aspect Container**: All pages must use `FixedAspectContainer` with consistent sizing.
3. **Configuration References**: Always import paths/constants from `config/general.py`; never hardcode.
4. **Pydantic Validation**: Always validate LLM JSON output through Pydantic models.
5. **Voice Interaction**: Long-press threshold is 250ms; visual feedback must be provided during recording.

## Quick Reference

### Backend API Examples
```python
# Feature router definition
triager_router = APIRouter(prefix="/triager")

# Route with online/offline model selection
@triager_router.get("/get_route_patch")
async def get_route_patch(text: str, online_model: bool = False):
    result = await get_route_patch_workflow(text, online_model=online_model)
    if result is None:
        return JSONResponse({"success": False}, status_code=500)
    return {"success": True, "data": result}
```

### Frontend Component Example
```vue
<!-- Using FixedAspectContainer with default size -->
<FixedAspectContainer
  bg-color-class="bg-white"
  extra-class="font-display"
  :shadow="true"
>
  <!-- Page content -->
</FixedAspectContainer>

<!-- Using planned size (332×774.66px) -->
<FixedAspectContainer
  :width="332"
  :height="774.66"
  bg-color-class="bg-white"
  extra-class="font-display"
  :shadow="true"
>
  <!-- Page content -->
</FixedAspectContainer>
```