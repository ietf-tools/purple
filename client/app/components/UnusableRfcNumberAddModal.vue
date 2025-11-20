<template>
  <div class="flex flex-col h-full bg-white dark:bg-gray-800">
    <div class="flex-shrink-0 px-6 py-6 sm:px-8">
      <div class="space-y-6">
        <div class="space-y-2">
          <h2 class="text-lg font-medium text-gray-900 dark:text-white">
            Add Unusable RFC Number
          </h2>
          <p class="text-sm text-gray-500 dark:text-gray-400">
            Reserve an RFC number to make it unavailable for assignment.
          </p>
        </div>

        <form @submit.prevent="addUnusableRfcNumber" class="space-y-6">
          <div>
            <label for="rfc-number" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
              RFC Number *
            </label>
            <input
              id="rfc-number"
              v-model="newRfcNumber"
              type="number"
              required
              min="1"
              placeholder="Enter RFC number"
              class="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              :disabled="isSubmitting"
            />
          </div>

          <div>
            <label for="comment" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Comment
            </label>
            <textarea
              id="comment"
              v-model="newComment"
              rows="6"
              placeholder="Enter reason for making this RFC number unusable..."
              class="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white resize-y"
              :disabled="isSubmitting"
            />
          </div>

          <div class="flex justify-end space-x-3 pt-6">
            <BaseButton
              type="button"
              variant="secondary"
              @click="$emit('close')"
              :disabled="isSubmitting"
            >
              Cancel
            </BaseButton>
            <BaseButton
              type="submit"
              :disabled="isSubmitting || !newRfcNumber"
            >
              {{ isSubmitting ? 'Adding...' : 'Add Number' }}
            </BaseButton>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">

const emit = defineEmits<{
  success: []
  close: []
}>()

const api = useApi()
const snackbar = useSnackbar()

const newRfcNumber = ref<number | null>(null)
const newComment = ref('')
const isSubmitting = ref(false)

const addUnusableRfcNumber = async () => {
  if (!newRfcNumber.value) return

  try {
    isSubmitting.value = true

    await api.unusableRfcNumbersCreate({
      unusableRfcNumberRequest: {
        number: newRfcNumber.value,
        comment: newComment.value || ''
      }
    })

    snackbar.add({
      type: 'success',
      title: `RFC ${newRfcNumber.value} added to unusable numbers`,
      text: ''
    })

    emit('success')
    emit('close')

  } catch (e) {
    snackbarForErrors({
      snackbar,
      defaultTitle: 'Unable to add RFC number',
      error: e
    })
    console.error(e)
  } finally {
    isSubmitting.value = false
  }
}
</script>
