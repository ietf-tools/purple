<template>
  <div class="flex flex-row items-center h-full mx-0 text-sm font-medium">
    <template v-if="!isEditing">
      <span v-if="person" class="flex-1">
        <a
          :href="person.email ? datatrackerLinks.personByEmail(person.email) : undefined"
          :class="ANCHOR_STYLE"
        >{{ person.name }}</a>
        <span v-if="person.email" class="text-gray-500 ml-1">({{ person.email }})</span>
      </span>
      <span v-else class="flex-1">(none)</span>
      <div v-if="!isReadOnly" class="flex gap-1">
        <button
          v-if="person"
          @click="handleRemove"
          class="text-red-600 hover:text-red-800 px-2 py-1"
        >
          <Icon name="uil:times" />
        </button>
        <button @click="startEditing" :class="[classForBtnType.outline, 'px-2 py-1']">
          <Icon name="uil:pen" />
        </button>
      </div>
    </template>
    <template v-else>
      <div class="w-full flex flex-col gap-1">
        <ComboboxRoot v-model="selected" class="relative">
          <ComboboxAnchor
            class="inline-flex items-center justify-between rounded-lg border border-gray-500 px-1 py-1 text-xs leading-none gap-[5px] bg-white hover:bg-stone-50 shadow-sm outline-none"
          >
            <ComboboxInput
              v-model="searchInput"
              class="outline-none text-sm py-1 border-none h-full placeholder-gray-400"
              placeholder="Search for person…"
              ref="inputRef"
            />
          </ComboboxAnchor>
          <ComboboxContent
            class="absolute z-10 w-full mt-1 min-w-[160px] bg-white overflow-hidden rounded-lg shadow-sm border shadow-xl"
          >
            <ComboboxViewport class="p-[5px]">
              <ComboboxEmpty class="text-mauve8 text-xs font-medium text-center py-2">
                (no matches)
              </ComboboxEmpty>
              <ComboboxItem
                v-if="searchResults"
                v-for="result in searchResults.results"
                :key="result.personId"
                :value="result"
                class="text-xs leading-none rounded-[3px] flex items-center h-[25px] pr-[35px] pl-[25px] relative select-none data-[highlighted]:outline-none data-[highlighted]:bg-gray-100 data-[highlighted]:text-black"
              >
                <span class="font-bold">{{ result.name }}</span>
                <span class="font-normal ml-1" v-if="result.personId">#{{ result.personId }}</span>
              </ComboboxItem>
            </ComboboxViewport>
          </ComboboxContent>
        </ComboboxRoot>
        <div class="flex justify-end">
          <button
            @click="isEditing = false"
            class="text-xs text-gray-500 hover:text-gray-700 underline"
          >
            Cancel
          </button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { refDebounced } from "@vueuse/core"
import {
  ComboboxAnchor,
  ComboboxContent,
  ComboboxEmpty,
  ComboboxInput,
  ComboboxItem,
  ComboboxRoot,
  ComboboxViewport,
} from "reka-ui"
import type { BaseDatatrackerPerson } from '~/purple_client'
import { ANCHOR_STYLE } from '~/utils/html'
import { classForBtnType } from '~/utils/button'
import { useDatatrackerLinks } from '~/composables/useDatatrackerLinks'

type Props = {
  person?: BaseDatatrackerPerson | null
  isReadOnly?: boolean
  onSave: (personId: number | null) => Promise<void>
}

const props = withDefaults(defineProps<Props>(), {
  isReadOnly: false,
})

const api = useApi()
const datatrackerLinks = useDatatrackerLinks()
const snackbar = useSnackbar()

const isEditing = ref(false)
const searchInput = ref('')
const inputRef = ref<HTMLElement | null>(null)
const selected = ref<BaseDatatrackerPerson | undefined>()

const debouncedInput = refDebounced(searchInput, 100)

type SearchPersonsResponse = Awaited<ReturnType<typeof api.searchDatatrackerpersons>>
const searchResults = ref<SearchPersonsResponse>()

let abortController: AbortController | undefined

watch(debouncedInput, async () => {
  abortController?.abort()
  abortController = new AbortController()
  searchResults.value = await api.searchDatatrackerpersons(
    { search: debouncedInput.value },
    { signal: abortController.signal }
  )
})

const startEditing = async () => {
  isEditing.value = true
  searchInput.value = ''
  searchResults.value = undefined
  selected.value = undefined
  await nextTick()
  inputRef.value?.focus()
}

watch(selected, async (person) => {
  if (!person) return
  try {
    await props.onSave(person.personId ?? null)
    snackbar.add({ type: 'success', text: 'Person updated successfully.' })
  } catch (e: unknown) {
    snackbar.add({ type: 'error', text: 'Failed to update person.' })
    console.error('Failed to update person:', e)
  } finally {
    isEditing.value = false
    selected.value = undefined
  }
})

const handleRemove = async () => {
  try {
    await props.onSave(null)
    snackbar.add({ type: 'success', text: 'Person removed successfully.' })
  } catch (e: unknown) {
    snackbar.add({ type: 'error', text: 'Failed to remove person.' })
    console.error('Failed to remove person:', e)
  }
}
</script>
