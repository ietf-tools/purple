<template>
  <ComboboxRoot v-model="selectedAuthor" class="relative">
    <ComboboxAnchor
      class="mt-3 inline-flex items-center justify-between rounded-lg border border-gray-500 px-1 py-1 text-xs leading-none gap-[5px] bg-white text-grass11 hover:bg-stone-50 shadow-sm focus:shadow-[0_0_0_2px] focus:shadow-black data-[placeholder]:text-grass9 outline-none"
    >
      <ComboboxInput
        v-model="inputRef"
        class="outline-none border-none h-full placeholder-gray-400"
        placeholder="Search authors to add..."
      />
      <ComboboxTrigger class="px-2">
        <Icon name="fluent:chevron-down-12-filled" />
      </ComboboxTrigger>
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
          v-for="(searchResult, index) in searchResults"
          :key="searchResult.id"
          :value="searchResult"
          class="text-xs leading-none text-grass11 rounded-[3px] flex items-center h-[25px] pr-[35px] pl-[25px] relative select-none data-[highlighted]:outline-none data-[highlighted]:bg-gray-100 data-[highlighted]:text-black"
        >
          <span>
            {{ searchResult.titlepageName }}
          </span>
        </ComboboxItem>
      </ComboboxViewport>
    </ComboboxContent>
  </ComboboxRoot>
</template>

<script setup lang="ts">
import { refDebounced } from "@vueuse/core";
import {
  ComboboxAnchor,
  ComboboxContent,
  ComboboxInput,
  ComboboxItem,
  ComboboxRoot,
  ComboboxTrigger,
  ComboboxViewport,
} from "reka-ui";
import type { RfcAuthor } from "~/purple_client";

type Props = {};

const props = defineProps<Props>();

const authors = defineModel<RfcAuthor[]>('authors', { required: true })

const selectedAuthor = ref<RfcAuthor | undefined>()

const snackbar = useSnackbar()

watch(selectedAuthor, () => {
  if(selectedAuthor.value) {
    const { value } = selectedAuthor
    if(!authors.value.find(author => author.id === value.id)) {
      authors.value.push(selectedAuthor.value)
    } else {
      snackbar.add({
        type: 'error',
        title: `${selectedAuthor.value.titlepageName} already added`,
        text: ''
      })
    }
  }
  selectedAuthor.value = undefined
})

const api = useApi();

const searchResults = ref<RfcAuthor[]>([])

const mockDatatrackerPersonSearch = async (props: {
  query: string;
  page: number;
}, initOverrides?: Parameters<typeof api.assignmentsCreate>[1]): Promise<RfcAuthor[]> => {
  // TODO replace this mock with API usage
  const allAuthors = [
    {
      id: 5,
      titlepageName: 'Bobby',
      isEditor: true,
      datatrackerPerson: 105,
    },
    {
      id: 6,
      titlepageName: 'Billy',
      isEditor: true,
      datatrackerPerson: 106,
    },
    {
      id: 7,
      titlepageName: 'Boxy',
      isEditor: true,
      datatrackerPerson: 107,
    }
  ]

  return allAuthors.filter(author => JSON.stringify(author).toLowerCase().includes(props.query.toLowerCase()))
}

type PurpleApiExtension = typeof api & {
  datatrackerPersonSearch: typeof mockDatatrackerPersonSearch;
};

const apiWithExtension = (function(){
  (api as PurpleApiExtension).datatrackerPersonSearch = mockDatatrackerPersonSearch;
  return api as PurpleApiExtension
})()

const inputRef = ref("");

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

    searchResults.value = await apiWithExtension.datatrackerPersonSearch(
      { query: debouncedInputRef.value, page: 0 },
      { signal: previousAbortController.signal }
    )
  });

</script>
