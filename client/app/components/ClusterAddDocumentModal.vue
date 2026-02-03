<template>
  <div class="h-full bg-gray-100 text-black dark:text-white dark:bg-gray-800 px-2 pt-10 pb-2">
    <div>
      <Heading :heading-level="3" class="py-5 px-3">
        Add to Cluster {{ props.cluster.number }}
      </Heading>
      <BaseButton btnType="outline" class="absolute right-1 top-1 z-50" @click="closeOverlayModal">
        <Icon name="uil:times" class="h-5 w-5" aria-hidden="true" />
      </BaseButton>
    </div>
    <div class="px-3">
      <DocumentsSearch id="clusterDocument" label="Search for draft" v-model="selectedRfcToBe" />
    </div>
    <div class="flex mx-3 mt-3 py-3 justify-end border-t border-gray-300">
      <BaseButton @click="handleAdd" :disabled="selectedRfcToBe === undefined">Add to cluster</BaseButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { type RfcToBe, type Cluster } from '../purple_client'
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

const handleAdd = async () => {
  const { value: newRfcToBe } = selectedRfcToBe
  if (newRfcToBe === undefined) {
    snackbar.add({ type: 'error', title: 'An RFC must be chosen', text: '' })
    return
  }
  const { name: draftName } = newRfcToBe
  if (!draftName) {
    snackbar.add({ type: 'error', title: 'An RFC must have a draft name to be added', text: '' })
    return
  }
  try {
    const serverCluster = await api.clustersAddDocument({
      number: props.cluster.number,
      clusterAddRemoveDocumentRequest: {
        draftName
      }
    })

    if (serverCluster.documents?.some(rfcToBe => rfcToBe.name === draftName)) {
      snackbar.add({ type: 'success', title: 'Cluster document added', text: '' })
      props.onSuccess()
      closeOverlayModal()
    } else {
      snackbar.add({ type: 'error', title: "Couldn't add cluster document", text: "The server didn't say why" })
    }
  } catch (error) {
    snackbarForErrors({ snackbar, defaultTitle: "Couldn't add cluster document", error })
  }

}
</script>
