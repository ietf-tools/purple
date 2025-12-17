<template>
  <BaseCard>
    <template #header>
      <CardHeader :title="`Reorder Cluster ${props.cluster.number}`">
        <template #actions>
          <Icon v-if="queueStatus === 'pending' || labelsStatus === 'pending'" name="ei:spinner-3" size="1.3rem" class="animate-spin" title="Loading additional information about cluster documents" />
          <span v-else-if="queueStatus === 'error' || labelsStatus === 'error'" class="text-red-800 dark:text-red-400">
            {{ queueError }}
            {{ labelsError }}
          </span>
        </template>
      </CardHeader>
    </template>
    <p class="italic text-sm">(drag to reorder)</p>
    <ol ref="parent" class="min-w-[200px] mb-6">
      <li v-for="(clusterDocument, index) in clusterDocumentsRef" :index="index" :key="clusterDocument.name"
        class="flex justify-between items-center pl-2 cursor-ns-resize pr-1 py-1 mt-1 bg-white dark:bg-gray-700 border rounded-md border-gray-400 select-none">
        <span class="flex items-center font-semibold text-sm w-[350px]">
          <Icon name="fluent:re-order-dots-vertical-24-regular" class="mr-2" />
          {{ clusterDocument.name }}
        </span>

        <span class="w-[200px]">
          <span v-if="rfcToBeLabelsByName[clusterDocument.name]"
            v-for="(label, labelIndex) in rfcToBeLabelsByName[clusterDocument.name]" :key="labelIndex">
            <RpcLabel :label="label" />
          </span>
          <span v-else-if="labelsStatus === 'pending'">
            <!-- <Icon name="ei:spinner-3" size="1.3rem" class="animate-spin" /> -->
          </span>
          <span v-else-if="labelsStatus === 'success' && queueStatus === 'success'"
            title="Couldn't find rfcToBe in queue">
            ?
          </span>
        </span>

        <span class="w-[100px]">
          <span v-if="enqueuedAtByDraftName[clusterDocument.name]">
            <component :is="enqueuedAtByDraftName[clusterDocument.name]" />
          </span>
          <span v-else-if="queueStatus === 'pending'">
            <!-- <Icon name="ei:spinner-3" size="1.3rem" class="animate-spin" /> -->
          </span>
        </span>

        <button type="button" class="p-2 rounded-md bg-gray-100 text-gray-800 hover:bg-gray-200 focus:bg-gray-200"
          :aria-label="`Remove ${clusterDocument.name}`"
          @click="() => removeDocument(clusterDocument.name)">&times</button>
      </li>
    </ol>
    <div class="flex mx-3 py-3 justify-end border-t border-gray-300">
      <BaseButton @click="handleSaveReorder">Save new order</BaseButton>
    </div>
  </BaseCard>
</template>

<script setup lang="ts">
import { useDragAndDrop } from "fluid-dnd/vue";
import { type Cluster, type RfcToBe, type Label, type QueueItem } from '~/purple_client'
import BaseButton from './BaseButton.vue'
import { calculateEnqueuedAtData, renderEnqueuedAt } from '../utils/queue'

type Props = {
  cluster: Cluster
  onSuccess: () => Promise<void>
  rfcsToBe?: RfcToBe[]
}

const {
  data: queue,
  status: queueStatus,
  pending,
  refresh,
  error: queueError,
} = await useAsyncData(
  'queue-for-cluster',
  () => api.queueList(),
  {
    server: false,
    lazy: true,
    default: () => [] as QueueItem[],
  }
)

const snackbar = useSnackbar()

const props = defineProps<Props>()

type QueueItemByDraftName = Record<string, QueueItem | undefined>

const queueItemByDraftName = computed(() => queue.value.reduce((acc, queueItem) => {
  const { name } = queueItem
  if (name !== undefined) {
    acc[name] = queueItem
  }
  return acc
}, {} as QueueItemByDraftName))

type EnqueuedAtByDraftName = Record<string, ReturnType<typeof renderEnqueuedAt> | undefined>
const enqueuedAtByDraftName = computed(() => queue.value.reduce((acc, queueItem) => {
  const { name, enqueuedAt, cluster } = queueItem
  if (name !== undefined && enqueuedAt) {
    const vNodes = renderEnqueuedAt(calculateEnqueuedAtData(enqueuedAt))
    if (cluster?.number === props.cluster.number) {
      console.log("cluster hit", name)
    } else {
      console.log("cluster miss", name)
    }
    acc[name] = vNodes
  }
  return acc
}, {} as EnqueuedAtByDraftName))

const clusterDocumentsRef = ref(props.cluster.documents ?? [])

const { data: labels, status: labelsStatus, error: labelsError } = await useAsyncData(
  `labels-lazy`,
  () => api.labelsList(),
  {
    default: () => ([] as Label[]),
    server: false,
    lazy: true,
  }
)

type LabelsById = Record<number, Label | undefined>

const labelsById = computed(() => labels.value.reduce((acc, label) => {
  const { id } = label
  if (id) {
    acc[id] = label
  }
  return acc
}, {} as LabelsById))

type RfcToBeLabelsByName = Record<string, Label[] | undefined>

const rfcToBeLabelsByName = computed(() => props.rfcsToBe?.reduce((acc, rfcToBe) => {
  const { name } = rfcToBe
  if (!name) {
    throw Error('Expected item to have id')
  }
  if (labels.value.length > 0) {
    const rfcToBeLabelsResolved = rfcToBe.labels.map(labelId => labelsById.value[labelId]).filter(item => !!item)
    acc[name] = rfcToBeLabelsResolved.length > 0 ? rfcToBeLabelsResolved : undefined
  }
  return acc
}, {} as RfcToBeLabelsByName) ?? {})

const [parent] = useDragAndDrop(clusterDocumentsRef);

const api = useApi()

const removeDocument = async (name: string) => {
  const reallyRemove = confirm(`Really remove ${JSON.stringify(name)} from cluster?`)
  if (!reallyRemove) {
    console.info("User rejected removing member from cluster")
    return
  }

  try {
    const serverCluster = await api.clustersRemoveDocument({
      number: props.cluster.number,
      clusterAddRemoveDocumentRequest: {
        draftName: name,
      }
    })

    if (serverCluster.documents?.some(clusterMember => clusterMember.name === name)) {
      snackbar.add({ type: 'error', title: `Cluster member removal failed.`, text: `` })
      return
    }

    snackbar.add({ type: 'success', title: `Cluster member removal succeeded`, text: '' })
    props.onSuccess()
  } catch (error) {
    snackbarForErrors({ snackbar, error, defaultTitle: "Can't remove member from cluster" })
  }
}

const handleSaveReorder = async () => {
  if (clusterDocumentsRef.value.length <= 1) {
    snackbar.add({ type: 'info', title: `Can't reorder a cluster with ${clusterDocumentsRef.value.length} documents`, text: '' })
    return
  }
  try {
    const draftNames = clusterDocumentsRef.value.map(doc => doc.name)
    const serverCluster = await api.clustersReorderDocuments({
      number: props.cluster.number,
      clusterReorderDocumentsRequest: {
        draftNames
      }
    })

    if (!serverCluster.documents) {
      snackbar.add({ type: 'error', title: `Server cluster reorder request failed.`, text: `Returned 0 docs when it should have returned ${draftNames.length}` })
      return
    }

    const serverDraftNames = serverCluster.documents.map(doc => doc.name)

    if (serverDraftNames.length !== draftNames.length || JSON.stringify(draftNames) !== JSON.stringify(serverDraftNames)) {
      console.error("Server rejected reorder", { draftNames, newDraftNames: serverDraftNames })
      snackbar.add({ type: 'error', title: `Server cluster reorder failed.`, text: `See dev console for details` })
      return
    }

    snackbar.add({ type: 'success', title: `Cluster reorder succeeded`, text: '' })
    props.onSuccess()
  } catch (error) {
    snackbarForErrors({ snackbar, error, defaultTitle: "Can't reorder cluster" })
  }
}
</script>
