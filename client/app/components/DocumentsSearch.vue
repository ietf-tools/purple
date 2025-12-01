<template>
  <div class="flex flex-row items-center">
    <label class="text-gray-900 w-[160px] text-right text-sm font-bold mr-1" :for="props.id"> {{ props.label }}:</label>
    <ComboboxRoot v-model="selectedRfcToBe" class="relative">
      <ComboboxAnchor
        class="inline-flex items-center justify-between rounded-lg border border-gray-500 px-1 py-1 leading-none gap-[5px] bg-white focus:shadow-[0_0_0_2px] focus:shadow-black outline-none"
      >
        <span v-if="selectedRfcToBe" class="flex flex-row bg-gray-100 text-xs rounded-lg px-2 py-0.5 shadow-md border-1 border-gray-500 items-center gap-1 px-1">
          <b>{{ selectedRfcToBe.name }}</b>
          <span>{{ ` #${selectedRfcToBe.name}` }}</span>
          <button type="button" class="rounded-lg bg-gray-200 focus:bg-gray-300 hover:bg-gray-300 p-0.5 text-black border-none" @click="handleClearSelectedAuthor" :label="`Unselect document ${selectedRfcToBe.name} #${selectedRfcToBe.rfcNumber}`">&times;</button>
        </span>
        <ComboboxInput v-model="inputRef" :id="props.id" class="outline-none text-sm py-1 border-none h-full placeholder-gray-400" :placeholder="selectedRfcToBe?.name ? `Change RFC...` : `Search RFC`" />
      </ComboboxAnchor>

      <ComboboxContent
        class="absolute z-10 w-full mt-1 min-w-[160px] bg-white overflow-hidden rounded-lg shadow-sm border shadow-xl">
        <ComboboxViewport class="p-[5px]">
          <ComboboxEmpty class="text-mauve8 text-xs font-medium text-center py-2">
            (no matches)
          </ComboboxEmpty>
          <ComboboxItem
            v-if="searchResults"
            v-for="searchResult in searchResults.results"
            :key="searchResult.personId"
            :value="searchResult"
            class="text-xs leading-none rounded-[3px] flex items-center h-[25px] pr-[35px] pl-[25px] relative select-none data-[highlighted]:outline-none data-[highlighted]:bg-gray-100 data-[highlighted]:text-black"
          >
            <span class="font-bold">
              {{ searchResult.name }}
            </span>
            <span class="font-normal ml-1" v-if="searchResult.personId">
              {{ SPACE }}{{ ` #${searchResult.personId}` }}
            </span>
          </ComboboxItem>
        </ComboboxViewport>
      </ComboboxContent>
    </ComboboxRoot>
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
import type { RfcToBe } from "~/purple_client"
import { SPACE } from '../utils/strings'

type Props = {
  id: string
  label: string
}

const props = defineProps<Props>()

const selectedRfcToBe = defineModel<RfcToBe | undefined>()

const api = useApi()

type SearchDatatrackerpersonsResponse = Awaited<ReturnType<typeof api.searchDatatrackerpersons>>

const searchResults = ref<SearchDatatrackerpersonsResponse>()

const handleClearSelectedAuthor = () => {
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

    searchResults.value = await api.searchDatatrackerpersons({
      search: debouncedInputRef.value
    },
      { signal: previousAbortController.signal }
    )
  })
</script>
