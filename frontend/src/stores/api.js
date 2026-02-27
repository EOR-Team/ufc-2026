/**
 * API Service Store
 *
 * This store handles all HTTP communication with the backend API.
 * It provides a centralized HTTP client with error handling and loading state management.
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'

/**
 * Create API store
 */
export const useApiStore = defineStore('api', () => {
  // State
  const isLoading = ref(false)
  const error = ref(null)
  const lastRequestTime = ref(null)

  // Configuration
  const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'
  const DEFAULT_ONLINE_MODEL = import.meta.env.VITE_DEFAULT_ONLINE_MODEL === 'true' || true
  const ENABLE_LOGGING = import.meta.env.VITE_ENABLE_LOGGING === 'true' || false

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

    const url = `${BASE_URL}${endpoint}`
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
  const collectConditions = async (userInput, onlineModel = DEFAULT_ONLINE_MODEL) => {
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
  const selectClinic = async (conditions, onlineModel = DEFAULT_ONLINE_MODEL) => {
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
  const collectRequirement = async (userInput, onlineModel = DEFAULT_ONLINE_MODEL) => {
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
    onlineModel = DEFAULT_ONLINE_MODEL
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
  const getRoutePatch = async (userInput, originRoute, onlineModel = DEFAULT_ONLINE_MODEL) => {
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
   * Get hospital map data
   * @returns {Promise<ApiResponse>} API response with map data (nodes and edges)
   */
  const getMap = async () => {
    log('Getting map data')

    return await request('/triager/map/', {
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
    BASE_URL,
    DEFAULT_ONLINE_MODEL,

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
    clearError,
    reset
  }
})