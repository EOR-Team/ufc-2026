/**
 * Workflow State Management Store
 *
 * This store manages the four-state workflow for hospital navigation:
 * 1. collecting_conditions - Collect user symptoms
 * 2. collecting_requirements - Collect personalized requirements
 * 3. selecting_clinic - Select appropriate clinic
 * 4. patching_route - Optimize route based on clinic and requirements
 *
 * It also handles state transitions, data persistence, and message history.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useApiStore } from '@/stores/api.js'
import {
  generateOriginalRoute,
  applyPatchesToRoute,
  validateRouteContinuity,
  formatRouteForDisplay
} from '@/utils/route.js'
import { computeHighlights } from '@/utils/mapHighlights.js'
import {
  BASE_PATH,
  CLINIC_ID_PLACEHOLDER,
  DEFAULT_CLINIC_ID
} from '@/types/workflow.js'

/**
 * Create workflow store
 */
export const useWorkflowStore = defineStore('workflow', () => {
  // State machine states
  const STATE = {
    IDLE: 'idle',
    COLLECTING_CONDITIONS: 'collecting_conditions',
    SELECTING_CLINIC: 'selecting_clinic',
    COLLECTING_REQUIREMENTS: 'collecting_requirements',
    PATCHING_ROUTE: 'patching_route',
    COMPLETED: 'completed',
    ERROR: 'error'
  }

  // State
  const currentState = ref(STATE.IDLE)
  const previousState = ref(STATE.IDLE)
  const errorMessage = ref('')

  // Workflow data
  const conditions = ref(null)
  const requirements = ref(null)
  const clinicId = ref(null)
  const patches = ref(null)
  const originalRoute = ref(null)
  const modifiedRoute = ref(null)

  // Map visualization data
  const commands = ref(null)
  const mapData = ref(null)
  const highlightedMap = ref(null)
  const showMapOverlay = ref(false)

  // Message history
  const messages = ref([])

  // API store
  const apiStore = useApiStore()

  // Computed properties
  const isIdle = computed(() => currentState.value === STATE.IDLE)
  const isCollectingConditions = computed(() => currentState.value === STATE.COLLECTING_CONDITIONS)
  const isSelectingClinic = computed(() => currentState.value === STATE.SELECTING_CLINIC)
  const isCollectingRequirements = computed(() => currentState.value === STATE.COLLECTING_REQUIREMENTS)
  const isPatchingRoute = computed(() => currentState.value === STATE.PATCHING_ROUTE)
  const isCompleted = computed(() => currentState.value === STATE.COMPLETED)
  const isError = computed(() => currentState.value === STATE.ERROR)
  const isLoading = computed(() => apiStore.isLoading)

  const hasConditions = computed(() => conditions.value !== null)
  const hasRequirements = computed(() => requirements.value !== null && requirements.value.length > 0)
  const hasClinicId = computed(() => clinicId.value !== null)
  const hasPatches = computed(() => patches.value !== null && patches.value.patches && patches.value.patches.length > 0)
  const hasOriginalRoute = computed(() => originalRoute.value !== null && originalRoute.value.length > 0)
  const hasModifiedRoute = computed(() => modifiedRoute.value !== null && modifiedRoute.value.length > 0)

  // Map visualization computed properties
  const hasCommands = computed(() => commands.value !== null)
  const hasMapData = computed(() => mapData.value !== null)
  const hasHighlightedMap = computed(() => highlightedMap.value !== null)

  const formattedOriginalRoute = computed(() =>
    hasOriginalRoute.value ? formatRouteForDisplay(originalRoute.value) : ''
  )
  const formattedModifiedRoute = computed(() =>
    hasModifiedRoute.value ? formatRouteForDisplay(modifiedRoute.value) : ''
  )

  // State transition methods
  const transitionTo = (newState) => {
    if (currentState.value !== newState) {
      previousState.value = currentState.value
      currentState.value = newState
      errorMessage.value = ''

      console.log(`Workflow state transition: ${previousState.value} → ${newState}`)
    }
  }

  const transitionToError = (error) => {
    errorMessage.value = error.message || String(error)
    transitionTo(STATE.ERROR)
  }

  const resetWorkflow = () => {
    currentState.value = STATE.IDLE
    previousState.value = STATE.IDLE
    errorMessage.value = ''

    conditions.value = null
    requirements.value = null
    clinicId.value = null
    patches.value = null
    originalRoute.value = null
    modifiedRoute.value = null
    commands.value = null
    mapData.value = null
    highlightedMap.value = null
    showMapOverlay.value = false

    messages.value = []

    console.log('Workflow reset')
  }

  // Message management
  const addMessage = (name, message, options = {}) => {
    const messageObj = {
      name,
      message,
      timestamp: Date.now(),
      isProcessing: options.isProcessing || false,
      isError: options.isError || false,
      isSkeleton: options.isSkeleton || false,
      isStreaming: options.isStreaming || false,
      streamingProgress: options.streamingProgress || 0
    }

    messages.value.push(messageObj)
    return messageObj
  }

  const addAssistantMessage = (message, options = {}) => {
    return addMessage('assistant', message, options)
  }

  const addUserMessage = (message, options = {}) => {
    return addMessage('user', message, options)
  }

  const updateLastMessage = (updates) => {
    if (messages.value.length > 0) {
      const lastIndex = messages.value.length - 1
      messages.value[lastIndex] = { ...messages.value[lastIndex], ...updates }
    }
  }

  // Workflow methods
  const startWorkflow = () => {
    resetWorkflow()
    transitionTo(STATE.COLLECTING_CONDITIONS)

    addAssistantMessage('你好！我是智能寻路助手，可以帮你导航到医院各个科室。请描述你的症状，以便我为你选择合适的诊室。')
  }

  const processUserInput = async (userInput) => {
    if (!userInput || userInput.trim() === '') {
      addAssistantMessage('请输入有效的症状描述。')
      return
    }

    // Check if the last message is a user message with the same content
    // This prevents duplicate user messages when voice input updates skeleton message
    const lastMessage = messages.value.length > 0 ? messages.value[messages.value.length - 1] : null
    const isDuplicateUserMessage = lastMessage &&
      lastMessage.name === 'user' &&
      lastMessage.message === userInput &&
      lastMessage.isSkeleton === false

    // Only add user message if it's not a duplicate
    if (!isDuplicateUserMessage) {
      addUserMessage(userInput)
    } else {
      console.log('[Workflow] Skipping duplicate user message:', userInput)
    }

    // Process based on current state
    switch (currentState.value) {
      case STATE.COLLECTING_CONDITIONS:
        await handleConditionsInput(userInput)
        break

      case STATE.COLLECTING_REQUIREMENTS:
        await handleRequirementsInput(userInput)
        break

      default:
        addAssistantMessage(`当前状态无法处理输入。当前状态: ${currentState.value}`)
    }
  }

  const handleConditionsInput = async (userInput) => {
    console.log('[Workflow] handleConditionsInput called with:', userInput)
    const processingMsg = addAssistantMessage('正在分析你的症状...', { isProcessing: true })

    try {
      // Call API to collect conditions
      console.log('[Workflow] Calling collectConditions API...')
      const response = await apiStore.collectConditions(userInput)
      console.log('[Workflow] collectConditions API response:', response)

      if (response.success && response.data) {
        // Update conditions
        conditions.value = response.data

        // Update message
        const symptomDesc = response.data.description || '症状已记录'
        updateLastMessage({
          message: `已分析你的症状：${symptomDesc}。现在为你选择合适的诊室...`,
          isProcessing: false
        })

        // Auto-transition to selecting clinic
        await autoSelectClinic()
      } else {
        // API error
        console.error('[Workflow] collectConditions API error:', response.error)
        updateLastMessage({
          message: `抱歉，分析症状时出现错误：${response.error || '未知错误'}`,
          isProcessing: false,
          isError: true
        })

        transitionToError(new Error(response.error || 'Failed to collect conditions'))
      }
    } catch (error) {
      console.error('[Workflow] Exception in handleConditionsInput:', error)
      updateLastMessage({
        message: `处理症状时出现错误：${error.message}`,
        isProcessing: false,
        isError: true
      })

      transitionToError(error)
    }
  }

  const autoSelectClinic = async () => {
    if (!conditions.value) {
      transitionToError(new Error('No conditions available for clinic selection'))
      return
    }

    transitionTo(STATE.SELECTING_CLINIC)
    const processingMsg = addAssistantMessage('正在根据症状选择合适诊室...', { isProcessing: true })

    try {
      // Call API to select clinic
      const response = await apiStore.selectClinic(conditions.value)

      if (response.success && response.data) {
        // Extract clinic selection - handle different response formats
        const clinicSelection = response.data.clinic_selection || response.data

        if (clinicSelection) {
          // Update clinic ID
          clinicId.value = typeof clinicSelection === 'string' ? clinicSelection : String(clinicSelection)

          // Generate original route
          originalRoute.value = generateOriginalRoute(clinicId.value)

          // Update message
          updateLastMessage({
            message: `已为你选择 ${clinicId.value} 诊室。请告诉我你有什么个性化需求（例如：需要轮椅、需要优先就诊等），我将为你优化路线。`,
            isProcessing: false
          })

          // Auto-transition to collecting requirements
          transitionTo(STATE.COLLECTING_REQUIREMENTS)
        } else {
          throw new Error('No clinic selection in response')
        }
      } else {
        // API error
        updateLastMessage({
          message: `抱歉，选择诊室时出现错误：${response.error || '未知错误'}`,
          isProcessing: false,
          isError: true
        })

        transitionToError(new Error(response.error || 'Failed to select clinic'))
      }
    } catch (error) {
      updateLastMessage({
        message: `选择诊室时出现错误：${error.message}`,
        isProcessing: false,
        isError: true
      })

      transitionToError(error)
    }
  }

  const handleRequirementsInput = async (userInput) => {
    const processingMsg = addAssistantMessage('正在分析你的需求...', { isProcessing: true })

    try {
      // Call API to collect requirements
      const response = await apiStore.collectRequirement(userInput)

      if (response.success && response.data) {
        // Update requirements - response.data should be an array
        requirements.value = Array.isArray(response.data) ? response.data : []

        // Update message
        const reqCount = requirements.value.length
        updateLastMessage({
          message: `已记录你的${reqCount > 0 ? ` ${reqCount} 项` : ''}需求。现在根据诊室和需求优化路线...`,
          isProcessing: false
        })

        // Auto-transition to patching route
        await autoPatchRoute()
      } else {
        // API error
        updateLastMessage({
          message: `抱歉，分析需求时出现错误：${response.error || '未知错误'}`,
          isProcessing: false,
          isError: true
        })

        transitionToError(new Error(response.error || 'Failed to collect requirements'))
      }
    } catch (error) {
      updateLastMessage({
        message: `处理需求时出现错误：${error.message}`,
        isProcessing: false,
        isError: true
      })

      transitionToError(error)
    }
  }

  const autoPatchRoute = async () => {
    if (!clinicId.value || !requirements.value || !originalRoute.value) {
      transitionToError(new Error('Missing data for route patching'))
      return
    }

    transitionTo(STATE.PATCHING_ROUTE)
    const processingMsg = addAssistantMessage('正在根据你的需求优化路线...', { isProcessing: true })

    try {
      // Call API to patch route
      const response = await apiStore.patchRoute(
        clinicId.value,
        requirements.value,
        originalRoute.value
      )

      if (response.success && response.data) {
        // Update patches
        patches.value = response.data

        // Apply patches to generate modified route
        const patchesList = response.data.patches || []
        modifiedRoute.value = applyPatchesToRoute(originalRoute.value, patchesList)

        // Validate the modified route
        const validation = validateRouteContinuity(modifiedRoute.value)

        // Update message
        if (validation.valid) {
          updateLastMessage({
            message: `路线优化完成！\n\n原始路线：\n${formattedOriginalRoute.value}\n\n优化后路线：\n${formattedModifiedRoute.value}\n\n你可以按照这个路线前往诊室。`,
            isProcessing: false
          })
        } else {
          updateLastMessage({
            message: `路线优化完成，但路线连续性验证失败：${validation.errors.join('; ')}\n\n优化后路线：\n${formattedModifiedRoute.value}`,
            isProcessing: false,
            isError: true
          })
        }

        // 解析命令
        if (mapData.value && modifiedRoute.value) {
          try {
            const commandsResponse = await apiStore.parseCommands(modifiedRoute.value);
            if (commandsResponse.success) {
              commands.value = commandsResponse.data;
              console.log('[Workflow] Commands parsed:', commands.value);

              // 计算高亮地图
              highlightedMap.value = computeHighlights(commands.value, mapData.value);
              console.log('[Workflow] Highlighted map computed:', highlightedMap.value);
            } else {
              console.warn('[Workflow] Failed to parse commands:', commandsResponse.error);
            }
          } catch (commandsError) {
            console.error('[Workflow] Exception parsing commands:', commandsError);
          }
        }

        // Transition to completed state
        transitionTo(STATE.COMPLETED)
      } else {
        // API error
        updateLastMessage({
          message: `抱歉，优化路线时出现错误：${response.error || '未知错误'}`,
          isProcessing: false,
          isError: true
        })

        transitionToError(new Error(response.error || 'Failed to patch route'))
      }
    } catch (error) {
      updateLastMessage({
        message: `优化路线时出现错误：${error.message}`,
        isProcessing: false,
        isError: true
      })

      transitionToError(error)
    }
  }

  // Quick start method for testing
  const quickStartDemo = async () => {
    resetWorkflow()
    transitionTo(STATE.COLLECTING_CONDITIONS)

    addAssistantMessage('你好！我是智能寻路助手，可以帮你导航到医院各个科室。请描述你的症状，以便我为你选择合适的诊室。')

    // Simulate user input after a delay
    setTimeout(() => {
      processUserInput('我头痛已经两天了，有点发烧，感觉头晕')
    }, 1000)
  }

  // Map visualization methods
  const showMap = () => {
    if (hasHighlightedMap.value) {
      showMapOverlay.value = true
      console.log('[Workflow] Showing map overlay')
    } else {
      console.warn('[Workflow] Cannot show map: no highlighted map data available')
    }
  }

  const hideMap = () => {
    showMapOverlay.value = false
    console.log('[Workflow] Hiding map overlay')
  }

  return {
    // State
    STATE,
    currentState,
    previousState,
    errorMessage,
    conditions,
    requirements,
    clinicId,
    patches,
    originalRoute,
    modifiedRoute,
    commands,
    mapData,
    highlightedMap,
    showMapOverlay,
    messages,

    // Computed
    isIdle,
    isCollectingConditions,
    isSelectingClinic,
    isCollectingRequirements,
    isPatchingRoute,
    isCompleted,
    isError,
    isLoading,
    hasConditions,
    hasRequirements,
    hasClinicId,
    hasPatches,
    hasOriginalRoute,
    hasModifiedRoute,
    formattedOriginalRoute,
    formattedModifiedRoute,
    hasCommands,
    hasMapData,
    hasHighlightedMap,

    // Methods
    transitionTo,
    transitionToError,
    resetWorkflow,
    addMessage,
    addAssistantMessage,
    addUserMessage,
    updateLastMessage,
    startWorkflow,
    processUserInput,
    handleConditionsInput,
    autoSelectClinic,
    handleRequirementsInput,
    autoPatchRoute,
    quickStartDemo,
    showMap,
    hideMap
  }
})