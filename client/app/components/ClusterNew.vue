<template>
  <button type="button"
    class="flex items-center rounded-md bg-violet-600 px-3 py-2 text-center text-sm font-semibold text-white shadow-sm hover:bg-violet-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
    @click="handleOpenModal">
    <Icon name="uil:plus" class="-ml-1 h-5 w-5 mr-2" aria-hidden="true" />
    New Cluster
  </button>
</template>

<script setup lang="ts">
import { ClusterNewModal } from '#components'
import { overlayModalKey } from '~/providers/providerKeys';

type Props = {
  lastClusterNumber: number
  onSuccess: () => void
}

const props = defineProps<Props>()

const overlayModal = inject(overlayModalKey)

const snackbar = useSnackbar()

if (!overlayModal) {
  snackbar.add({
    type: 'error',
    title: "Expected modal features to be available",
    text: 'See console',
  })
  throw Error('Injection of modal not available')
}

const handleOpenModal = async () => {
  const { openOverlayModal } = overlayModal

  openOverlayModal({
    component: ClusterNewModal,
    componentProps: {
      lastClusterNumber: props.lastClusterNumber,
      onSuccess: () => {
        props.onSuccess()
      }
    },
    mode: 'side',
  }).catch(e => {
    if (e === undefined) {
      // ignore... it's just signalling that the modal has closed
    } else {
      console.error(e)
      throw e
    }
  })
}
</script>
