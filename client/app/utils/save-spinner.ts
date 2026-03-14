import { ref } from 'vue'

type UseAsyncDataReturn = Awaited<ReturnType<typeof useAsyncData>>
export type SaveStatus = UseAsyncDataReturn['status']['value']
export type SaveStatusError = string | undefined

export const useSaveStatusRef = () => ref<SaveStatus>('idle')

export const useSaveStatusErrorRef = () => ref<SaveStatusError>(undefined)

/**
 * Optional helper function to handle updating save status refs.
 * Expects async function that will complete, or throw for errors.
 */
export const wrapSaveUpdateFn = async (fn: () => Promise<unknown>, saveStatusRef: Ref<SaveStatus>, saveStatusErrorRef: Ref<SaveStatusError>) => {
  saveStatusRef.value = 'pending'
  try {
    await fn()
    saveStatusRef.value = 'success'
  } catch (e) {
    saveStatusRef.value = 'error'
    saveStatusErrorRef.value = String(e)
  }
}
