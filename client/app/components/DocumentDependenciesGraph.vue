<template>
  <ErrorAlert v-if="rfcToBesStatus === 'error' || clusterDocumentsReferencesListStatus === 'error'"
    title="Loading error. Reload page.">
    {{ rfcToBesError }}
    {{ clusterDocumentsReferencesListError }}
  </ErrorAlert>

  <div ref="container" class="overflow-hidden h-[75vh] border border-gray-700 rounded-md bg-white inset-shadow-sm">
  </div>

  <div class="flex gap-2 justify-between py-2 px-1.5">
    <span class="flex flex-row items-center text-sm pl-1">
      Pan and zoom the dependency graph after the layout settles.
    </span>
    <span class="flex flex-row items-center gap-2">
      <RpcCheckbox label="Show legend" value="" :checked="showLegend" @change="showLegend = !showLegend" size='medium'
        class="mr-3" />
      <BaseButton btn-type="default" :class="{ 'opacity-50': !canDownload }" @click="handleDownload">
        <span v-if="canDownload">
          <Icon name="el:download-alt" size="1.1em" class="mr-2" />
          Download
        </span>
        <span v-else>
          <Icon name="ei:spinner-3" size="1.5em" class="animate-spin mr-2" />
          Loading...
        </span>
      </BaseButton>
    </span>
  </div>
</template>

<script setup lang="ts">
import { uniqBy } from 'lodash-es';
import type { Cluster } from '~/purple_client'
import { draw_graph, type DrawGraphParameters } from '~/utils/document_relations';
import { legendData, type DataParam, type LinkParam, type NodeParam, type Rel } from '~/utils/document_relations-utils'
import { downloadTextFile } from '~/utils/download';

type Props = {
  cluster: Cluster
}

const props = defineProps<Props>()

const api = useApi()

const snackbar = useSnackbar()

const containerRef = useTemplateRef('container')

const showLegend = ref(false)

const { data: clusterDocumentsReferencesList, status: clusterDocumentsReferencesListStatus, error: clusterDocumentsReferencesListError } = await useAsyncData(
  async () =>
    Promise.all(
      props.cluster.documents.map(
        (clusterDocument) => api.documentsReferencesList({ draftName: clusterDocument.name })
      ))
)

const { data: rfcToBes, status: rfcToBesStatus, error: rfcToBesError } = await useAsyncData(
  async () => {
    const filterIsString = (maybeString: string | undefined) => typeof maybeString === 'string'
    const names: string[] = (clusterDocumentsReferencesList.value ?? []).flatMap(
      (relatedDocuments): string[] => [
        ...relatedDocuments.map((relatedDocument) => relatedDocument.draftName).filter(filterIsString),
        ...relatedDocuments.map((relatedDocument) => relatedDocument.targetDraftName).filter(filterIsString)
      ])
    console.log("From", clusterDocumentsReferencesList.value, "Accessing draft names", names)
    return Promise.all(
      names.map(name => api.documentsRetrieve({ draftName: name }))
    )
  })

const canDownload = ref(false)

type SnackbarType = NonNullable<Parameters<(typeof snackbar)["add"]>[0]["type"]>

const snackbarMessage = (title: string, type: SnackbarType = 'error'): void => {
  snackbar.add({
    type,
    title,
    text: ''
  })
}

const hasMounted = ref(false)

const data = computed(() => {
  const newData: DataParam = {
    links: [],
    nodes: []
  }

  const isNode = (data: unknown): data is NodeParam => {
    const isANode = Boolean((data && typeof data === 'object' && 'id' in data))
    return isANode
  }

  const isLink = (data: unknown): data is LinkParam => {
    return Boolean((data && typeof data === 'object' && 'source' in data && 'target' in data && 'rel' in data))
  }

  if (rfcToBes.value) {
    newData.nodes.push(
      ...rfcToBes.value.map((rfcToBe): NodeParam | null => {
        const { name } = rfcToBe
        if (!name) return null
        return { id: name, rfc: Boolean(rfcToBe.rfcNumber), url: `/docs/${name}`, level: parseLevel(rfcToBe.submittedStdLevel) }
      }).filter(isNode)
    )
  }

  if (clusterDocumentsReferencesList.value) {
    clusterDocumentsReferencesList.value.forEach(documentsReferencesList => {
      documentsReferencesList.forEach(reference => {
        const { draftName, targetDraftName, relationship } = reference;
        if (!draftName || !targetDraftName) {
          return
        }
        newData.nodes.push(
          { id: draftName },
          { id: targetDraftName }
        )
        newData.links.push(
          { source: draftName, target: targetDraftName, rel: relationship as Rel }
        )
      })
    })
  }

  if (props.cluster.documents) {
    newData.nodes.push(...props.cluster.documents.map((document): NodeParam | null => {
      const { name } = document
      if (!name) return null
      return {
        id: name
      }
    }).filter(isNode))

    newData.links.push(...props.cluster.documents.flatMap((document, index): LinkParam[] | null => {
      const { name } = document
      if (!name || !clusterDocumentsReferencesList.value) return null
      const clusterDocumentReferences = clusterDocumentsReferencesList.value[index]
      if (!clusterDocumentReferences) return null
      return clusterDocumentReferences.map((clusterDocumentReference): LinkParam | null => {
        const { draftName } = clusterDocumentReference
        if (!draftName) return null
        return {
          source: name,
          target: draftName,
          rel: 'relinfo',
        }
      }).filter(isLink)
    }).filter(isLink))
  }

  newData.nodes = uniqBy(newData.nodes, (node) => node.id)
  newData.links = uniqBy(newData.links, (link) => JSON.stringify([link.source, link.target, link.rel]))

  return newData
})

const attemptToRenderGraph = () => {
  const { value: container } = containerRef

  if (!container) {
    if (
      // only bother reporting error if DOM ref was expected to be found, ie after mounting
      hasMounted.value === true) {
      console.error('container ref not found')
    }
    return
  }

  const graphData = structuredClone(
    // the D3 code will mutate arg data so we'll make a copy
    data.value
  )

  const args: DrawGraphParameters = showLegend.value
    ? [legendData]
    : [graphData]

  let [leg_el, leg_sim] = draw_graph(...args);

  if (!(leg_el instanceof SVGElement) || !leg_sim) {
    console.error({ leg_el, leg_sim })
    return snackbarMessage(`Received unexpected response from draw_graph. See dev console.`)
  }

  while (container.firstChild) {
    container.removeChild(container.firstChild)
  }

  container.appendChild(leg_el)

  if (leg_sim instanceof SVGSVGElement) {
    console.error({ leg_sim })
    return snackbarMessage('Expected `leg_sim` to be D3 Simulation Node not SVGSVGElement. See dev console.')
  } else {
    leg_sim.restart();
  }

  canDownload.value = true // now that we've rendered the SVG we can offer it for download
}

onMounted(() => {
  hasMounted.value === true
  attemptToRenderGraph()
})

watch([data, showLegend], attemptToRenderGraph)

const handleDownload = () => {
  if (!canDownload.value) {
    return snackbarMessage('Still preparing download. Try again soon')
  }
  const { value: container } = containerRef
  if (!container) {
    return snackbarMessage('container ref not found')
  }
  const svgString = container.innerHTML
  downloadTextFile(`cluster-${props.cluster.number}.svg`, 'text/svg', svgString)
}
</script>
