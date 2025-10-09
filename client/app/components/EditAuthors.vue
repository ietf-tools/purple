<template>
  <BaseCard>
    <template #header>
      <CardHeader title="Edit Authors"/>
    </template>
    <div v-if="draft.authors" class="border-5 border-gray-700 text-gray-500">
      <p class="italic text-sm">(drag to reorder)</p>
      <ul ref="parent" class="block">
        <li class="flex items-center justify-between pl-2 cursor-ns-resize pr-1 py-1 mt-1 border rounded-md border-gray-400" v-for="(author, index) in draft.authors" :index="index" :key="author.id">
          <Icon name="fluent:re-order-dots-vertical-24-regular" class="mr-2" />
          <input type="text" v-model="author.titlepageName" class="flex-1 min-w-0 cursor-text border border-gray-400 rounded py-1 mr-2"/>
          <label class="border flex gap-2 items-center cursor-pointer border-gray-400 inline-block px-2 py-1 rounded text-sm mr-4">
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
import type { RfcToBe } from '~/purple_client'

type Props = {
  draftName: string
}

const props = defineProps<Props>()

const draft = defineModel<CookedDraft | RfcToBe>({ required: true })

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
        titlepageName: author.titlepageName
      }
    })
  ))

},
  { deep: true }
)


</script>
