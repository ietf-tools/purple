<template>
  <div class="flex flex-col h-full bg-white dark:bg-gray-800">
    <div class="flex-shrink-0 px-4 py-6 sm:px-6">
      <div class="flex items-start justify-between space-x-3">
        <div class="space-y-1">
          <h2 class="text-lg font-medium text-gray-900 dark:text-white">
            Delete RFC Number
          </h2>
          <p class="text-sm text-gray-500 dark:text-gray-400">
            Are you sure you want to delete RFC {{ rfcNumber }} from the unusable numbers list?
          </p>
        </div>
      </div>
    </div>

    <div class="flex-shrink-0 px-4 py-6 sm:px-6">
      <div class="flex justify-end space-x-3">
        <BaseButton
          type="button"
          variant="secondary"
          @click="$emit('close')"
          :disabled="isDeleting"
        >
          Cancel
        </BaseButton>
        <BaseButton
          type="button"
          variant="danger"
          :disabled="isDeleting"
          @click="deleteRfcNumber"
        >
          {{ isDeleting ? 'Deleting...' : 'Delete RFC Number' }}
        </BaseButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { snackbarForErrors } from "~/utils/snackbar"

type Props = {
  rfcNumber: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
  success: []
  close: []
}>()

const api = useApi()
const snackbar = useSnackbar()

const isDeleting = ref(false)

const deleteRfcNumber = async () => {
  try {
    isDeleting.value = true

    await api.unusableRfcNumbersDestroy({
      number: props.rfcNumber
    })

    snackbar.add({
      type: 'success',
      title: `RFC ${props.rfcNumber} removed from unusable numbers`,
      text: ''
    })

    emit('success')
    emit('close')

  } catch (e: unknown) {
    snackbarForErrors({
      snackbar,
      defaultTitle: 'Unable to delete RFC number',
      error: e
    })
  } finally {
    isDeleting.value = false
  }
}
</script>
