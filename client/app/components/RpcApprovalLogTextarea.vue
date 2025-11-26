<!-- based on https://tailwindui.com/components/application-ui/forms/textareas#component-784309f82e9913989c2196a2d47eff4a -->
<template>
  <div class="flex items-start space-x-4">
    <div class="flex-shrink-0">
      <Icon name="mdi:comment-text-outline" class="mr-1" />
    </div>
    <div class="min-w-0 flex-1">
      <form action="#" class="relative" @submit.prevent="handleSubmit">
        <div
          class="overflow-hidden rounded-lg shadow-sm ring-1 ring-inset ring-gray-300 focus-within:ring-2 focus-within:ring-indigo-600"
        >
          <label for="approvalLog" class="sr-only">Add your approval log</label>
          <textarea
            v-model="logMessage"
            rows="3"
            name="approvalLog"
            id="approvalLog"
            class="block w-full resize-none border-0 bg-transparent py-1.5 text-gray-900 placeholder:text-gray-400 focus:ring-0 sm:text-sm sm:leading-6"
            placeholder="Add your approval log..."
          />
          <!-- Spacer element to match the height of the toolbar -->
          <div class="py-2" aria-hidden="true">
            <!-- Matches height of button in toolbar (1px border + 36px content height) -->
            <div class="py-px">
              <div class="h-9" />
            </div>
          </div>
        </div>

        <div
          class="absolute inset-x-0 bottom-0 flex justify-end py-2 pl-3 pr-2"
        >
          <button
            type="submit"
            class="inline-flex items-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
            :disabled="isSubmitting"
          >
            <Icon
              v-if="isSubmitting"
              name="ei:spinner-3"
              size="1.1em"
              class="animate-spin mr-1"
            />
            Add Approval Log (public)
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { localStorageWrapper } from '~/utils/localstorage'
import { snackbarForErrors } from '~/utils/snackbar'

type Props = {
  draftName: string
  reload: () => void
}

const props = defineProps<Props>()

const api = useApi()

const logMessage = ref('')

const localStorageKey = computed(() => `rpc:saved-approval-log-${props.draftName}`)

onMounted(() => {
  const val = localStorageWrapper.getItem(localStorageKey.value)
  if (typeof val === 'string') {
    logMessage.value = `${
      logMessage.value // preserve any value typed before restoring value
    }${val}`
  }
})

watch(logMessage, () => {
  localStorageWrapper.setItem(localStorageKey.value, logMessage.value)
})

const isSubmitting = ref(false)

const snackbar = useSnackbar()

const handleSubmit = async () => {
  try {
    isSubmitting.value = true
    await api.documentsApprovalLogsCreate({
      draftName: props.draftName,
      approvalLogMessageRequest: {
        logMessage: logMessage.value
      }
    })
    // assume approval log was successfully created so clean up local state
    isSubmitting.value = false
    clearLocalStorage()
    logMessage.value = ''
    props.reload()
  } catch (error: unknown) {
    isSubmitting.value = false
    // server can respond with validation errors that we should show users
    snackbarForErrors({ snackbar, defaultTitle: 'Adding approval log message failed', error })
  }
}

const clearLocalStorage = () =>
  localStorageWrapper.removeItem(localStorageKey.value)
</script>
