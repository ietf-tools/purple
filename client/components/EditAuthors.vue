<template>
  <div class="border-5 border-gray-700 text-gray-500">
    <h2 class="font-bold">Authors (drag to reorder)</h2>
    <ul ref="parent" class="block">
      <li class="flex items-center justify-between pl-4 pr-1 py-1 mt-1 border rounded-md border-gray-400" v-for="(author, index) in draft.authors" :index="index" :key="author.id">
        <span class="cursor-ns-resize">{{ author.titlepageName }}</span>
        <button type="button" @click="handleRemoveAuthor(index)" class="border-1 cursor-not-allowed border-gray-500 rounded px-2 py-1 hover:bg-gray-200 focus:bg-gray-200">&times;</button>
      </li>
    </ul>
    <EditAuthorsAdd v-model="draft" />
  </div>
</template>

<script setup lang="ts">
import { useDragAndDrop } from "fluid-dnd/vue";
import type { CookedDraft } from "~/utilities/rpc";

type Props = {
  draftName: string
}

const props = defineProps<Props>()

const draft = defineModel<CookedDraft>({ required: true })

const api = useApi()

const handleRemoveAuthor = async (index: number) => {
  const draftName = draft.value.name
  if (draftName === undefined) {
    throw Error(`Expected draft to have name but was "${draftName}"`)
  }

  draft.value.authors.splice(index, 1)
  // FIXME: remove author API
  alert('Remove author API update not implemented yet')
}

const authorsRef = ref(draft.value.authors)

const [ parent ] = useDragAndDrop(authorsRef);

watch(() => draft.value?.authors, () => {
  const newAuthors = draft.value?.authors
  if(!newAuthors) return

  const authorIds = newAuthors
    .map(author => author.id)
    .filter(maybeId => maybeId !== undefined)

  api.documentsAuthorsOrder({
    draftName: props.draftName,
    authorOrder: {
      order: authorIds
    }
  })
},
  { deep: true }
)


</script>
