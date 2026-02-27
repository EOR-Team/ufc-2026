# 状态转移系统设计文档

## 概述

本文档详细描述 UFC-2026 医院智能导航系统中的四状态工作流状态转移系统设计。该系统实现了完整的医院导航流程，从症状收集到路线优化的全流程自动化。

## 设计目标

1. **模块化状态管理**：清晰的状态划分和转移逻辑
2. **语音优先交互**：纯语音输入驱动状态转移
3. **API驱动数据流**：前后端分离，API 调用触发状态变更
4. **错误恢复能力**：完善的状态回退和错误处理机制
5. **可复用架构**：设计模式可应用于其他多步骤交互场景

## 系统架构

### 状态定义 (7个核心状态)

```javascript
const STATE = {
  IDLE: 'idle',                     // 初始状态，等待启动
  COLLECTING_CONDITIONS: 'collecting_conditions',  // 收集用户症状
  SELECTING_CLINIC: 'selecting_clinic',            // 根据症状选择诊室
  COLLECTING_REQUIREMENTS: 'collecting_requirements', // 收集个性化需求
  PATCHING_ROUTE: 'patching_route',                // 优化路线
  COMPLETED: 'completed',           // 流程完成
  ERROR: 'error'                    // 错误状态
}
```

### 状态转移图

```
    [IDLE]
       ↓ (startWorkflow)
[COLLECTING_CONDITIONS]
       ↓ (conditions collected)
[SELECTING_CLINIC]
       ↓ (clinic selected)
[COLLECTING_REQUIREMENTS]
       ↓ (requirements collected)
[PATCHING_ROUTE]
       ↓ (route patched)
[COMPLETED]

    [任何状态]
       ↓ (error occurred)
    [ERROR]
       ↓ (reset)
    [IDLE]
```

## 核心设计模式

### 1. 有限状态机模式 (Finite State Machine)

**实现方式**：Pinia Store + 响应式状态管理

```javascript
// 状态转移函数
const transitionTo = (newState) => {
  if (currentState.value !== newState) {
    previousState.value = currentState.value
    currentState.value = newState
    errorMessage.value = ''
    console.log(`状态转移: ${previousState.value} → ${newState}`)
  }
}

// 错误转移
const transitionToError = (error) => {
  errorMessage.value = error.message || String(error)
  transitionTo(STATE.ERROR)
}
```

### 2. 状态驱动的处理逻辑

**输入处理根据当前状态分发**：

```javascript
const processUserInput = async (userInput) => {
  switch (currentState.value) {
    case STATE.COLLECTING_CONDITIONS:
      await handleConditionsInput(userInput)
      break
    case STATE.COLLECTING_REQUIREMENTS:
      await handleRequirementsInput(userInput)
      break
    default:
      // 其他状态不接受用户输入
  }
}
```

### 3. API 驱动的自动转移

**状态完成时自动触发下一步**：

```javascript
const handleConditionsInput = async (userInput) => {
  // 1. 调用API收集症状
  const response = await apiStore.collectConditions(userInput)

  if (response.success) {
    // 2. 更新状态数据
    conditions.value = response.data

    // 3. 自动转移到下一步
    await autoSelectClinic()  // 内部调用 transitionTo(STATE.SELECTING_CLINIC)
  }
}
```

## 数据流设计

### 状态数据模型

```javascript
// 工作流数据
const conditions = ref(null)        // 结构化症状信息
const requirements = ref(null)      // 用户需求列表
const clinicId = ref(null)          // 选择的诊室ID
const patches = ref(null)           // 路线修改方案
const originalRoute = ref(null)     // 原始路线
const modifiedRoute = ref(null)     // 修改后路线

// 消息历史
const messages = ref([])            // 对话历史记录
```

### 数据验证和计算属性

```javascript
// 状态验证
const hasConditions = computed(() => conditions.value !== null)
const hasRequirements = computed(() => requirements.value?.length > 0)
const hasClinicId = computed(() => clinicId.value !== null)

// 状态便捷访问
const isCollectingConditions = computed(() => currentState.value === STATE.COLLECTING_CONDITIONS)
const isCompleted = computed(() => currentState.value === STATE.COMPLETED)
```

## 语音输入集成设计

### 语音到状态转移的完整流程

```
语音输入 → 语音识别(STT) → 文本处理 → 状态处理 → API调用 → 状态转移 → 语音响应(TTS)
```

### 关键集成点

1. **语音录制**：`useVoiceRecorder` 组合式函数
2. **STT API**：音频格式转换和识别
3. **骨架屏消息**：实时反馈的占位消息
4. **重复消息处理**：防止语音识别导致的重复输入

```javascript
// 语音输入处理流程
const handlePressEnd = async () => {
  // 1. 停止录音
  const audioBlob = await voiceRecorder.stopRecording()

  // 2. 添加骨架屏消息
  const skeletonMessage = workflowStore.addUserMessage('...', {
    isSkeleton: true,
    isProcessing: true
  })

  // 3. 发送到STT API
  const sttResponse = await apiStore.speechToText(audioBlob)

  // 4. 更新消息为识别结果
  workflowStore.updateLastMessage({
    message: recognizedText,
    isSkeleton: false,
    isStreaming: true
  })

  // 5. 触发工作流处理
  await handleVoiceInput(recognizedText)
}
```

## 错误处理策略

### 三级错误处理机制

1. **API级别错误**：网络失败、服务器错误
   ```javascript
   try {
     const response = await apiStore.collectConditions(userInput)
     if (!response.success) {
       throw new Error(response.error || 'API调用失败')
     }
   } catch (error) {
     transitionToError(error)
   }
   ```

2. **状态验证错误**：无效状态转移、数据不完整
   ```javascript
   const autoSelectClinic = async () => {
     if (!conditions.value) {
       transitionToError(new Error('没有症状数据可供选择诊室'))
       return
     }
     // ... 正常处理
   }
   ```

3. **用户恢复机制**：语音命令重启
   ```javascript
   // 检查是否为重启命令
   if (input === '重新开始' || input === 'restart') {
     workflowStore.resetWorkflow()
     workflowStore.startWorkflow()
     return
   }
   ```

## 可复用设计模式

### 1. 状态机模板

```javascript
// 可复用的状态机基础结构
export function createStateMachine(states, initialState) {
  const currentState = ref(initialState)
  const previousState = ref(initialState)

  const transitionTo = (newState) => {
    if (currentState.value !== newState) {
      previousState.value = currentState.value
      currentState.value = newState
    }
  }

  return { currentState, previousState, transitionTo }
}
```

### 2. 多步骤工作流模式

```javascript
// 可应用于其他多步骤流程
class MultiStepWorkflow {
  constructor(steps) {
    this.steps = steps
    this.currentStepIndex = 0
    this.data = {}
  }

  async processInput(input) {
    const currentStep = this.steps[this.currentStepIndex]
    const result = await currentStep.process(input, this.data)

    if (currentStep.isComplete(result)) {
      this.data[currentStep.name] = result
      this.currentStepIndex++

      if (this.currentStepIndex < this.steps.length) {
        return this.steps[this.currentStepIndex].prompt
      } else {
        return this.completeWorkflow()
      }
    }
  }
}
```

### 3. API状态集成模式

```javascript
// API调用与状态管理的标准模式
async function apiDrivenStateTransition(apiCall, data, successCallback, errorCallback) {
  try {
    const response = await apiCall(data)

    if (response.success) {
      await successCallback(response.data)
      return true
    } else {
      errorCallback(new Error(response.error))
      return false
    }
  } catch (error) {
    errorCallback(error)
    return false
  }
}
```

## 实际应用案例

### 医院导航流程

1. **症状收集阶段** (`collecting_conditions`)
   - 输入：语音描述症状（"我头疼"）
   - 处理：提取结构化症状数据
   - 输出：`{ body_parts: "头", severity: "有点", description: "头疼" }`

2. **诊室选择阶段** (`selecting_clinic`)
   - 输入：结构化症状数据
   - 处理：匹配最佳诊室
   - 输出：诊室ID（如："neurology_clinic"）

3. **需求收集阶段** (`collecting_requirements`)
   - 输入：语音描述需求（"需要轮椅"）
   - 处理：提取个性化需求
   - 输出：需求列表 `[{ when: "during navigation", what: "wheelchair access" }]`

4. **路线优化阶段** (`patching_route`)
   - 输入：诊室ID + 需求列表 + 原始路线
   - 处理：生成路线修改方案
   - 输出：路线补丁和优化后路线

## 性能优化考虑

1. **延迟状态转移**：API调用完成后再更新状态
2. **批量消息更新**：避免频繁的UI重渲染
3. **缓存策略**：复用已计算的路由数据
4. **懒加载**：按需加载API模块

## 测试策略

### 单元测试
```javascript
// 状态转移逻辑测试
test('should transition from idle to collecting_conditions on start', () => {
  const store = useWorkflowStore()
  store.startWorkflow()
  expect(store.currentState).toBe('collecting_conditions')
})
```

### 集成测试
```javascript
// 完整工作流测试
test('complete voice-to-route workflow', async () => {
  // 模拟语音输入
  const audioBlob = createTestAudio()
  const text = await sttService.recognize(audioBlob)

  // 执行完整流程
  await workflow.processUserInput(text)

  // 验证最终状态和数据
  expect(workflow.currentState).toBe('completed')
  expect(workflow.hasModifiedRoute).toBe(true)
})
```

## 扩展性设计

### 添加新状态
1. 在 `STATE` 对象中添加新状态常量
2. 实现对应的处理函数
3. 更新状态转移逻辑
4. 添加UI状态指示

### 自定义状态转移规则
```javascript
// 可配置的状态转移规则
const transitionRules = {
  'collecting_conditions': {
    next: 'selecting_clinic',
    condition: (data) => data.conditions !== null,
    action: 'autoSelectClinic'
  },
  'selecting_clinic': {
    next: 'collecting_requirements',
    condition: (data) => data.clinicId !== null,
    action: 'transitionToRequirements'
  }
}
```

## 总结

本状态转移系统设计实现了以下关键特性：

1. **清晰的职责分离**：状态管理、数据处理、UI呈现分离
2. **灵活的扩展机制**：易于添加新状态和转移规则
3. **鲁棒的错误处理**：多层错误恢复机制
4. **优秀的用户体验**：语音驱动、实时反馈、进度可视化
5. **技术栈集成**：Vue 3 Composition API + Pinia + 响应式设计

此设计模式可广泛应用于需要多步骤交互、状态驱动、API集成的应用场景，如问卷调查、订单流程、配置向导等。