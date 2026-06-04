<template>
  <BaseCard>
    <template #header>
      <CardHeader :title="`Cluster-Members C${props.cluster.number}`">
        <template #actions>
          <Icon v-if="queueStatus === 'pending'" name="ei:spinner-3" size="1.3rem" class="animate-spin" title="Loading additional information about cluster documents" />
          <span v-else-if="queueStatus === 'error'" class="text-red-800 dark:text-red-400">
            {{ queueError }}
          </span>
        </template>
      </CardHeader>
    </template>
    <p class="italic text-sm mb-2">(drag to reorder)</p>
    <table class="w-full text-sm">
      <thead>
        <tr class="border-b border-gray-200 dark:border-gray-600 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">
          <th class="pb-2 w-6"></th>
          <th class="pb-2">Document</th>
          <th class="pb-2 w-48">Labels</th>
          <th class="pb-2 w-40">Enqueue Date</th>
          <th class="pb-2 w-56">Status</th>
          <th class="pb-2 w-56">Assignees</th>
          <th class="pb-2 w-36 text-center">Approvals Received</th>
          <th class="pb-2 w-28"></th>
        </tr>
      </thead>
      <tbody ref="parent">
        <tr v-for="(clusterDocument, index) in clusterDocumentsRef" :index="index" :key="clusterDocument.name"
          class="cursor-ns-resize bg-white dark:bg-gray-700 border-b border-gray-100 dark:border-gray-600 select-none hover:bg-gray-50 dark:hover:bg-gray-650">
          <td class="py-2 pl-1 pr-2">
            <Icon name="fluent:re-order-dots-vertical-24-regular" class="text-gray-400" />
          </td>
          <td class="py-2 pr-3 font-semibold">
            {{ clusterDocument.name }}
          </td>
          <td class="py-2 pr-3">
            <span v-for="(label, labelIndex) in labelsByDraftName[clusterDocument.name]" :key="labelIndex">
              <RpcLabel :label="label" />
            </span>
          </td>
          <td class="py-2 pr-3 text-gray-600 dark:text-gray-300">
            <component v-if="enqueuedAtByDraftName[clusterDocument.name]" :is="enqueuedAtByDraftName[clusterDocument.name]" />
          </td>
          <td class="py-2 pr-3">
            <template v-if="queueItemByDraftName[clusterDocument.name]?.assignmentSet?.length">
              <span v-for="role in [...new Set(queueItemByDraftName[clusterDocument.name]?.assignmentSet?.map(a => a.role))]" :key="role"
                class="mr-1">
                <BaseBadge :label="role" />
              </span>
              <span v-if="queueItemByDraftName[clusterDocument.name]?.assignmentSet?.some(a => a.role === 'blocked')"
                class="text-xs text-gray-500 dark:text-gray-400">
                {{ queueItemByDraftName[clusterDocument.name]?.blockingReasons?.map(br => br.reason?.name).filter(Boolean).join(', ') }}
              </span>
            </template>
          </td>
          <td class="py-2 pr-3">
            <ul class="space-y-0.5">
              <li v-for="assignment in queueItemByDraftName[clusterDocument.name]?.assignmentSet" :key="assignment.id"
                class="flex items-center gap-1.5 text-sm">
                <BaseBadge :label="assignment.role" class="shrink-0" />
                <span class="text-gray-700 dark:text-gray-300 truncate">
                  {{ personById[assignment.person ?? -1]?.name ?? '—' }}
                </span>
              </li>
            </ul>
          </td>
          <td class="py-2 pr-3 text-center">
            <Anchor :href="`/docs/${clusterDocument.name}/approvals`"
              class="text-violet-700 dark:text-violet-300 hover:underline whitespace-nowrap font-mono text-sm">
              {{ queueItemByDraftName[clusterDocument.name]?.finalApproval?.filter(a => a.approved !== undefined).length ?? 0 }}
              /
              {{ queueItemByDraftName[clusterDocument.name]?.finalApproval?.length ?? 0 }}
            </Anchor>
          </td>
          <td class="py-2 text-right">
            <button type="button" class="p-1 rounded bg-gray-100 text-gray-800 hover:bg-gray-200 focus:bg-gray-200 text-xs"
              :aria-label="`Remove ${clusterDocument.name}`"
              @click="() => removeDocument(clusterDocument.name)">&times;</button>
          </td>
        </tr>
      </tbody>
    </table>
    <div class="flex mx-3 py-3 justify-end border-t border-gray-300">
      <BaseButton @click="handleSaveReorder">Save new order</BaseButton>
    </div>
  </BaseCard>
</template>

<script setup lang="ts">
import { useDragAndDrop } from "fluid-dnd/vue";
import { type Cluster, type RfcToBe, type QueueItem, type RpcPerson } from '~/purple_client'
import { Anchor } from '#components'
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

const { data: people } = await useAsyncData(
  'rpc-people-for-cluster',
  () => api.rpcPersonList(),
  { server: false, lazy: true, default: () => [] as RpcPerson[] }
)

const personById = computed(() =>
  Object.fromEntries(people.value.map(p => [p.id, p]))
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

const labelsByDraftName = computed(() =>
  Object.fromEntries(
    Object.entries(queueItemByDraftName.value).map(([name, item]) => [name, item?.labels ?? []])
  )
)

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
