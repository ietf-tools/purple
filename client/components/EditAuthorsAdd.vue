<template>
  <ComboboxRoot v-model="props.authors" class="relative">
    <ComboboxAnchor
      class="min-w-[160px] inline-flex items-center justify-between rounded-lg border px-[15px] text-xs leading-none h-[35px] gap-[5px] bg-white text-grass11 hover:bg-stone-50 shadow-sm focus:shadow-[0_0_0_2px] focus:shadow-black data-[placeholder]:text-grass9 outline-none"
    >
      <ComboboxInput
        v-model="inputRef"
        class="!bg-transparent outline-none text-grass11 h-full selection:bg-grass5 placeholder-stone-400"
        placeholder="type name..."
      />
      <ComboboxTrigger> v </ComboboxTrigger>
    </ComboboxAnchor>

    <ComboboxContent
      class="absolute z-10 w-full mt-1 min-w-[160px] bg-white overflow-hidden rounded-lg shadow-sm border will-change-[opacity,transform] data-[side=top]:animate-slideDownAndFade data-[side=right]:animate-slideLeftAndFade data-[side=bottom]:animate-slideUpAndFade data-[side=left]:animate-slideRightAndFade"
    >
      <ComboboxViewport class="p-[5px]">
        <ComboboxEmpty
          class="text-mauve8 text-xs font-medium text-center py-2"
        />
        <ComboboxItem
          v-for="(searchResult, index) in searchResults"
          :key="searchResult.id"
          :value="searchResult.id!.toString()"
          class="text-xs leading-none text-grass11 rounded-[3px] flex items-center h-[25px] pr-[35px] pl-[25px] relative select-none data-[disabled]:text-mauve8 data-[disabled]:pointer-events-none data-[highlighted]:outline-none data-[highlighted]:bg-grass9 data-[highlighted]:text-grass1"
        >
          <ComboboxItemIndicator
            class="absolute left-0 w-[25px] inline-flex items-center justify-center"
          >
            ✓
          </ComboboxItemIndicator>
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
  ComboboxItemIndicator,
  ComboboxRoot,
  ComboboxTrigger,
  ComboboxViewport,
} from "reka-ui";
import type { RfcAuthor,  } from "~/purple_client";

type Props = {
  authors: RfcAuthor[];
};

const props = defineProps<Props>();

const api = useApi();

const searchResults = ref<RfcAuthor[]>([])

const mockDatatrackerPersonSearch = async (props: {
  query: string;
  page: number;
}, initOverrides?: Parameters<typeof api.assignmentsCreate>[1]): Promise<RfcAuthor[]> => {
  return [
    // TODO return mock responses until API available
  ]
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
