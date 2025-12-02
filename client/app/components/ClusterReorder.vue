<template>
  <BaseCard>
    <template #header>
      <CardHeader :title="`Reorder Cluster ${props.cluster.number}`" />
    </template>
    <p class="italic text-sm">(drag to reorder)</p>
    <ol ref="parent" class="min-w-[200px] mb-6">
      <li v-for="(clusterDocument, index) in clusterDocumentsRef" :index="index" :key="clusterDocument.name"
        class="flex items-center pl-2 cursor-ns-resize pr-1 py-1 mt-1 bg-white border rounded-md border-gray-400 select-none">
        <Icon name="fluent:re-order-dots-vertical-24-regular" class="mr-2" />
        {{ clusterDocument.name }}
      </li>
    </ol>
    <div class="flex mx-3 py-3 justify-end border-t border-gray-300">
      <BaseButton @click="handleSaveReorder">Save new order</BaseButton>
    </div>
  </BaseCard>
</template>

<script setup lang="ts">
import { useDragAndDrop } from "fluid-dnd/vue";
import type { Cluster } from '~/purple_client'
import BaseButton from './BaseButton.vue'

type Props = {
  cluster: Cluster
  onSuccess: () => Promise<void>
}

const snackbar = useSnackbar()

const props = defineProps<Props>()

const clusterDocumentsRef = ref(props.cluster.documents)

const [parent] = useDragAndDrop(clusterDocumentsRef);

const api = useApi()

const handleSaveReorder = () => {
  snackbar.add({ type: 'error', title: 'Saving new cluster order is not yet done', text: 'Maybe tomorrow' })
  props.onSuccess()
}
</script>
