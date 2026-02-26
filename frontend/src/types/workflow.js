/**
 * Workflow Type Definitions
 *
 * This file defines the TypeScript/JSDoc types for the workflow state system.
 * These types mirror the backend Pydantic models to ensure data consistency.
 */

/**
 * @typedef {Object} LocationLink
 * @property {string} this - Current location ID
 * @property {string} next - Next location ID
 */

/**
 * @typedef {Object} ConditionCollectorOutput
 * @property {string} body_parts - Affected body parts
 * @property {string} duration - Symptom duration
 * @property {string} severity - Symptom severity
 * @property {string} description - Detailed symptom description
 * @property {string[]} other_relevant_information - Other relevant information
 */

/**
 * @typedef {Object} Requirement
 * @property {string} when - When to execute the requirement (e.g., "during consultation", "after prescription")
 * @property {string} what - What the patient needs (e.g., "ask more questions", "prescribe medication")
 */

/**
 * @typedef {Object} LocationLinkPatch
 * @property {'insert' | 'delete'} type - Patch type: insert or delete
 * @property {string} previous - Previous location ID
 * @property {string} this - Current location ID
 * @property {string} next - Next location ID
 */

/**
 * @typedef {Object} RoutePatcherOutput
 * @property {LocationLinkPatch[]} patches - List of route patches
 */

/**
 * @typedef {Object} ClinicSelectionOutput
 * @property {string} clinic_selection - Selected clinic ID
 */

/**
 * @typedef {Object} ApiResponse
 * @property {boolean} success - Whether the API call succeeded
 * @property {any} [data] - Response data if success is true
 * @property {string} [error] - Error message if success is false
 */

/**
 * @typedef {'idle' | 'collecting_conditions' | 'collecting_requirements' | 'selecting_clinic' | 'patching_route' | 'completed' | 'error'} WorkflowState
 */

/**
 * @typedef {Object} WorkflowData
 * @property {ConditionCollectorOutput | null} conditions - Structured symptom information
 * @property {Requirement[] | null} requirements - Patient requirements
 * @property {string | null} clinicId - Selected clinic ID
 * @property {RoutePatcherOutput | null} patches - Route patches
 * @property {LocationLink[] | null} originalRoute - Original route before patching
 * @property {LocationLink[] | null} modifiedRoute - Final route after applying patches
 */

/**
 * @typedef {Object} Message
 * @property {'assistant' | 'user'} name - Sender of the message
 * @property {string} message - Message content
 * @property {boolean} [isProcessing] - Whether the message is being processed
 * @property {boolean} [isError] - Whether the message indicates an error
 * @property {boolean} [isSkeleton] - Whether the message is a skeleton/loading placeholder
 * @property {boolean} [isStreaming] - Whether the message is streaming text content
 * @property {number} [streamingProgress] - Streaming progress (0-100) for progressive display
 */

/**
 * Base path template for hospital navigation
 * This matches the backend's origin_route_list in triager.py
 * @type {LocationLink[]}
 */
export const BASE_PATH = [
  { this: 'entrance', next: 'registration_center' },
  { this: 'registration_center', next: '<xxx_clinic>' },
  { this: '<xxx_clinic>', next: 'pharmacy' },
  { this: 'pharmacy', next: 'exit' }
]

/**
 * Clinic ID placeholders to replace in the base path
 */
export const CLINIC_ID_PLACEHOLDER = '<xxx_clinic>'

/**
 * Default clinic ID (surgery clinic) for fallback
 */
export const DEFAULT_CLINIC_ID = 'surgery_clinic'