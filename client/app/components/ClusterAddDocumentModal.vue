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
    <div class="px-3 mb-3 text-sm text-gray-600 dark:text-gray-400">
      <p>Use this interface to add documents <strong>without</strong> setting a reference.</p>
      <p>Use the Publishing Dependencies dialog on the document's individual info page to add a document to the cluster that is a normative reference.</p>
    </div>
    <div class="px-3 flex flex-row items-center gap-2">
      <DocumentsSearch id="clusterDocument" label="Add received draft" v-model="selectedRfcToBe" />
      <BaseButton @click="handleAdd" :disabled="selectedRfcToBe === undefined">Add</BaseButton>
    </div>
    <div class="px-3 mt-3 pt-3 border-t border-gray-300">
      <div class="flex flex-row items-center gap-2">
        <label class="text-gray-900 dark:text-gray-200 w-[160px] text-right text-sm font-bold mr-1 shrink-0" for="notReceivedDraft">
          Add not-received draft:
        </label>
        <input
          id="notReceivedDraft"
          v-model="notReceivedDraftName"
          type="text"
          placeholder="draft-ietf-example-document"
          class="flex-1 rounded-lg border border-gray-500 px-2 py-1 text-sm bg-white dark:bg-gray-700 text-black dark:text-white outline-none focus:ring-2 focus:ring-blue-500"
          @keydown.enter="handleAddNotReceived"
        />
        <BaseButton @click="handleAddNotReceived" :disabled="!notReceivedDraftName.trim()">Add</BaseButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { type RfcToBe, type Cluster } from '~/purple_client'
import { overlayModalKey } from '~/providers/providerKeys'
import BaseButton from './BaseButton.vue'
import { snackbarForErrors } from '~/utils/snackbar'

type Props = {
  cluster: Cluster
  onSuccess: () => Promise<void>
}

const snackbar = useSnackbar()

const props = defineProps<Props>()

const api = useApi()

const selectedRfcToBe = ref<RfcToBe | undefined>(undefined)

const notReceivedDraftName = ref('')

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

const handleAddNotReceived = async () => {
  const draftName = notReceivedDraftName.value.trim()
  if (!draftName) return
  try {
    await api.clustersAddDocument({
      number: props.cluster.number,
      clusterAddRemoveDocumentRequest: { draftName }
    })
    snackbar.add({ type: 'success', title: 'Not-received draft added to cluster', text: '' })
    notReceivedDraftName.value = ''
    props.onSuccess()
    closeOverlayModal()
  } catch (error) {
    snackbarForErrors({ snackbar, defaultTitle: "Couldn't add draft to cluster", error })
  }
}
</script>
