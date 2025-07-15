<template>
  <div>
    <DialogRoot v-model:open="isOpenDependencyModal">
      <DialogTrigger
        class="text-gray-100 font-semibold hover:bg-mauve3 inline-flex h-[35px] items-center justify-center rounded-md bg-white px-[15px] leading-none shadow-sm focus:shadow-[0_0_0_2px] focus:shadow-black dark:focus:shadow-green8 focus:outline-none border">
        Add document reference
      </DialogTrigger>
      <DialogPortal>
        <DialogOverlay class="bg-black/50 data-[state=open]:animate-overlayShow fixed inset-0 z-30" />
        <DialogContent
          class="data-[state=open]:animate-contentShow fixed top-[50%] left-[50%] max-h-[85vh] w-[90vw] max-w-[450px] translate-x-[-50%] translate-y-[-50%] rounded-[6px] bg-white p-[25px] shadow-[hsl(206_22%_7%_/_35%)_0px_10px_38px_-10px,_hsl(206_22%_7%_/_20%)_0px_10px_20px_-15px] focus:outline-none z-[100]">
          <DialogTitle class="m-0 text-[17px] font-semibold">
            New Document Reference
          </DialogTitle>
          <DialogDescription class="mt-[10px] mb-5 text-sm leading-normal">
            Make changes to your profile here. Click save when you're done.
          </DialogDescription>

          <ComboboxRoot v-model="selectedDraft" class="relative">
            <ComboboxAnchor
              class="mt-3 inline-flex items-center justify-between rounded-lg border border-gray-500 px-1 py-1 text-xs leading-none gap-[5px] shadow-sm focus:shadow-[0_0_0_2px] focus:shadow-black outline-none"
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
                  class="text-xs font-medium text-center py-2"
                >
                (no matches)
              </ComboboxEmpty>
                <ComboboxItem
                  v-if="searchResults"
                  v-for="searchResult in searchResults.results"
                  :key="searchResult.personId"
                  :value="searchResult"
                  class="text-xs leading-none rounded-[3px] flex items-center h-[25px] pr-[35px] pl-[25px] relative select-none data-[highlighted]:outline-none data-[highlighted]:bg-gray-100 data-[highlighted]:text-black"
                >
                  <span>
                    {{ searchResult.name }}
                  </span>
                </ComboboxItem>
              </ComboboxViewport>
            </ComboboxContent>
          </ComboboxRoot>

          <fieldset class="mb-[15px] flex items-center gap-5">
            <label class="text-gray-900 w-[90px] text-right text-sm" for="name"> Name </label>
            <input id="name"
              class="text-gray-900 bg-stone-50 shadow-green7 focus:shadow-green8 inline-flex h-[35px] w-full flex-1 items-center justify-center rounded-lg px-[10px] text-sm leading-none shadow-[0_0_0_1px] outline-none focus:shadow-[0_0_0_2px]"
              defaultValue="Pedro Duarte">
          </fieldset>
          <fieldset class="mb-[15px] flex items-center gap-5">
            <label class="text-gray-900 w-[90px] text-right text-sm" for="username"> Username </label>
            <input id="username"
              class="text-gray-900 bg-stone-50 shadow-green7 focus:shadow-green8 inline-flex h-[35px] w-full flex-1 items-center justify-center rounded-lg px-[10px] text-sm leading-none shadow-[0_0_0_1px] outline-none focus:shadow-[0_0_0_2px]"
              defaultValue="@peduarte">
          </fieldset>
          <div class="mt-[25px] flex justify-end">
            <DialogClose as-child>
              <BaseButton btn-type="default" @click="addDependencyItem"
                class="bg-green4 text-green11 text-sm hover:bg-green5 focus:shadow-green7 inline-flex h-[35px] items-center justify-center rounded-lg px-[15px] font-semibold leading-none focus:shadow-[0_0_0_2px] focus:outline-none">
                Save changes
              </BaseButton>
            </DialogClose>
          </div>
          <DialogClose
            class="text-gray-100 hover:bg-green4 focus:shadow-green7 absolute top-[10px] right-[10px] inline-flex h-[25px] w-[25px] appearance-none items-center justify-center rounded-full focus:shadow-[0_0_0_2px] focus:outline-none"
            aria-label="Close">
            <Icon name="lucide:x" />
          </DialogClose>
        </DialogContent>
      </DialogPortal>
    </DialogRoot>
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

  DialogClose,
  DialogContent,
  DialogDescription,
  DialogOverlay,
  DialogPortal,
  DialogRoot,
  DialogTitle,
  DialogTrigger,
} from "reka-ui"
import type { DocumentsReferencesCreateRequest, RpcRelatedDocument } from "~/purple_client"
import { snackbarForErrors } from "~/utilities/snackbar"

const relatedDocuments = defineModel<RpcRelatedDocument[]>('relatedDocuments', { required: true, default: [] })

const isOpenDependencyModal = defineModel<boolean>('isOpenDependencyModal', { required: true })

const selectedDraft = ref<RpcRelatedDocument | undefined>()

const snackbar = useSnackbar()

const api = useApi()

watch(selectedDraft, async () => {
  if(!selectedDraft.value) {
    return
  }


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

    searchResults.value = await api.search({
      search: debouncedInputRef.value
    },
      { signal: previousAbortController.signal }
    )
  });

const addDependencyItem = async () => {
  const createArg: DocumentsReferencesCreateRequest = {
    draftName: "",
    rpcRelatedDocument: {
      relationship: "",
      targetDraftName: ""
    }
  }
  try {
    const newRpcRelatedDocument = await api.documentsReferencesCreate(createArg)
    relatedDocuments.value.push(newRpcRelatedDocument)
    // TODO reset form
    selectedDraft.value = undefined
  } catch (e: unknown) {
    snackbarForErrors({
      snackbar,
      defaultTitle: `Unable to add document reference "${JSON.stringify(createArg)}"`,
      error: e
    })
  }
}

</script>
