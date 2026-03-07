/**
 * API Service Store
 *
 * This store handles all HTTP communication with the backend API.
 * It provides a centralized HTTP client with error handling and loading state management.
 */

import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'

/**
 * Create API store
 */
export const useApiStore = defineStore('api', () => {
  // State
  const isLoading = ref(false)
  const error = ref(null)
  const lastRequestTime = ref(null)

  // Configuration
  const DEFAULT_ONLINE_MODEL = import.meta.env.VITE_DEFAULT_ONLINE_MODEL === 'true' || true
  const ENABLE_LOGGING = import.meta.env.VITE_ENABLE_LOGGING === 'true' || false

  // Server address (without /api suffix)
  const getInitialServerAddress = () => {
    // First check localStorage
    if (typeof window !== 'undefined' && window.localStorage) {
      const stored = localStorage.getItem('serverAddress')
      if (stored !== null) return stored
    }
    // Then check environment variables
    const envServerAddress = import.meta.env.VITE_SERVER_ADDRESS
    if (envServerAddress) return envServerAddress
    const envApiBaseUrl = import.meta.env.VITE_API_BASE_URL
    if (envApiBaseUrl) {
      // Remove /api suffix if present
      let url = envApiBaseUrl.trim()
      url = url.replace(/\/$/, '')
      if (url.endsWith('/api')) {
        url = url.slice(0, -4)
      }
      return url
    }
    // Default fallback
    return 'http://localhost:8000'
  }
  const serverAddress = ref(getInitialServerAddress())
  // Base URL for API requests (serverAddress + /api)
  const baseUrl = computed(() => {
    let addr = serverAddress.value.trim()
    if (!addr) {
      addr = 'http://localhost:8000'
    }
    // Remove trailing slash
    addr = addr.replace(/\/$/, '')
    // Remove /api suffix if present
    if (addr.endsWith('/api')) {
      addr = addr.slice(0, -4)
    }
    return `${addr}/api`
  })

  // 在线模型开关（可由设置页面控制）
  const onlineModelEnabled = ref(DEFAULT_ONLINE_MODEL)

  // Persist server address changes to localStorage
  watch(serverAddress, (newVal) => {
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.setItem('serverAddress', newVal)
    }
  })

  /**
   * Log debug messages if logging is enabled
   */
  const log = (...args) => {
    if (ENABLE_LOGGING) {
      console.log('[API Store]', ...args)
    }
  }

  /**
   * Make an HTTP request with standardized error handling
   * @param {string} endpoint - API endpoint (without base URL)
   * @param {Object} options - Fetch options
   * @returns {Promise<ApiResponse>} Standardized API response
   */
  const request = async (endpoint, options = {}) => {
    isLoading.value = true
    error.value = null
    lastRequestTime.value = Date.now()

    const url = `${baseUrl.value}${endpoint}`
    log(`Making request to: ${url}`, options)

    try {
      // 准备请求头
      const headers = { ...options.headers }

      // 如果不是 FormData，默认设置 JSON Content-Type
      // FormData 会自动设置正确的 Content-Type 和 boundary
      if (!(options.body instanceof FormData)) {
        headers['Content-Type'] = 'application/json'
      }

      const response = await fetch(url, {
        headers,
        ...options
      })

      const responseText = await response.text()
      let data

      try {
        data = responseText ? JSON.parse(responseText) : {}
      } catch (parseError) {
        log('Failed to parse JSON response:', responseText)
        throw new Error(`Invalid JSON response: ${parseError.message}`)
      }

      if (!response.ok) {
        throw new Error(data.error || `HTTP ${response.status}: ${response.statusText}`)
      }

      // Some backend endpoints return JSON strings within the data field
      // Check if data.data is a string that looks like JSON and parse it
      if (data.success && data.data && typeof data.data === 'string') {
        try {
          data.data = JSON.parse(data.data)
        } catch (e) {
          // If it's not valid JSON, keep it as a string
          log('Data field is not valid JSON, keeping as string:', data.data)
        }
      }

      log('Request successful:', data)
      return data
    } catch (err) {
      error.value = err.message
      log('Request failed:', err.message)

      // Return standardized error response
      return {
        success: false,
        error: err.message
      }
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Collect conditions from user input
   * @param {string} userInput - User's symptom description
   * @param {boolean} [onlineModel] - Whether to use online model
   * @returns {Promise<ApiResponse>} API response with ConditionCollectorOutput
   */
  const collectConditions = async (userInput, onlineModel = onlineModelEnabled.value) => {
    log('Collecting conditions:', { userInput, onlineModel })

    return await request('/triager/collect_conditions/', {
      method: 'POST',
      body: JSON.stringify({
        user_input: userInput,
        online_model: onlineModel
      })
    })
  }

  /**
   * Select clinic based on conditions
   * @param {ConditionCollectorOutput} conditions - Structured symptom information
   * @param {boolean} [onlineModel] - Whether to use online model
   * @returns {Promise<ApiResponse>} API response with clinic selection
   */
  const selectClinic = async (conditions, onlineModel = onlineModelEnabled.value) => {
    log('Selecting clinic:', { conditions, onlineModel })

    return await request('/triager/select_clinic/', {
      method: 'POST',
      body: JSON.stringify({
        conditions,
        online_model: onlineModel
      })
    })
  }

  /**
   * Collect requirements from user input
   * @param {string} userInput - User's requirement description
   * @param {boolean} [onlineModel] - Whether to use online model
   * @returns {Promise<ApiResponse>} API response with requirements list
   */
  const collectRequirement = async (userInput, onlineModel = onlineModelEnabled.value) => {
    log('Collecting requirements:', { userInput, onlineModel })

    return await request('/triager/collect_requirement/', {
      method: 'POST',
      body: JSON.stringify({
        user_input: userInput,
        online_model: onlineModel
      })
    })
  }

  /**
   * Patch route based on clinic ID and requirements
   * @param {string} destinationClinicId - Destination clinic ID
   * @param {Requirement[]} requirementSummary - List of requirements
   * @param {LocationLink[]} originRoute - Original route
   * @param {boolean} [onlineModel] - Whether to use online model
   * @returns {Promise<ApiResponse>} API response with route patches
   */
  const patchRoute = async (
    destinationClinicId,
    requirementSummary,
    originRoute,
    onlineModel = onlineModelEnabled.value
  ) => {
    log('Patching route:', { destinationClinicId, requirementSummary, originRoute, onlineModel })

    return await request('/triager/patch_route/', {
      method: 'POST',
      body: JSON.stringify({
        destination_clinic_id: destinationClinicId,
        requirement_summary: requirementSummary,
        origin_route: originRoute,
        online_model: onlineModel
      })
    })
  }

  /**
   * Get route patch through complete workflow
   * @param {string} userInput - User's symptom and requirement description
   * @param {LocationLink[]} originRoute - Original route
   * @param {boolean} [onlineModel] - Whether to use online model
   * @returns {Promise<ApiResponse>} API response with complete route patch
   */
  const getRoutePatch = async (userInput, originRoute, onlineModel = onlineModelEnabled.value) => {
    log('Getting route patch:', { userInput, originRoute, onlineModel })

    return await request('/triager/get_route_patch/', {
      method: 'POST',
      body: JSON.stringify({
        user_input: userInput,
        origin_route: originRoute,
        online_model: onlineModel
      })
    })
  }

  /**
   * Parse route to commands
   * @param {LocationLink[]} originRoute - Original route (优化后的路线)
   * @returns {Promise<ApiResponse>} API response with parsed commands
   */
  const parseCommands = async (originRoute) => {
    log('Parsing commands:', { originRoute })

    return await request('/triager/parse_commands/', {
      method: 'POST',
      body: JSON.stringify({
        origin_route: originRoute
      })
    })
  }

  /**
   * Execute a single car command
   * @param {CarAction} action - Car action to execute
   * @param {number} commandIndex - Index of the command in the sequence (optional)
   * @param {string} carId - Car identifier (default: "default_car")
   * @returns {Promise<ApiResponse>} API response with execution result
   */
  const executeCarCommand = async (action, commandIndex = null, carId = 'default_car') => {
    log('Executing car command:', { action, commandIndex, carId })

    return await request('/navigation/execute_command/', {
      method: 'POST',
      body: JSON.stringify({
        action,
        car_id: carId,
        command_index: commandIndex
      })
    })
  }

  /**
   * Execute multiple car commands
   * @param {CarAction[]} actions - Array of car actions to execute
   * @param {number} startIndex - Starting index for execution (optional, default: 0)
   * @param {string} carId - Car identifier (default: "default_car")
   * @returns {Promise<ApiResponse>} API response with execution results
   */
  const executeCarCommands = async (actions, startIndex = 0, carId = 'default_car') => {
    log('Executing car commands:', { actions: actions.length, startIndex, carId })

    return await request('/navigation/execute_commands/', {
      method: 'POST',
      body: JSON.stringify({
        actions,
        car_id: carId,
        start_index: startIndex
      })
    })
  }

  /**
   * Verify current position
   * @param {string} expectedDestination - Expected destination node ID
   * @param {string} carId - Car identifier (default: "default_car")
   * @param {string} imageData - Base64 encoded image data (optional)
   * @returns {Promise<ApiResponse>} API response with verification result
   */
  const verifyPosition = async (expectedDestination, carId = 'default_car', imageData = null) => {
    log('Verifying position:', { expectedDestination, carId })

    const requestBody = {
      expected_destination: expectedDestination,
      car_id: carId
    }

    if (imageData) {
      requestBody.image_data = imageData
    }

    return await request('/navigation/verify_position/', {
      method: 'POST',
      body: JSON.stringify(requestBody)
    })
  }

  /**
   * Get navigation status
   * @param {string} carId - Car identifier (default: "default_car")
   * @returns {Promise<ApiResponse>} API response with navigation status
   */
  const getNavigationStatus = async (carId = 'default_car') => {
    log('Getting navigation status:', { carId })

    return await request(`/navigation/status/?car_id=${encodeURIComponent(carId)}`, {
      method: 'GET'
    })
  }

  /**
   * Start navigation with commands
   * @param {CarCommandsOutput} commands - Car commands to execute
   * @param {string} carId - Car identifier (default: "default_car")
   * @returns {Promise<ApiResponse>} API response with navigation start confirmation
   */
  const startNavigation = async (commands, carId = 'default_car') => {
    log('Starting navigation:', { commands: commands.actions.length, carId })

    return await request('/navigation/start_navigation/', {
      method: 'POST',
      body: JSON.stringify({
        commands,
        car_id: carId
      })
    })
  }

  /**
   * Pause navigation
   * @param {string} carId - Car identifier (default: "default_car")
   * @returns {Promise<ApiResponse>} API response with pause confirmation
   */
  const pauseNavigation = async (carId = 'default_car') => {
    log('Pausing navigation:', { carId })

    return await request('/navigation/pause_navigation/', {
      method: 'POST',
      body: JSON.stringify({
        car_id: carId
      })
    })
  }

  /**
   * Resume navigation
   * @param {string} carId - Car identifier (default: "default_car")
   * @returns {Promise<ApiResponse>} API response with resume confirmation
   */
  const resumeNavigation = async (carId = 'default_car') => {
    log('Resuming navigation:', { carId })

    return await request('/navigation/resume_navigation/', {
      method: 'POST',
      body: JSON.stringify({
        car_id: carId
      })
    })
  }

  /**
   * Stop navigation
   * @param {string} carId - Car identifier (default: "default_car")
   * @returns {Promise<ApiResponse>} API response with stop confirmation
   */
  const stopNavigation = async (carId = 'default_car') => {
    log('Stopping navigation:', { carId })

    return await request('/navigation/stop_navigation/', {
      method: 'POST',
      body: JSON.stringify({
        car_id: carId
      })
    })
  }

  /**
   * Get hospital map data
   * @returns {Promise<ApiResponse>} API response with map data (nodes and edges)
   */
  const getMap = async () => {
    log('Getting map data')

    return await request('/map/', {
      method: 'GET'
    })
  }

  /**
   * Convert speech to text using backend STT API
   * @param {Blob} audioBlob - Audio blob from voice recording
   * @returns {Promise<ApiResponse>} API response with recognized text
   */
  const speechToText = async (audioBlob) => {
    log('Converting speech to text:', {
      size: audioBlob.size,
      type: audioBlob.type
    })

    // 创建 FormData 并添加音频文件
    const formData = new FormData()
    formData.append('file', audioBlob, 'audio.wav')

    // 调用基础 request 方法
    const response = await request('/voice/stt/', {
      method: 'POST',
      body: formData
      // 注意：FormData 会自动设置正确的 Content-Type
      // 我们修改的 request 方法会检测到 FormData 并不设置默认的 JSON Content-Type
    })

    log('STT API raw response:', response)

    // 处理不同的响应格式
    // 格式1: {text: "recognized text"} (旧格式)
    // 格式2: {success: true, data: {text: "recognized text"}} (标准格式)

    if (response.success === true && response.data && response.data.text) {
      // 已经是标准格式，直接返回
      log('STT response in standard format')
      return response
    } else if (response.text) {
      // 旧格式：{text: "recognized text"}
      log('STT response in legacy format, converting to standard format')
      return {
        success: true,
        data: {
          text: response.text
        }
      }
    } else if (response.success === false) {
      // 已经是错误格式
      log('STT response indicates failure')
      return response
    } else {
      // 未知格式
      log('STT response in unknown format')
      return {
        success: false,
        error: 'Unknown response format from STT API'
      }
    }
  }

  /**
   * Convert text to speech using backend TTS API
   * @param {string} text - Text to synthesize
   * @returns {Promise<Blob|null>} WAV audio Blob, or null on failure
   */
  const tts = async (text) => {
    const url = `${baseUrl.value}/voice/tts?text=${encodeURIComponent(text)}`
    log('TTS request:', text)
    try {
      const response = await fetch(url)
      if (!response.ok) throw new Error(`TTS HTTP ${response.status}`)
      return await response.blob()
    } catch (err) {
      log('TTS failed:', err.message)
      return null
    }
  }

  /**
   * Get medical suggestion from backend
   * @param {string} symptoms - User's symptoms / message
   * @param {string|null} [diagnosis] - Doctor's diagnosis (optional)
   * @param {boolean} [onlineModel] - Whether to use online model
   * @returns {Promise<ApiResponse>} API response with { response, scenario, requires_doctor_consultation }
   */
  const getMedicalSuggestion = async (symptoms, diagnosis = null, onlineModel = onlineModelEnabled.value) => {
    log('Getting medical suggestion:', { symptoms, diagnosis, onlineModel })

    const params = new URLSearchParams()
    params.append('symptoms', symptoms)
    if (diagnosis !== null && diagnosis !== '') {
      params.append('diagnosis', diagnosis)
    }
    params.append('online_model', String(onlineModel))

    return await request(`/medical/suggest?${params.toString()}`, {
      method: 'GET'
    })
  }

  /**
   * Clear error state
   */
  const clearError = () => {
    error.value = null
  }

  /**
   * Reset store state
   */
  const reset = () => {
    isLoading.value = false
    error.value = null
    lastRequestTime.value = null
  }

  return {
    // State
    isLoading,
    error,
    lastRequestTime,

    // Configuration
    serverAddress,
    baseUrl,
    DEFAULT_ONLINE_MODEL,
    onlineModelEnabled,

    // Methods
    request,
    collectConditions,
    selectClinic,
    collectRequirement,
    patchRoute,
    getRoutePatch,
    parseCommands,
    getMap,
    speechToText,
    tts,
    getMedicalSuggestion,
    clearError,
    // Navigation methods
    executeCarCommand,
    executeCarCommands,
    verifyPosition,
    getNavigationStatus,
    startNavigation,
    pauseNavigation,
    resumeNavigation,
    stopNavigation,
    reset
  }
})