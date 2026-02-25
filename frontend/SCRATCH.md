# UFC-2026 Frontend Codebase Analysis

## 🚀 Project Status Overview (Last Updated: 2026-02-26)

### Current Implementation Status:
- **✅ Core UI/UX Framework**: Complete with fixed-aspect container system, Material Design 3, and custom shadow system
- **✅ Four-State Workflow System**: Fully implemented with 7-state Pinia store (`idle` → `collecting_conditions` → `selecting_clinic` → `collecting_requirements` → `patching_route` → `completed` → `error`)
- **✅ API Service Layer**: Complete HTTP client with error handling for all smart triage endpoints
- **✅ NavigationView Integration**: Workflow system fully integrated with voice-only interaction interface
- **🔄 Backend Connectivity**: API client ready but requires running backend server for end-to-end testing
- **🔄 Voice Integration Framework**: UI complete with 250ms long-press FAB, but STT/TTS API integration pending
- **⏳ MedicalView Adaptation**: Navigation workflow complete, medical consultation page needs similar integration
- **⏳ Testing & Validation**: Manual testing guide available, automated tests not yet implemented

### Key Technical Achievements:
1. **Voice-First Design**: Pure voice interaction with no text input dependencies
2. **Type-Safe Data Flow**: JSDoc type definitions matching backend Pydantic models
3. **Route Processing Pipeline**: Four-stage path generation and modification system
4. **Error Recovery**: Voice command "重新开始" to restart workflow from any state
5. **Environment Configuration**: `.env`-based API endpoint management

### Next Priority Tasks:
1. Test workflow system with running backend server
2. Integrate voice recognition with `/api/voice/stt` endpoint
3. Connect text-to-speech with `/api/voice/tts` endpoint
4. Adapt workflow system for MedicalView.vue
5. Implement WebSocket for real-time voice streaming

## 2. Application Scenario & Problem Statement

**Application**: UFC-2026 Frontend - Hospital Intelligent Assistant System

**Primary Users**: Hospital patients, visitors, and potentially medical staff

**Core Problem Solved**: This application provides an intelligent hospital navigation and medical consultation system that helps users:
- Navigate through hospital facilities using voice interaction
- Access medical information and preliminary consultation
- Use facial recognition for login/authentication
- Interact with AI assistants for both navigation and medical guidance

**User Journey**:
1. **Login Page** (`HomeView.vue`): Facial recognition login with camera access
2. **Navigation Assistant** (`NavigationView.vue`): Hospital wayfinding and route guidance
3. **Medical Assistant** (`MedicalView.vue`): Medical consultation and health advice
4. **Settings** (`SettingsView.vue`): App configuration and preferences

## 3. Features & Functionalities

### Core Features:
1. **Four-State Workflow System**:
   - **Hospital Navigation Workflow**: `collecting_conditions` → `selecting_clinic` → `collecting_requirements` → `patching_route`
   - **Automatic State Transitions**: Symptom analysis → Clinic selection → Requirement collection → Route optimization
   - **Voice-First Interaction**: Pure voice interface with no text input dependencies
   - **Route Processing Pipeline**: Four-stage route processing: 1) Base path (`entrance → registration_center → <xxx_clinic> → pharmacy → exit`) 2) Original route generation (replace clinic placeholder) 3) Patch application (apply requirement-based modifications) 4) Route validation (continuity checking)
   - **Error Recovery**: Voice command "重新开始" to restart workflow from any state

2. **Voice Interaction System**:
   - Long-press (250ms) FAB button for voice input
   - Visual feedback with `VoiceOverlay` and `ListeningIndicator`
   - Custom audio waveform animations and pulse rings

3. **Conversation Interface**:
   - Four-layer message bubble architecture
   - Assistant vs. User message differentiation
   - Scrollable conversation history
   - Mock conversation data for both navigation and medical modes

3. **Facial Recognition Login**:
   - Camera access via `useCamera` composable
   - Animated scanning effects with chaos motion animations
   - Tech-themed visual design with decorative elements

4. **Navigation System**:
   - Intelligent wayfinding assistant
   - Route guidance and directions
   - Hospital-specific navigation

5. **Medical Consultation**:
   - AI-powered medical advice
   - Symptom analysis and preliminary guidance
   - Medical disclaimer integration

6. **Settings Management**:
   - Voice wakeup toggle
   - Continuous conversation mode
   - Volume and speech rate controls
   - Privacy policy and about sections

### UI/UX Features:
- Fixed aspect ratio container system (300×600px default, 332×774.66px planned)
- Responsive overflow detection with `useViewportOverflow`
- Material Design 3 with custom shadows and animations
- Custom color system with primary color `#4252b3`
- Inter font family with consistent typography scale

## 4. Architecture & Design Patterns

### Component Architecture:
1. **Four-Layer Message Bubble System**:
   - `MessageBubble` (Router): Routes based on `name` prop (`'assistant'`/`'user'`)
   - `BasicMessageBubble` (Generic): Core implementation with `isAssistant` prop
   - `AssistantMessageBubble`: Left-aligned, blue-themed assistant messages
   - `UserMessageBubble`: Right-aligned, gray-themed user messages (independent implementation)

2. **Layout Architecture**:
   - `FixedAspectContainer`: Root container for all pages with fixed dimensions
   - `AppTopBar`: Dynamic title based on current route
   - `AppBottomNav`: Bottom navigation with FAB microphone button
   - `ConversationList`: Scrollable message container

3. **Composables Pattern**:
   - `useLongPress(250)`: Handles 250ms long-press logic for voice input
   - `useViewportOverflow()`: Detects content overflow and adjusts layout
   - `useCamera()`: Manages camera access and video streaming

### Routing Structure:
- `/` → `HomeView` (Facial recognition login)
- `/nav_page` → `NavigationView` (Navigation assistant)
- `/doctor_page` → `MedicalView` (Medical assistant)
- `/settings` → `SettingsView` (App settings)
- `/chat` → Redirects to `/nav_page`

### State Management:
- **Pinia Workflow System**: Complete 7-state state machine (`idle` → `collecting_conditions` → `selecting_clinic` → `collecting_requirements` → `patching_route` → `completed` → `error`)
- **Centralized State Management**: `useWorkflowStore()` in `/src/stores/workflow.js` with computed properties for all states
- **API Service Layer**: `useApiStore()` in `/src/stores/api.js` for backend communication with standardized error handling
- **Dynamic Message Management**: Workflow-driven conversation history replacing hardcoded data
- **Type-Safe Data Flow**: JSDoc type definitions matching backend Pydantic models in `/src/types/workflow.js`

## 5. Technology Stack

### Core Technologies:
- **Vue 3.5.25** (Composition API)
- **Vuetify 3.12.0** (Material Design 3)
- **Tailwind CSS v4.2.0** (Latest version)
- **Vite 7.3.1** (Build tool)
- **Vue Router 5.0.3**
- **Pinia 3.0.4** (Implemented with workflow state management stores)

### Development Tools:
- **Material Design Icons** (`@mdi/font 7.4.47`)
- **Vite plugins**: Vue, Vuetify, Tailwind CSS
- **Alias configuration**: `@` points to `./src`

### Design System:
- **Primary Color**: `#4252b3` (Deep blue)
- **Background**: `#f6f6f8` (Light gray)
- **Font**: Inter (sans-serif)
- **Spacing**: 4px base unit system
- **Shadows**: Custom values for enhanced Material Design 3 effects
- **Border Radius**: Consistent scale (4px, 8px, 16px, full)

## 6. Backend Integration

### Current State:
- **✅ Workflow System Implementation**: Complete four-state workflow with API service layer (`/src/stores/api.js`)
- **✅ State Management**: Pinia workflow store with 7-state machine and automatic transitions
- **✅ Environment Configuration**: `.env` and `.env.development` with `VITE_API_BASE_URL=http://localhost:8000/api`
- **🔄 Voice Interaction Framework**: UI ready with long-press (250ms) FAB button, but actual STT/TTS API integration pending
- **🔄 Backend API Integration**: API client implemented but untested with running backend server
- **⏳ Real-time Communication**: WebSocket for voice streaming not yet implemented
- **⏳ Authentication**: JWT token management for secure API calls pending

### Expected Integration Points (based on documentation):
1. **Smart Triage API**: `/api/triager/get_route_patch/` for navigation
2. **Face Recognition API**: Medical records and authentication
3. **Voice Interaction API**: Speech-to-text and text-to-speech
4. **Navigation API**: Map data and pathfinding

### Smart Triage API 接口详情（基于 `backend/src/router/triager.py`）：

后端智能分诊系统提供了以下 RESTful API 端点，所有端点均以 `/api/triager/` 为前缀：

#### 1. `POST /get_route_patch/` - 获取路线修改方案
**功能**：根据用户输入的需求，生成对原路线的修改方案（集成多步工作流）。
**请求体**：
```json
{
  "user_input": "字符串，用户需求描述",
  "origin_route": [
    {"this": "起点位置ID", "next": "下一位置ID"},
    ...
  ],
  "online_model": true
}
```
**响应**：
- 成功：`{"success": true, "data": "修改后的路线JSON"}`
- 失败：`{"success": false, "error": "错误信息"}`

#### 2. `POST /collect_conditions/` - 收集症状信息
**功能**：从用户输入的病症描述中提取结构化症状信息。
**请求体**：
```json
{
  "user_input": "字符串，病症描述",
  "online_model": true
}
```
**响应**：
- 成功：`{"success": true, "data": {症状结构化数据}}`
- 失败：`{"success": false, "error": "错误信息"}`

#### 3. `POST /select_clinic/` - 选择诊室
**功能**：根据结构化症状信息推荐合适的诊室。
**请求体**：
```json
{
  "conditions": {症状结构化数据对象},
  "online_model": true
}
```
**响应**：
- 成功：`{"success": true, "data": {"clinic_selection": "诊室ID"}}`
- 失败：`{"success": false, "error": "错误信息"}`

#### 4. `POST /collect_requirement/` - 收集个性化需求
**功能**：从用户输入中提取个性化需求（如偏好、限制条件等）。
**请求体**：
```json
{
  "user_input": "字符串，需求描述",
  "online_model": true
}
```
**响应**：
- 成功：`{"success": true, "data": [需求对象列表]}`
- 失败：`{"success": false, "error": "错误信息"}`

#### 5. `POST /patch_route/` - 修改路线
**功能**：根据目的地诊室和需求摘要修改原路线。
**请求体**：
```json
{
  "destination_clinic_id": "字符串，目的地诊室ID",
  "requirement_summary": [
    {需求对象1},
    {需求对象2}
  ],
  "origin_route": [
    {"this": "起点位置ID", "next": "下一位置ID"},
    ...
  ],
  "online_model": true
}
```
**响应**：
- 成功：`{"success": true, "data": {修改后的路线数据}}`
- 失败：`{"success": false, "error": "错误信息"}`

#### 6. `POST /parse_commands/` - 解析小车移动指令
**功能**：将路线转换为小车可执行的移动指令序列。
**请求体**：
```json
{
  "origin_route": [
    {"this": "起点位置ID", "next": "下一位置ID"},
    ...
  ]
}
```
**响应**：
- 成功：`{"success": true, "data": {指令序列}}`
- 失败：`{"success": false, "error": "错误信息"}`

#### 公共数据结构：
- `LocationLink`：`{"this": "位置ID", "next": "下一位置ID"}`
- `ConditionCollectorOutput`：症状结构化数据（由 `collect_conditions` 生成）
- `Requirement`：需求对象（由 `collect_requirement` 生成）
- `online_model` 参数：`true` 使用在线 LLM（DeepSeek），`false` 使用离线 LLM

### Voice Interaction API 接口详情（基于 `backend/src/router/voice.py`）：

后端语音交互系统提供了以下 RESTful API 端点，所有端点均以 `/api/voice/` 为前缀：

#### 1. `POST /stt` - 语音转文本（Speech-to-Text）
**功能**：将上传的音频文件转换为文本。
**请求**：`multipart/form-data` 表单，包含 `file` 字段（WAV 音频文件）。
**响应**：
- 成功：`{"text": "识别出的文本内容"}`（JSON 格式）
- 失败：可能返回 500 错误或识别失败

**使用示例**：
```bash
curl -X POST -F "file=@audio.wav" http://localhost:8000/api/voice/stt
```

#### 2. `GET /tts` - 文本转语音（Text-to-Speech）
**功能**：将文本转换为语音音频文件。
**请求参数**：`text` 查询参数（要转换的文本内容）。
**响应**：直接返回 `audio/wav` 格式的音频文件流，文件名为 `output.wav`。

**使用示例**：
```bash
curl -X GET "http://localhost:8000/api/voice/tts?text=你好，我是智能助手" --output speech.wav
```

#### 技术实现说明：
- **STT 流程**：接收 WAV 文件 → 保存到 `./assets/input.wav` → 调用 `VoiceInteraction().stt_async()` → 返回识别文本
- **TTS 流程**：接收文本 → 调用 `VoiceInteraction().tts_async(text)` → 生成 WAV 文件 → 返回音频文件流
- **音频格式**：WAV 格式，适用于 Web Audio API 播放

### API Patterns Needed:
- Fetch/Axios integration for HTTP requests
- WebSocket for real-time voice streaming
- Environment variables for API endpoints
- Error handling and loading states

## 8. UI/UX Patterns & Design System

### Key Design Patterns:
1. **Fixed Aspect Container Pattern**:
   - All pages use `FixedAspectContainer` for consistent sizing
   - Default: 300×600px, Planned: 332×774.66px (9:21 aspect ratio)
   - Centered in viewport with overflow detection

2. **Voice Interaction Pattern**:
   - 250ms long-press threshold (prevents accidental activation)
   - Multi-layer visual feedback (FAB styling, overlay, indicators)
   - Smooth fade transitions (0.25s)

3. **Message Bubble Pattern**:
   - Clear role differentiation (left/right alignment, color coding)
   - 80% maximum width constraint
   - Consistent spacing and typography
   - Icon-based sender identification

4. **Responsive Overflow Pattern**:
   - Smart detection of content exceeding viewport
   - Dynamic switching between centered and top-aligned layouts
   - Hidden scrollbars with maintained functionality

### Animation System:
- **CSS Transitions**: 150ms (fast), 300ms (medium), 500ms (slow)
- **Custom Keyframes**: Pulse rings, audio waves, chaos motion
- **Performance Optimized**: `will-change`, `backface-visibility`
- **Hardware Accelerated**: Transform and opacity transitions

### Accessibility Features:
- Semantic HTML structure
- Keyboard navigation support
- Sufficient color contrast (≥4.5:1)
- Screen reader compatibility
- Reduced motion considerations

## 9. Code Quality & Structure

### Strengths:
1. **Modular Architecture**: Clear separation of concerns
2. **Composable Design**: Reusable logic in composables
3. **Consistent Styling**: Tailwind-first approach with design system
4. **Comprehensive Documentation**: Detailed design principles and solved issues
5. **Type Safety**: Prop validation and TypeScript-like patterns

### Areas for Improvement:
1. **Backend API Connectivity**: API service layer implemented but needs actual backend connection and testing
2. **Voice Recognition Integration**: UI ready but needs STT API integration with `/api/voice/stt` endpoint
3. **Speech Synthesis Integration**: TTS API endpoints defined but not connected to `/api/voice/tts`
4. **Testing Infrastructure**: Still no unit or integration tests (TEST_WORKFLOW.md guide added)
5. **MedicalView Integration**: Medical consultation page still needs workflow system adaptation
6. **Real-time Voice Streaming**: WebSocket implementation for continuous voice interaction pending
7. **Authentication System**: JWT token management not yet implemented
8. **Type Safety Enhancement**: JSDoc comments added but no TypeScript compilation

### File Structure:
```
frontend/
├── src/
│   ├── components/
│   │   ├── message-bubbles/     # Four-layer message system
│   │   ├── settings/            # Settings page components
│   │   └── *.vue               # Layout and UI components
│   ├── composables/            # Reusable logic (useLongPress, useViewportOverflow, etc.)
│   ├── stores/                 # Pinia stores for state management
│   │   ├── index.js           # Pinia store registration
│   │   ├── workflow.js        # 7-state workflow state machine
│   │   └── api.js             # API service layer with error handling
│   ├── types/                  # JSDoc type definitions
│   │   └── workflow.js        # Type definitions matching backend Pydantic models
│   ├── utils/                  # Utility functions
│   │   └── route.js           # Route generation and modification utilities
│   ├── views/                  # Page components (NavigationView.vue integrated with workflow)
│   ├── router/                 # Vue Router configuration
│   └── style.css              # Global styles
├── docs/                       # Design documentation
├── .env.development           # Development environment variables
├── .env                       # Production environment variables
└── vite.config.js             # Build configuration
```

## 10. Development Status & Next Steps

### ✅ Completed:
- Core UI/UX implementation
- Voice interaction interface
- Message system architecture
- Routing and navigation
- Settings page
- Design system documentation
- **Four-State Workflow System Implementation**:
  - Complete state machine (`idle` → `collecting_conditions` → `selecting_clinic` → `collecting_requirements` → `patching_route` → `completed` → `error`)
  - Pinia stores for workflow state management (`/src/stores/workflow.js`)
  - API service layer for backend integration (`/src/stores/api.js`)
  - Type definitions matching backend Pydantic models (`/src/types/workflow.js`)
  - Route utility functions for path generation and modification (`/src/utils/route.js`)
  - Environment configuration (`.env`, `.env.development`)
  - Pure voice interaction interface (no text input boxes)
  - Integration with existing `NavigationView.vue`

### 🔄 In Progress:
- **Voice Recognition Integration**: Connecting the workflow system to actual speech-to-text API
- **Workflow System Testing**: End-to-end testing with backend API integration
- **MedicalView Integration**: Applying the same workflow pattern to the medical consultation assistant
- **Error Handling Refinement**: Improving user feedback for API failures and network errors

### ⏳ Pending Integration:
1. **Voice Recognition API**: Integrate speech-to-text with backend `/api/voice/stt` endpoint
2. **Speech Synthesis API**: Connect text-to-speech with backend `/api/voice/tts` endpoint
3. **Actual Backend Connectivity**: Test workflow system with running backend server
4. **Real-time Voice Streaming**: WebSocket implementation for continuous voice interaction
5. **Authentication System**: JWT token management for secure API calls
6. **Cross-view State Synchronization**: Share workflow state between NavigationView and MedicalView
7. **Offline Mode Support**: Mock API responses for development without backend

### Technical Debt (Partially Addressed):
- ✅ **Environment Configuration**: Added `.env` and `.env.development` files with API endpoint configuration
- ✅ **API Service Abstraction**: Created comprehensive API service layer in `/src/stores/api.js` with standardized error handling
- ✅ **Error Handling Framework**: Implemented standardized error handling in workflow and API stores with voice command restart capability
- 🔄 **Hardcoded Conversation Data**: Partially addressed - workflow system uses dynamic messages but initial greetings are static
- 🔄 **Limited Error Recovery**: Basic error states implemented but could be more robust with better user feedback
- ⏳ **Testing Infrastructure**: Still no unit or integration tests (but added `TEST_WORKFLOW.md` guide for manual testing)
- ⏳ **Type Safety**: JSDoc comments added but no TypeScript compilation for compile-time validation
- ⏳ **Code Duplication**: MedicalView.vue still needs workflow integration (NavigationView.vue already integrated)

## 11. Current Testing Status & Validation Methods

### Workflow System Testing Status:
- **✅ State Machine Logic**: Implemented and functioning with 7-state transitions
- **✅ Route Processing Utilities**: `generateOriginalRoute()`, `applyPatchesToRoute()`, `validateRouteContinuity()` functions tested
- **✅ Pinia Store Integration**: `useWorkflowStore()` and `useApiStore()` properly integrated in NavigationView.vue
- **🔄 API Connectivity**: API service layer ready but requires running backend server for end-to-end testing
- **⏳ Voice Integration**: STT/TTS API endpoints defined but not connected to actual speech recognition

### Manual Testing Checklist:
1. **Build Verification**: Ensure `npm run build` succeeds without errors
2. **Development Server**: Verify `npm run dev` starts on http://localhost:5173
3. **Navigation Page Access**: Access `/nav_page` and verify page loads correctly
4. **Workflow Initialization**: Verify automatic greeting message appears on page load
5. **Voice Interaction UI**: Test 250ms long-press on FAB microphone button shows `VoiceOverlay`
6. **State Transitions**: Manually test workflow progression through API mock responses
7. **Error Recovery**: Test voice command "重新开始" to restart workflow from any state

### Backend Integration Testing Requirements:
1. **Start Backend Server**: Ensure backend is running on http://localhost:8000
2. **API Endpoint Verification**: Test `/api/triager/collect_conditions/` endpoint with sample input
3. **CORS Configuration**: Verify backend allows requests from frontend origin (http://localhost:5173)
4. **Environment Variables**: Confirm `VITE_API_BASE_URL` is correctly set in `.env.development`

### Critical Paths for End-to-End Testing:
1. **Symptom Collection Flow**: Voice input → `collect_conditions` API → structured symptom data
2. **Clinic Selection Flow**: Symptom data → `select_clinic` API → `clinic_id` selection
3. **Requirement Collection Flow**: Voice input → `collect_requirement` API → structured requirements
4. **Route Optimization Flow**: Clinic ID + requirements → `patch_route` API → optimized route
5. **Error Handling Flow**: Network failure → graceful error recovery → user retry option

### Testing Tools & Documentation:
- **TEST_WORKFLOW.md**: Step-by-step guide for manual workflow testing
- **Postman/curl**: For backend API endpoint verification
- **Browser DevTools**: For network request inspection and debugging
- **Console Logging**: Workflow store includes detailed console logging for state transitions

## 12. Notable Implementation Details

### Four-State Workflow System Implementation:
- **State Machine Design**: 7-state workflow (`idle` → `collecting_conditions` → `selecting_clinic` → `collecting_requirements` → `patching_route` → `completed` → `error`)
- **Pinia Store Architecture**: Centralized state management in `/src/stores/workflow.js` with computed properties for all states
- **API Service Layer**: Dedicated HTTP client in `/src/stores/api.js` with standardized error handling and loading states
- **Pure Voice Interaction**: No text input boxes - all interaction via long-press microphone button (250ms threshold)
- **Route Processing Pipeline**:
  1. **Base Path**: `entrance → registration_center → <xxx_clinic> → pharmacy → exit`
  2. **Original Route Generation**: Replace `<xxx_clinic>` placeholder with actual `clinic_id`
  3. **Patch Application**: Apply `patches` array to modify route based on user requirements
  4. **Route Validation**: Continuity checking and error detection
- **Type Safety**: JSDoc type definitions in `/src/types/workflow.js` matching backend Pydantic models
- **Environment Configuration**: `.env` files for development and production API endpoints
- **Error Recovery**: Voice command "重新开始" to restart workflow from any state

### Custom Shadow System:
```css
/* FAB Button Shadows */
shadow-[0_8px_20px_rgba(0,0,0,0.35)]        /* Default */
hover:shadow-[0_12px_28px_rgba(0,0,0,0.45)] /* Hover */
!shadow-[0_16px_32px_rgba(0,0,0,0.55)]      /* Active */
```

### Animation Performance:
- Uses `transform` and `opacity` for GPU acceleration
- `will-change` for performance hints
- `backface-visibility: hidden` for smoother 3D transforms

### Responsive Strategy:
- Fixed container with overflow detection
- Dynamic vertical alignment based on content height
- Touch-optimized scrolling with hidden scrollbars

### Security Considerations:
- HTTPS requirement for camera access
- No sensitive data in frontend code
- Proper CORS configuration needed for backend APIs

## 13. Summary

The UFC-2026 frontend is a well-architected Vue 3 application with a strong focus on user experience and visual design. It implements a hospital intelligent assistant system with voice interaction, facial recognition login, and dual-mode assistance (navigation and medical).

**Key Strengths**:
- Modern technology stack with best practices (Vue 3.5.25, Vuetify 3.12.0, Tailwind v4.2.0)
- Comprehensive design system and documentation with detailed implementation guides
- Modular, component-based architecture with clear separation of concerns
- **Advanced Workflow System**: Four-state hospital navigation workflow with automatic state transitions
- **Voice-First Interface**: Pure voice interaction design with no text input dependencies
- **Type-Safe Data Flow**: JSDoc type definitions matching backend Pydantic models
- **Robust Error Handling**: Standardized error recovery with voice command restart capability
- Excellent visual design and animations with custom shadow systems
- Responsive and accessible UI patterns with viewport overflow detection

**Integration Requirements**:
- ✅ **State Management Implementation**: Complete Pinia workflow system with 7-state machine
- ✅ **Error Handling Framework**: Standardized error handling in API and workflow stores with voice command restart
- ✅ **Environment Configuration**: `.env` files with API endpoint configuration for development and production
- ✅ **Workflow Logic Implementation**: Complete four-state workflow with automatic transitions and route processing
- 🔄 **Backend API Connectivity**: API service layer implemented but needs actual backend connection and testing
- 🔄 **Voice Recognition Integration**: UI ready with long-press FAB but needs STT API integration (`/api/voice/stt`)
- 🔄 **Speech Synthesis Integration**: TTS API endpoints defined but not connected to `/api/voice/tts`
- 🔄 **Testing Infrastructure**: Manual testing guide (`TEST_WORKFLOW.md`) available but no automated tests
- ⏳ **MedicalView Integration**: Navigation workflow complete but medical consultation page needs adaptation
- ⏳ **Authentication System**: JWT token management not yet implemented for secure API calls
- ⏳ **Real-time Voice Streaming**: WebSocket implementation for continuous voice interaction pending

The codebase demonstrates professional frontend development practices and is well-positioned for integration with the backend services described in the project documentation.