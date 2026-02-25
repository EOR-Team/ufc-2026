/**
 * Route Utility Functions
 *
 * Pure functions for route generation, modification, validation, and formatting.
 */

import { BASE_PATH, CLINIC_ID_PLACEHOLDER, DEFAULT_CLINIC_ID } from '@/types/workflow.js'

/**
 * Generate original route by replacing clinic placeholder in base path
 * @param {string} clinicId - Clinic ID to insert into route
 * @param {LocationLink[]} [basePath=BASE_PATH] - Base path template
 * @returns {LocationLink[]} Original route with clinic ID
 */
export function generateOriginalRoute(clinicId, basePath = BASE_PATH) {
  if (!clinicId) {
    throw new Error('Clinic ID is required to generate original route')
  }

  return basePath.map(link => ({
    this: link.this === CLINIC_ID_PLACEHOLDER ? clinicId : link.this,
    next: link.next === CLINIC_ID_PLACEHOLDER ? clinicId : link.next
  }))
}

/**
 * Apply patches to original route
 * @param {LocationLink[]} originalRoute - Original route
 * @param {LocationLinkPatch[]} patches - List of patches to apply
 * @returns {LocationLink[]} Modified route after applying patches
 */
export function applyPatchesToRoute(originalRoute, patches) {
  if (!patches || patches.length === 0) {
    return [...originalRoute]
  }

  // Start with a copy of the original route
  let modifiedRoute = [...originalRoute]

  // First, apply delete patches
  const deletePatches = patches.filter(p => p.type === 'delete')
  const insertPatches = patches.filter(p => p.type === 'insert')

  // Apply delete patches
  for (const patch of deletePatches) {
    // Find the link to delete
    const index = modifiedRoute.findIndex(
      link => link.this === patch.this && link.next === patch.next
    )

    if (index !== -1) {
      // Also need to update the previous link's next pointer
      if (index > 0) {
        const previousLink = modifiedRoute[index - 1]
        const nextLink = index < modifiedRoute.length - 1 ? modifiedRoute[index + 1] : null

        // Update previous link to point to the link after the deleted one
        if (nextLink) {
          modifiedRoute[index - 1] = { ...previousLink, next: nextLink.this }
        }
      }

      // Remove the link
      modifiedRoute.splice(index, 1)
    }
  }

  // Apply insert patches
  for (const patch of insertPatches) {
    // Find where to insert (after the link with this = patch.previous)
    const insertAfterIndex = modifiedRoute.findIndex(link => link.this === patch.previous)

    if (insertAfterIndex !== -1) {
      // Create the new link
      const newLink = { this: patch.this, next: patch.next }

      // Update the previous link's next pointer
      modifiedRoute[insertAfterIndex] = { ...modifiedRoute[insertAfterIndex], next: patch.this }

      // Insert the new link
      modifiedRoute.splice(insertAfterIndex + 1, 0, newLink)
    } else {
      // If we can't find where to insert, append to the end
      console.warn(`Could not find link with this=${patch.previous}, appending new link`)
      modifiedRoute.push({ this: patch.this, next: patch.next })
    }
  }

  return modifiedRoute
}

/**
 * Validate route continuity
 * @param {LocationLink[]} route - Route to validate
 * @returns {{valid: boolean, errors: string[]}} Validation result
 */
export function validateRouteContinuity(route) {
  const errors = []

  if (!route || route.length === 0) {
    errors.push('Route is empty')
    return { valid: false, errors }
  }

  // Check that each link's next matches the next link's this
  for (let i = 0; i < route.length - 1; i++) {
    const currentLink = route[i]
    const nextLink = route[i + 1]

    if (currentLink.next !== nextLink.this) {
      errors.push(`Link discontinuity at index ${i}: ${currentLink.this}→${currentLink.next} does not connect to ${nextLink.this}→${nextLink.next}`)
    }
  }

  // Check for duplicate this values (except at junctions)
  const thisValues = route.map(link => link.this)
  const duplicateThis = thisValues.filter((value, index) => thisValues.indexOf(value) !== index)

  if (duplicateThis.length > 0) {
    errors.push(`Duplicate location IDs found: ${[...new Set(duplicateThis)].join(', ')}`)
  }

  return {
    valid: errors.length === 0,
    errors
  }
}

/**
 * Format route for display
 * @param {LocationLink[]} route - Route to format
 * @returns {string} Formatted route string
 */
export function formatRouteForDisplay(route) {
  if (!route || route.length === 0) {
    return 'No route available'
  }

  const steps = []

  // Add starting point
  steps.push(`从 ${route[0].this} 出发`)

  // Add each step
  for (let i = 0; i < route.length; i++) {
    const link = route[i]

    if (i < route.length - 1) {
      steps.push(`→ 前往 ${link.next}`)
    } else {
      steps.push(`→ 到达终点 ${link.next}`)
    }
  }

  return steps.join('\n')
}

/**
 * Format patches for display
 * @param {LocationLinkPatch[]} patches - Patches to format
 * @returns {string} Formatted patches description
 */
export function formatPatchesForDisplay(patches) {
  if (!patches || patches.length === 0) {
    return '无路线修改'
  }

  const descriptions = patches.map(patch => {
    if (patch.type === 'insert') {
      return `在 ${patch.previous} 之后插入 ${patch.this} → ${patch.next}`
    } else if (patch.type === 'delete') {
      return `删除 ${patch.this} → ${patch.next}`
    }
    return `未知修改类型: ${patch.type}`
  })

  return '路线修改:\n' + descriptions.join('\n')
}

/**
 * Extract location IDs from route
 * @param {LocationLink[]} route - Route to extract IDs from
 * @returns {string[]} List of location IDs in order
 */
export function extractLocationIds(route) {
  if (!route || route.length === 0) {
    return []
  }

  const ids = [route[0].this]

  for (const link of route) {
    ids.push(link.next)
  }

  return [...new Set(ids)] // Remove duplicates while preserving order
}

/**
 * Check if a route contains a specific location
 * @param {LocationLink[]} route - Route to check
 * @param {string} locationId - Location ID to find
 * @returns {boolean} Whether the location is in the route
 */
export function routeContainsLocation(route, locationId) {
  if (!route || !locationId) return false

  return route.some(link => link.this === locationId || link.next === locationId)
}

/**
 * Get the next location from current position
 * @param {LocationLink[]} route - Route to navigate
 * @param {string} currentLocation - Current location ID
 * @returns {string | null} Next location ID, or null if not found or at end
 */
export function getNextLocation(route, currentLocation) {
  if (!route || !currentLocation) return null

  for (const link of route) {
    if (link.this === currentLocation) {
      return link.next
    }
  }

  return null
}

export default {
  generateOriginalRoute,
  applyPatchesToRoute,
  validateRouteContinuity,
  formatRouteForDisplay,
  formatPatchesForDisplay,
  extractLocationIds,
  routeContainsLocation,
  getNextLocation
}