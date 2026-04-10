# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在此代码库中工作时提供指导。

## 项目概述

**ufc-2026** 是一个智能医疗导航系统，结合大语言模型(LLM)、语音交互和人脸识别技术，为用户提供智能分诊、路线规划和医疗咨询服务。

### 核心功能

| 功能 | 描述 | 技术实现 |
|------|------|----------|
| 智能分诊 | 多智能体工作流分析症状选择诊室 | condition_collector → requirement_collector → route_patcher |
| 导航系统 | Dijkstra 路径规划 + LLM 可读的树状结构 | newest.map.json + map/tools.py |
| 语音交互 | 长按录音 → 语音转文字 → LLM → 文字转语音 | Sherpa-onnx (STT) + MeloTTS (TTS) |
| 医疗记录 | 人脸识别关联个人医疗档案 | face.jpg + recorder 模块 |
| 医疗咨询 | 基于上下文的医疗建议生成 | medical/agent.py |

## 技术架构

### 技术栈

```
后端: Python 3.10 + FastAPI + llama-cpp-python + DeepSeek API
前端: Vue 3.5 + Vuetify 3.12 + Tailwind CSS v4 + Pinia 3.0
```

### 后端架构

```
backend/
├── src/
│   ├── config/general.py      # 全局配置（路径、模型常量）
│   ├── router/                 # API 路由（统一挂载到 /api）
│   │   ├── __init__.py         # 主路由汇总
│   │   ├── triager.py          # 智能分诊
│   │   ├── medical.py          # 医疗咨询
│   │   ├── navigation.py       # 导航
│   │   ├── voice.py            # 语音
│   │   └── ...
│   ├── smart_triager/          # 多智能体分诊系统
│   │   ├── triager/            # 分诊智能体
│   │   │   ├── condition_collector.py
│   │   │   ├── requirement_collector.py
│   │   │   ├── route_patcher.py
│   │   │   ├── clinic_selector.py
│   │   │   └── workflow.py     # 核心工作流
│   │   └── car/                # 车辆相关智能体
│   ├── llm/                    # LLM 客户端
│   │   ├── online/             # DeepSeek 在线模型
│   │   └── offline/           # llama-cpp-python 离线模型
│   ├── voice_interaction/      # 语音交互
│   │   ├── speech2text.py      # Sherpa-onnx
│   │   └── text2speech.py      # MeloTTS
│   ├── map/                    # 导航模块
│   ├── medical/                # 医疗咨询智能体
│   ├── recorder/               # 人脸识别 + 医疗记录
│   ├── vision/                 # 黑盒分割、OCR
│   ├── user/                   # 用户数据库
│   └── utils.py                # 共享工具
└── assets/                     # 静态资源
    ├── face.jpg                # 人脸识别素材
    └── newest.map.json         # 导航图数据
```

**关键设计原则：**
1. **Pydantic 无处不在** - 请求、响应、LLM 输出、地图结构全部使用 Pydantic 模型验证
2. **LLM 智能体六层结构** - 导入 → 系统提示词 → logit_bias → 异步 API → 输出解析 → __all__
3. **在线/离线双模式** - 通过 `online_model: bool` 参数切换 DeepSeek / llama-cpp-python
4. **无独立 llama.cpp 服务器** - 离线模型直接加载到 FastAPI 进程内存

### 前端架构

```
frontend/src/
├── views/                      # 页面组件
│   ├── HomeView.vue            # 首页（语音 + 消息）
│   ├── SettingsView.vue         # 设置页
│   ├── MedicalView.vue          # 医疗咨询页
│   └── NavigationView.vue       # 导航页
├── components/
│   ├── FixedAspectContainer.vue # 固定比例容器（核心布局组件）
│   ├── message-bubbles/        # 四层消息气泡
│   │   ├── MessageBubble.vue    # 路由分发
│   │   ├── BasicMessageBubble.vue
│   │   ├── AssistantMessageBubble.vue
│   │   └── UserMessageBubble.vue
│   └── ...
├── composables/
│   ├── useLongPress.js         # 长按交互（250ms 阈值）
│   ├── useViewportOverflow.js  # 视口溢出检测
│   ├── useCamera.js
│   └── useVoiceRecorder.js
├── stores/
│   ├── api.js                  # API 调用
│   ├── workflow.js              # 工作流状态
│   └── index.js
└── router/index.js              # Vue Router（懒加载）
```

**关键设计原则：**
1. **固定比例容器模式** - 所有页面使用 FixedAspectContainer（默认 300×600px，规划 332×774.66px）
2. **四层组件架构** - MessageBubble → BasicMessageBubble → Assistant/UserMessageBubble
3. **Composables 模式** - useLongPress(250ms)、useViewportOverflow

## 核心数据流

```
┌─────────────────────────────────────────────────────────────────────┐
│                         智能分诊流程                                 │
├─────────────────────────────────────────────────────────────────────┤
│  用户输入 → condition_collector → select_clinic →                  │
│  requirement_collector → route_patcher → 修补后的路线 JSON          │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                         语音交互流程                                 │
├─────────────────────────────────────────────────────────────────────┤
│  长按(250ms) → 录音 → /api/voice/stt → Sherpa-onnx → 文本 →        │
│  LLM 推理 → /api/voice/tts → MeloTTS → 语音播放                    │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                         导航流程                                     │
├─────────────────────────────────────────────────────────────────────┤
│  newest.map.json (模块加载时) → Dijkstra 寻路 →                     │
│  树状结构转换 → LLM 可读的路线描述                                   │
└─────────────────────────────────────────────────────────────────────┘
```

## 必读文件

| 文件 | 用途 |
|------|------|
| `backend/docs/llm_designing.md` | LLM 智能体编写规范（六层结构、提示词模板） |
| `backend/docs/backend_designing.md` | 后端架构规范（路由、配置、文件组织） |
| `backend/src/smart_triager/triager/workflow.py` | 多智能体工作流参考实现 |
| `backend/src/config/general.py` | 所有路径/模型常量定义 |
| `frontend/docs/ui_design_aesthetics.md` | UI 设计系统（颜色、字体、间距规范） |
| `frontend/src/components/FixedAspectContainer.vue` | 固定比例容器（所有页面必须使用） |

## 常用命令

### 后端
```bash
cd backend
source venv/bin/activate
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### 前端
```bash
cd frontend
npm install
npm run dev      # 开发服务器
npm run build    # 生产构建
```

## 重要约束

1. **离线 LLM 上下文限制** - `system_tokens + user_tokens + max_tokens` 不能超过模型的 `n_ctx`，否则 segfault
2. **LLM 并发限制** - 同一 `Llama` 实例不能并发调用，需串行或使用不同实例
3. **语音长按阈值** - 250ms，需提供视觉反馈
4. **配置集中化** - 所有路径从 `config/general.py` 导入，禁止硬编码

## 模块说明

### smart_triager - 智能分诊系统

**输入**: 用户症状描述文本
**输出**: 修补后的路线 JSON

**工作流**:
1. `collect_conditions` - 从文本提取结构化症状（body_parts, duration, severity...）
2. `select_clinic` - 根据症状选择诊室
3. `collect_requirement` - 提取用户个性化需求
4. `patch_route` - 根据目的地和需求修改原路线

每个步骤支持重试（最多 3 次），失败返回 None。

### voice_interaction - 语音交互

- **STT**: Sherpa-onnx 模型，warmup 时加载
- **TTS**: MeloTTS，numpy>=2 需要手动维护
- 长按触发录音，松开发送 /api/voice/stt

### map - 导航系统

- `newest.map.json` 模块级加载（启动时读入内存）
- `find_shortest_path()` - Dijkstra 单源最短路径
- `to_tree_structure()` - 转换为 LLM 可读的嵌套树格式
