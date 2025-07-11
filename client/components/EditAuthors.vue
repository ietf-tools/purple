<template>
  <BaseCard>
    <template #header>
      <CardHeader title="Edit Authors drag to reorder"/>
    </template>
    <div v-if="draft.authors" class="border-5 border-gray-700 text-gray-500">
      <ul ref="parent" class="block">
        <li class="flex items-center justify-between pl-4 pr-1 py-1 mt-1 border rounded-md border-gray-400" v-for="(author, index) in draft.authors" :index="index" :key="author.id">
          <span class="flex-1 cursor-ns-resize font-bold">{{ author.titlepageName }}</span>
          <label class="border flex gap-2 items-center  border-gray-300 inline-block px-2 py-1 rounded text-sm mr-4">
            editor?
            <input type="checkbox" class="" v-model="author.isEditor"/>
          </label>
          <button type="button" @click="handleRemoveAuthor(index)" class="border-1 cursor-not-allowed border-gray-500 rounded px-2 py-1 hover:bg-gray-200 focus:bg-gray-200">&times;</button>
        </li>
      </ul>
      <EditAuthorsAdd v-model="draft" />
    </div>
  </BaseCard>
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

  const removedAuthor = draft.value.authors.splice(index, 1)

  removedAuthor.forEach(author =>
    api.documentsAuthorsDestroy({
      draftName: draftName,
      id: author.id!,
    })
  )
}

const authorsRef = ref(draft.value.authors)

const [ parent ] = useDragAndDrop(authorsRef);

watch(() => draft.value?.authors, async () => {
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

  await Promise.all(newAuthors.map(author =>
    api.documentsAuthorsPartialUpdate({
      draftName: props.draftName,
      id: author.id!,
      patchedRfcAuthor: {
        isEditor: Boolean(author.isEditor),
      }
    })
  ))

},
  { deep: true }
)


</script>
