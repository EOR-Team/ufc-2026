import { defineStore } from 'pinia'
import { ref } from 'vue'

export const usePatientStore = defineStore('patient', () => {
  const info = ref(null) // { name, id, medical_records }
  const setPatient = (data) => { info.value = data }
  const clear = () => { info.value = null }
  return { info, setPatient, clear }
})
