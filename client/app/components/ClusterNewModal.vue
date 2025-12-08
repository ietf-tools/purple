<template>
  <div class="flex flex-col h-full bg-white dark:bg-gray-800">
    <div class="flex-shrink-0 px-6 py-6 sm:px-8">
      <div class="space-y-6">
        <div class="space-y-2">
          <h2 class="text-lg font-medium text-gray-900 dark:text-white">
            New Cluster
          </h2>
          <BaseButton btnType="cancel" class="absolute right-2 top-2 p-2 flex items-center" @click="closeModal">
            <Icon name="uil:times" class="h-5 w-5" aria-hidden="true" />
          </BaseButton>
        </div>

        <form @submit.prevent="handleAddCluster" class="space-y-6">
          <div>
            <label for="cluster-number" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Cluster Number *
            </label>
            <input id="cluster-number" v-model="newClusterNumberRef" type="number" required min="1"
              placeholder="Enter cluster number"
              class="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              :disabled="isSubmitting" />
          </div>

          <div class="flex justify-end space-x-3 pt-6">
            <BaseButton type="submit" :disabled="isSubmitting">
              {{ isSubmitting ? 'Adding...' : 'Add Cluster' }}
            </BaseButton>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { overlayModalKey } from '~/providers/providerKeys';


type Props = {
  lastClusterNumber: number
  onSuccess: () => Promise<void>
}

const props = defineProps<Props>()

const snackbar = useSnackbar()

const overlayModal = inject(overlayModalKey)

if (!overlayModal) {
  snackbar.add({
    type: 'error',
    title: "Expected modal features to be available",
    text: 'See console',
  })
  throw Error('Injection of modal not available')
}

const api = useApi()

const newClusterNumberRef = ref<number | null>(props.lastClusterNumber + 1)
const isSubmitting = ref(false)

const closeModal = async () => {
  const { closeOverlayModal } = overlayModal
  closeOverlayModal()
}

const handleAddCluster = async () => {
  const { value: newClusterNumber } = newClusterNumberRef
  if(newClusterNumber === null) {
    snackbar.add({
      type: 'error',
      title: `A number is required`,
      text: ''
    })
    return
  }

  try {
    isSubmitting.value = true

    await api.clustersCreate({
      clusterRequest: {
        number: newClusterNumber
      }
    })

    snackbar.add({
      type: 'success',
      title: `Cluster ${newClusterNumber} added`,
      text: ''
    })

    await props.onSuccess()
    closeModal()
  } catch (error) {
    snackbarForErrors({
      snackbar,
      defaultTitle: 'Unable to add cluster',
      error,
    })
    console.error(error)
  } finally {
    isSubmitting.value = false
  }
}
</script>
