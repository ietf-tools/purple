<template>
  <div class="h-full bg-gray-100 text-black dark:bg-gray-800 dark:text-black px-2 pt-10 pb-2">
    <div>
      <Heading :heading-level="3" class="py-5 px-3">
        Add to Cluster {{ props.cluster.number }}
      </Heading>
      <BaseButton btnType="outline" class="absolute right-1 top-1 z-50" @click="closeOverlayModal">
        <Icon name="uil:times" class="h-5 w-5" aria-hidden="true" />
      </BaseButton>
    </div>
    <div class="px-3">
      <DocumentSearch v-model="selectedRfcToBe" />
    </div>
    <div class="flex mx-3 py-3 justify-end border-t border-gray-300">
      <BaseButton @click="handleAdd">Add to cluster</BaseButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { type RfcToBe, type Cluster } from '~/purple_client'
import { overlayModalKey } from '~/providers/providerKeys'
import BaseButton from './BaseButton.vue'

type Props = {
  cluster: Cluster
  onSuccess: () => Promise<void>
}

const snackbar = useSnackbar()

const props = defineProps<Props>()

const api = useApi()

const selectedRfcToBe = ref<RfcToBe | undefined>(undefined)

const overlayModalKeyInjection = inject(overlayModalKey)

if (!overlayModalKeyInjection) {
  throw Error('Expected injection of overlayModalKey')
}

const { closeOverlayModal } = overlayModalKeyInjection

const handleAdd = () => {
  snackbar.add({ type: 'error', title: 'Adding a document to a cluste is not yet done', text: 'Maybe tomorrow' })
  props.onSuccess()
  closeOverlayModal()
}
</script>
