/**
 * Workflow Demo Script
 *
 * This script demonstrates the workflow state switching system
 * without requiring a running backend.
 * Run in browser console to test the workflow logic.
 */

// Mock API responses for demonstration
const MOCK_RESPONSES = {
  collectConditions: {
    success: true,
    data: {
      body_parts: "头部",
      duration: "2天",
      severity: "中度",
      description: "头痛伴随轻度发烧和头晕",
      other_relevant_information: ["无药物过敏", "无慢性病史"]
    }
  },

  selectClinic: {
    success: true,
    data: {
      clinic_selection: "internal_medicine_clinic"
    }
  },

  collectRequirement: {
    success: true,
    data: [
      {
        when: "在医生问诊过程中",
        what: "需要医生详细解释病情和治疗方案"
      },
      {
        when: "在医院移动过程中",
        what: "需要避开人群密集区域"
      }
    ]
  },

  patchRoute: {
    success: true,
    data: {
      patches: [
        {
          type: "insert",
          previous: "registration_center",
          this: "elevator",
          next: "internal_medicine_clinic"
        }
      ]
    }
  }
}

// Helper to simulate API delay
const simulateApiDelay = (ms = 1000) => {
  return new Promise(resolve => setTimeout(resolve, ms))
}

// Mock API store
class MockApiStore {
  constructor() {
    this.isLoading = false
    this.error = null
  }

  async collectConditions(userInput) {
    console.log(`[Mock API] collectConditions called with: "${userInput}"`)
    this.isLoading = true

    await simulateApiDelay()
    this.isLoading = false

    return MOCK_RESPONSES.collectConditions
  }

  async selectClinic(conditions) {
    console.log('[Mock API] selectClinic called with:', conditions)
    this.isLoading = true

    await simulateApiDelay()
    this.isLoading = false

    return MOCK_RESPONSES.selectClinic
  }

  async collectRequirement(userInput) {
    console.log(`[Mock API] collectRequirement called with: "${userInput}"`)
    this.isLoading = true

    await simulateApiDelay()
    this.isLoading = false

    return MOCK_RESPONSES.collectRequirement
  }

  async patchRoute(clinicId, requirements, originRoute) {
    console.log('[Mock API] patchRoute called with:', {
      clinicId,
      requirements,
      originRoute
    })
    this.isLoading = true

    await simulateApiDelay()
    this.isLoading = false

    return MOCK_RESPONSES.patchRoute
  }
}

// Demo workflow
async function runWorkflowDemo() {
  console.log('🎬 Starting Workflow Demo...')
  console.log('='.repeat(50))

  const apiStore = new MockApiStore()

  // Simulate user interactions
  console.log('📝 Phase 1: Collecting Conditions')
  console.log('User input: "我头痛已经两天了，有点发烧，感觉头晕"')

  const conditionsResp = await apiStore.collectConditions('我头痛已经两天了，有点发烧，感觉头晕')
  console.log('Conditions collected:', conditionsResp.data)

  console.log('\n🩺 Phase 2: Selecting Clinic')
  const clinicResp = await apiStore.selectClinic(conditionsResp.data)
  console.log('Clinic selected:', clinicResp.data.clinic_selection)

  // Generate original route
  const clinicId = clinicResp.data.clinic_selection
  const originalRoute = [
    { this: 'entrance', next: 'registration_center' },
    { this: 'registration_center', next: clinicId },
    { this: clinicId, next: 'pharmacy' },
    { this: 'pharmacy', next: 'exit' }
  ]
  console.log('Original route generated:', originalRoute)

  console.log('\n🎯 Phase 3: Collecting Requirements')
  console.log('User input: "我需要轮椅，希望避开人群多的区域"')

  const reqResp = await apiStore.collectRequirement('我需要轮椅，希望避开人群多的区域')
  console.log('Requirements collected:', reqResp.data)

  console.log('\n🔄 Phase 4: Patching Route')
  const patchResp = await apiStore.patchRoute(clinicId, reqResp.data, originalRoute)
  console.log('Route patches:', patchResp.data.patches)

  // Apply patches
  const modifiedRoute = applyPatches(originalRoute, patchResp.data.patches)
  console.log('Modified route:', modifiedRoute)

  console.log('\n✅ Phase 5: Workflow Completed')
  console.log('Final route display:')
  console.log(formatRouteForDisplay(modifiedRoute))

  console.log('\n' + '='.repeat(50))
  console.log('🎉 Workflow Demo Completed Successfully!')
}

// Route utility functions (simplified)
function applyPatches(originalRoute, patches) {
  if (!patches || patches.length === 0) return [...originalRoute]

  let route = [...originalRoute]

  // Apply delete patches first
  const deletePatches = patches.filter(p => p.type === 'delete')
  const insertPatches = patches.filter(p => p.type === 'insert')

  // Simple implementation for demo
  if (insertPatches.length > 0) {
    // Insert elevator between registration_center and clinic
    const insertIndex = route.findIndex(link => link.this === 'registration_center')
    if (insertIndex !== -1) {
      route.splice(insertIndex + 1, 0, { this: 'elevator', next: route[insertIndex + 1].this })
      route[insertIndex].next = 'elevator'
    }
  }

  return route
}

function formatRouteForDisplay(route) {
  const steps = [`从 ${route[0].this} 出发`]

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

// Run demo if loaded in browser
if (typeof window !== 'undefined') {
  window.runWorkflowDemo = runWorkflowDemo
  console.log('📋 Workflow demo available: runWorkflowDemo()')
  console.log('Use this function in browser console to test the workflow logic.')
}

export { runWorkflowDemo, MockApiStore }