import { ref } from 'vue'

type UseAsyncDataReturn = Awaited<ReturnType<typeof useAsyncData>>
export type UpdateStatus = UseAsyncDataReturn['status']['value']

export const useUpdateStatusRef = () => {
  const statusRef = ref<UpdateStatus>('idle')
  return statusRef
}

export const useUpdateStatusErrorRef = () => {
  const errorRef = ref<string | undefined>(undefined)
  return errorRef
}
