<template>
  <div class="h-full bg-gray-100 text-black dark:bg-gray-800 dark:text-black px-2 pt-10 pb-2">
    <div>
      <Heading :heading-level="3" class="p-5">
        Reorder Cluster {{ props.cluster.number }}
      </Heading>
      <BaseButton btnType="outline" class="absolute right-1 top-1 z-50" @click="closeOverlayModal">
        <Icon name="uil:times" class="h-5 w-5" aria-hidden="true" />
      </BaseButton>
    </div>

    <div>
      <p class="italic text-sm">(drag to reorder)</p>
      <ol ref="parent" class="min-w-[200px] mb-6">
        <li v-for="(clusterDocument, index) in clusterDocumentsRef" :index="index" :key="clusterDocument.name"
          class="flex items-center pl-2 cursor-ns-resize pr-1 py-1 mt-1 bg-white border rounded-md border-gray-400 select-none">
          <Icon name="fluent:re-order-dots-vertical-24-regular" class="mr-2" />
          {{ clusterDocument.name }}
        </li>
      </ol>
    </div>
    <BaseButton @click="handleSaveReorder">Save new order</BaseButton>
  </div>
</template>

<script setup lang="ts">
import { useDragAndDrop } from "fluid-dnd/vue";
import type { Cluster } from '~/purple_client'
import { overlayModalKey } from '~/providers/providerKeys'
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

const overlayModalKeyInjection = inject(overlayModalKey)

if (!overlayModalKeyInjection) {
  throw Error('Expected injection of overlayModalKey')
}

const { closeOverlayModal } = overlayModalKeyInjection

const handleSaveReorder = () => {
  snackbar.add({ type: 'error', title: 'Saving new cluster order is not yet done', text: 'Maybe tomorrow' })
  props.onSuccess()
  closeOverlayModal()
}
</script>
