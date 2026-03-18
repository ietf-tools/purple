<template>
  <div>
    <DialogRoot v-model:open="isOpenDependencyModal">
      <DialogPortal>
        <DialogOverlay class="bg-black/50 fixed inset-0 z-50" />
        <DialogContent
          class="fixed top-[50%] left-[50%] max-h-[85vh] w-[90vw] max-w-[450px] translate-x-[-50%] translate-y-[-50%] rounded-md bg-white p-5 shadow-xl focus:outline-none z-[100]">
          <DialogTitle class="text-md font-bold mb-4">
            New Document Reference
          </DialogTitle>

          <DialogFieldText
            v-model="searchQuery"
            label="Search target draft"
            id="targetDraftSearch"
          />

          <p class="mt-2 text-xs text-gray-500">Enter at least 5 characters.</p>

          <div v-if="searchQuery.trim().length >= MIN_SEARCH_LENGTH" class="mt-3 max-h-48 overflow-y-auto rounded-md border border-gray-200">
            <div v-if="searchLoading" class="px-3 py-2 text-sm text-gray-500">Searching...</div>
            <ul v-else-if="searchMatches.length" class="divide-y divide-gray-100">
              <li v-for="doc in searchMatches" :key="doc.id">
                <button
                  type="button"
                  class="w-full px-3 py-2 text-left hover:bg-gray-50"
                  @click="selectResult(doc.name)"
                >
                  <div class="text-sm font-medium text-gray-900">{{ doc.name }}</div>
                  <div v-if="doc.title" class="truncate text-xs text-gray-600">{{ doc.title }}</div>
                </button>
              </li>
            </ul>
            <div v-else class="p-2">
              <button
                type="button"
                class="w-full rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-left text-sm text-amber-800 hover:bg-amber-100"
                @click="selectNotReceived()"
              >
                Enter draft as not-received: {{ searchQuery.trim() }}
              </button>
            </div>
          </div>

          <p v-if="selectedResultName" class="mt-3 text-sm text-gray-700">
            Selected {{ selectedResultName }}. This will be added as refqueue.
          </p>
          <p v-else-if="useNotReceived" class="mt-3 text-sm text-gray-700">
            Selected {{ searchQuery.trim() }}. This will be added as not-received.
          </p>

          <div class="mt-[25px] flex justify-end">
            <BaseButton btn-type="default" :disabled="!canSubmit" @click="addDependencyItem"
              class="text-sm hover:bg-green5 inline-flex h-[35px] items-center justify-center rounded-lg px-[15px] font-semibold leading-none focus:shadow-[0_0_0_2px] focus:outline-none">
              {{ submitButtonLabel }}
            </BaseButton>
          </div>
          <DialogClose
            class="text-gray-700 absolute top-3 right-3 inline-flex p-2 appearance-none items-center justify-center rounded-full hover:bg-gray-200"
            aria-label="Close">
            <Icon name="uil:times" class="h-6 w-6" aria-hidden="true" />
          </DialogClose>
        </DialogContent>
      </DialogPortal>
    </DialogRoot>
  </div>
</template>

<script setup lang="ts">
import {
  DialogClose,
  DialogContent,
  DialogOverlay,
  DialogPortal,
  DialogRoot,
  DialogTitle,
} from "reka-ui"
import { refDebounced } from "@vueuse/core"
import type { DocumentsRelatedCreateRequest, RpcRelatedDocument } from "~/purple_client"
import { snackbarForErrors } from "~/utils/snackbar"

const relatedDocuments = defineModel<RpcRelatedDocument[]>('relatedDocuments', { required: true, default: [] })

const isOpenDependencyModal = defineModel<boolean>('isOpenDependencyModal', { required: true })

type Props = {
  draftName: string
  id: number,
}

const props = defineProps<Props>()

const api = useApi()

const MIN_SEARCH_LENGTH = 5

const searchQuery = ref("")
const searchLoading = ref(false)
const searchResults = ref<any>()
const selectedResultName = ref("")
const useNotReceived = ref(false)

const snackbar = useSnackbar()

const searchMatches = computed(() => {
  if (!searchResults.value) return []
  if (Array.isArray(searchResults.value)) return searchResults.value
  if (Array.isArray(searchResults.value.results)) return searchResults.value.results
  return []
})

const debouncedSearch = refDebounced(searchQuery, 250)
let previousAbortController: AbortController | undefined

watch(debouncedSearch, async (q) => {
  if (previousAbortController) {
    previousAbortController.abort()
  }

  selectedResultName.value = ""
  useNotReceived.value = false

  const trimmed = q.trim()
  if (trimmed.length < MIN_SEARCH_LENGTH) {
    searchResults.value = undefined
    return
  }

  previousAbortController = new AbortController()
  searchLoading.value = true
  try {
    searchResults.value = await api.documentsSearch(
      { q: trimmed },
      { signal: previousAbortController.signal }
    )
  } catch {
    // Ignore aborted and transient search failures.
  } finally {
    searchLoading.value = false
  }
})

const relationship = computed(() => {
  if (selectedResultName.value) return "refqueue"
  if (useNotReceived.value) return "not-received"
  return ""
})

const targetDraftName = computed(() => {
  if (selectedResultName.value) return selectedResultName.value
  if (useNotReceived.value) return searchQuery.value.trim()
  return ""
})

const canSubmit = computed(() => Boolean(relationship.value && targetDraftName.value))

const submitButtonLabel = computed(() => {
  if (relationship.value === "refqueue") return "Add as refqueue"
  if (relationship.value === "not-received") return "Add as not-received"
  return "Select relation option"
})

const selectResult = (name: string) => {
  selectedResultName.value = name
  useNotReceived.value = false
}

const selectNotReceived = () => {
  if (searchQuery.value.trim().length < MIN_SEARCH_LENGTH) return
  selectedResultName.value = ""
  useNotReceived.value = true
}

const addDependencyItem = async () => {
  if (!canSubmit.value) return

  const createArg: DocumentsRelatedCreateRequest = {
    draftName: props.draftName,
    createRpcRelatedDocumentRequest: {
      source: props.id,
      relationship: relationship.value,
      targetDraftName: targetDraftName.value
    }
  }
  try {
    const newRpcRelatedDocument = await api.documentsRelatedCreate(createArg)
    relatedDocuments.value = [...relatedDocuments.value, newRpcRelatedDocument]
    snackbar.add({
      type: 'success',
      title: 'Document reference added',
      text: ''
    })
    // reset form
    isOpenDependencyModal.value = false
    searchQuery.value = ''
    selectedResultName.value = ''
    useNotReceived.value = false
    searchResults.value = undefined
  } catch (e: unknown) {
    snackbarForErrors({
      snackbar,
      defaultTitle: `Unable to add document reference`,
      error: e
    })
  }
}

</script>
