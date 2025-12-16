<template>
  <ComboboxRoot v-model="selectedAuthor" class="relative">
    <ComboboxAnchor
      class="mt-3 inline-flex items-center justify-between rounded-lg border border-gray-500 px-1 py-1 text-xs leading-none gap-[5px] bg-white text-grass11 hover:bg-stone-50 shadow-sm focus:shadow-[0_0_0_2px] focus:shadow-black data-[placeholder]:text-grass9 outline-none"
    >
      <ComboboxInput
        v-model="inputRef"
        class="outline-none text-sm py-1 border-none h-full placeholder-gray-400"
        placeholder="Search authors to add..."
      />
    </ComboboxAnchor>

    <ComboboxContent
      class="absolute z-10 w-full mt-1 min-w-[160px] bg-white overflow-hidden rounded-lg shadow-sm border shadow-xl"
    >
      <ComboboxViewport class="p-[5px]">
        <ComboboxEmpty
          class="text-mauve8 text-xs font-medium text-center py-2"
        >
        (no matches)
      </ComboboxEmpty>
        <ComboboxItem
          v-if="searchResults"
          v-for="searchResult in searchResults.results"
          :key="searchResult.personId"
          :value="searchResult"
          class="text-xs leading-none text-grass11 rounded-[3px] flex items-center h-[25px] pr-[35px] pl-[25px] relative select-none data-[highlighted]:outline-none data-[highlighted]:bg-gray-100 data-[highlighted]:text-black"
        >
          <span class="font-bold">
            {{ searchResult.name }}
          </span>
          <span class="font-normal ml-1" v-if="searchResult.personId">
            {{ SPACE }}{{ ` #${searchResult.email ?? ''}` }}
          </span>
        </ComboboxItem>
      </ComboboxViewport>
    </ComboboxContent>
  </ComboboxRoot>
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
import type { RfcToBe, BaseDatatrackerPerson } from "~/purple_client"
import { snackbarForErrors } from "~/utils/snackbar"

const draft = defineModel<CookedDraft | RfcToBe>({ required: true })

const selectedAuthor = ref<BaseDatatrackerPerson | undefined>()

const snackbar = useSnackbar()

const api = useApi()

watch(selectedAuthor, async () => {
  if(selectedAuthor.value) {
    const draftName = draft.value.name
    if(draftName === undefined) {
      throw Error(`Expected draft to have name but was ${draft.value.name}`)
    }
    const { value } = selectedAuthor

    try {
      const rpcAuthor = await api.documentsAuthorsCreate({
        draftName,
        createRfcAuthorRequest: {
          titlepageName: value.name ?? `(no name)`,
          personId: value.personId,
        }
      })
      draft.value.authors.push(rpcAuthor)
    } catch (e: unknown) {
      snackbarForErrors({
        snackbar,
        defaultTitle: `Unable to add author "${value.name}" (${value.email ?? ''}) to draft "${draft.value.name}"`,
        error: e
      })
    }
  }
  selectedAuthor.value = undefined
})

type SearchDatatrackerpersonsResponse = Awaited<ReturnType<typeof api.searchDatatrackerpersons>>

const searchResults = ref<SearchDatatrackerpersonsResponse>()

const inputRef = ref('');

const debouncedInputRef = refDebounced(inputRef, 100);

let previousAbortController: AbortController | undefined;

watch(
  debouncedInputRef,
  async () => {
    if(previousAbortController) {
      // abort any fetches in flight to prevent race conditions
      previousAbortController.abort();
    }

    previousAbortController = new AbortController();

    searchResults.value = await api.searchDatatrackerpersons({
      search: debouncedInputRef.value
    },
      { signal: previousAbortController.signal }
    )
  });

</script>
