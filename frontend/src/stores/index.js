/**
 * Pinia Stores Index
 *
 * Central export point for all stores to avoid circular dependencies
 * and provide a clean import interface.
 */

export { useWorkflowStore } from './workflow.js'
export { useApiStore } from './api.js'

/**
 * Helper to initialize all stores at once
 * This is optional but can be useful for testing or debugging
 */
export function initializeAllStores() {
  // Stores are auto-initialized when used via useStore()
  // This function is just for semantic clarity
  console.log('All stores available for use')
}