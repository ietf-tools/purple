<template>
  <ComboboxRoot v-model="selectedAuthor" class="relative" :ignore-filter="true">
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
        <ComboboxGroup>
          <ComboboxItem
            v-for="searchResult in searchResults.results"
            :key="searchResult.personId"
            :value="searchResult"
            :textValue="searchResult.name"
            class="text-xs leading-none rounded-[3px] flex items-center h-[25px] pr-[35px] pl-[25px] relative select-none data-[highlighted]:outline-none data-[highlighted]:bg-gray-100 data-[highlighted]:text-black"
          >
            {{ searchResult.name }}
          </ComboboxItem>
        </ComboboxGroup>
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
import type { BaseDatatrackerPerson } from "~/purple_client"
import type { CookedDraft } from "~/utilities/rpc"
import { snackbarForErrors } from "~/utilities/snackbar"

const draft = defineModel<CookedDraft>({ required: true })

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

    const userAlreadyAdded = draft.value.authors
      .find(author => author.datatrackerPerson === value.personId)
    if(!userAlreadyAdded) {
      try {
        const rpcAuthor = await api.documentsAuthorsCreate({
          draftName,
          createRfcAuthor: {
            titlepageName: value.name ?? `(no name)`,
            personId: value.personId,
          }
        })
        draft.value.authors.push(rpcAuthor)
      } catch (e: unknown) {
        snackbarForErrors({
          snackbar,
          defaultTitle: `Unable to add author "${value.name}" #${value.personId} to draft "${draft.value.name}"`,
          error: e
        })
      }
    } else {
      snackbar.add({
        type: 'error',
        title: `Author "${selectedAuthor.value.name}" already added`,
        text: ''
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
