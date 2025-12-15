<template>
  <div v-if="allDocuments.length === 0" class="flex items-center justify-center italic pb-3">
    Loading search
    <Icon name="ei:spinner-3" size="1.3em" class="animate-spin ml-2" />
  </div>
  <div v-else :class="`flex flex-row items-center ${
  // so that the ComboboxContent is positioned against this
  'relative'}`">
    <label class="text-gray-900 dark:text-gray-200 w-[160px] text-right text-sm font-bold mr-1" :for="props.id"> {{ props.label }}:</label>
    <div>
    <ComboboxRoot v-model="selectedRfcToBe">
      <ComboboxAnchor
        class="inline-flex items-center justify-between rounded-lg border border-gray-500 px-1 py-1 leading-none gap-[5px] bg-white dark:bg-gray-700 focus:shadow-[0_0_0_2px] focus:shadow-black outline-none">
        <span v-if="selectedRfcToBe"
          class="flex flex-row bg-gray-100 text-white dark:bg-gray-500 dark:text-white text-xs rounded-lg px-2 py-0.5 shadow-md border-1 border-gray-500 items-center gap-1 px-1">
          <b>{{ selectedRfcToBe.name }}</b>
          <span v-if="selectedRfcToBe.rfcNumber">RFC {{ selectedRfcToBe.rfcNumber }}</span>
          <button type="button"
            class="rounded-lg bg-gray-200 dark:bg-gray-300 focus:bg-gray-300 hover:bg-gray-300 p-0.5 text-black border-none"
            @click="handleClearSelectedDocument"
            :label="`Unselect document ${selectedRfcToBe.name}${selectedRfcToBe.rfcNumber ? `(RFC ${selectedRfcToBe.rfcNumber})` : ''}`">&times;</button>
        </span>
        <ComboboxInput v-model="inputRef" :id="props.id" :readonly="allDocuments.length === 0"
          class="outline-none bg-white dark:bg-black text-black dark:text-white text-sm py-1 border-none h-full placeholder-gray-400 dark:placeholder-gray-200"
          :placeholder="allDocuments.length === 0 ? 'Loading search...' : selectedRfcToBe?.name ? `Change draft...` : `Search draft`" />
      </ComboboxAnchor>

      <ComboboxContent
        class="absolute left-0 top-10 z-10 w-full mt-1 min-w-[160px] max-h-[80vh] bg-white dark:bg-black overflow-y-scroll rounded-lg shadow-sm border shadow-xl">
        <ComboboxViewport class="p-[5px]">
          <ComboboxEmpty class="text-mauve8 text-xs font-medium text-center py-2">
            (no matches)
          </ComboboxEmpty>
          <ComboboxItem v-if="searchResults" v-for="(searchResult, index) in searchResults"
            :key="searchResult.id ?? index" :value="searchResult"
            class="text-xs leading-none rounded-[3px] flex items-center h-[2em] pr-[35px] pl-[25px] relative select-none data-[highlighted]:outline-none data-[highlighted]:bg-gray-100 data-[highlighted]:text-black">
            <span class="font-bold">
              {{ searchResult.name }}
            </span>
            <span class="font-normal ml-1" v-if="searchResult.rfcNumber">
              RFC {{ searchResult.rfcNumber }}
            </span>
          </ComboboxItem>
        </ComboboxViewport>
      </ComboboxContent>
    </ComboboxRoot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { refDebounced } from "@vueuse/core"
import {
  ComboboxAnchor,
  ComboboxContent,
  ComboboxInput,
  ComboboxItem,
  ComboboxRoot,
  ComboboxViewport,
} from "reka-ui"
import { type RfcToBe } from "~/purple_client"

type Props = {
  id: string
  label: string
}

const props = defineProps<Props>()

const selectedRfcToBe = defineModel<RfcToBe | undefined>()

const api = useApi()

const allDocuments = ref<RfcToBe[]>([])

onMounted(async () => {
  let limit = 50
  let offset = 0

  while (true) {
    console.log("searching...")
    const documentsList = await api.documentsList({
      limit,
      offset
    })
    offset = documentsList.results.length
    if (limit === undefined) {
      limit = documentsList.results.length
    }
    allDocuments.value.push(...documentsList.results)
    console.log("all docs length", allDocuments.value.length)
    if (documentsList.results.length > 0) {
      break
    }
  }
})

const searchResults = ref<RfcToBe[]>([])

type FakeDocSearchProps = {
  search: string
}

const fakeDocSearch = async ({ search }: FakeDocSearchProps, { }: { signal: unknown }) => {
  return allDocuments.value.filter(rfcToBe => {
    const docString = JSON.stringify(rfcToBe)
    return docString.includes(search)
  })
}

const handleClearSelectedDocument = () => {
  selectedRfcToBe.value = undefined
}

const inputRef = ref('')

const debouncedInputRef = refDebounced(inputRef, 100)

let previousAbortController: AbortController | undefined

watch(
  debouncedInputRef,
  async () => {
    if (previousAbortController) {
      // abort any fetches in flight to prevent race conditions
      previousAbortController.abort();
    }

    previousAbortController = new AbortController();

    searchResults.value = await fakeDocSearch({
      search: debouncedInputRef.value
    },
      { signal: previousAbortController.signal }
    )
  })
</script>
