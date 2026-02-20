<template>
  <div ref="container"
    class="overflow-hidden h-[75vh] flex items-center justify-center border border-gray-700 dark:border-gray-200 rounded-md inset-shadow-sm text-center">
    <Icon name="ei:spinner-3" size="1.3rem" class="animate-spin" />
  </div>

  <div v-show="tooltip.text" class="absolute transition-all" :style="{
    left: `${tooltip.position[0]}px`,
    top: `${tooltip.position[1]}px`,
  }">
    <div
      class="absolute transition-all bottom-0 text-xs text-center bg-white dark:bg-black text-black dark:text-white border border-gray-400 rounded-md shadow-xl p-2 w-[15em]">
      <p v-for="line in tooltip.text">{{ line }}</p>
    </div>
  </div>

  <div class="flex gap-2 justify-between py-2 px-1.5">
    <span class="flex flex-row items-center text-sm pl-1">
      Pan and zoom the dependency graph after the layout settles.
    </span>
    <span class="flex flex-row items-center gap-2">
      <select @change="handleChange" class="text-xs rounded-md">
        <option value="default">Show Cluster</option>
        <option value="legend">Show Legend</option>
        <option value="complex">Debug: Show complex cluster</option>
      </select>
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

  <details class="mt-10 pb-10">
    <summary class="flex justify-end font-bold cursor-pointer">Diagram data (for debug)</summary>

    <div class="ml-4">
      <h3 class="mt-4 font-bold">Cluster</h3>
      <pre>{{ JSON.stringify(clusterToUse, null, 2) }}</pre>
      <h3 class="mt-4 font-bold">RFCsToBe</h3>
      <pre>{{ JSON.stringify(rfcsToBe, null, 2) }}</pre>
    </div>
  </details>
</template>

<script setup lang="ts">
import { uniqBy } from 'lodash-es';
import { type Cluster, type RfcToBe } from '~/purple_client'
import { drawGraph, type DrawGraphParameters, type SetTooltip } from '~/utils/document_relations';
import { legendData, complexClusterExample, type DataParam, type LinkParam, type NodeParam } from '~/utils/document_relations-utils'
import { downloadTextFile } from '~/utils/download';

type Props = {
  cluster: Cluster
  rfcsToBe?: RfcToBe[]
}

const props = defineProps<Props>()

const clusterToUse = ref(props.cluster)

const snackbar = useSnackbar()

const router = useRouter()

const containerRef = useTemplateRef('container')

const showLegend = ref(false)

const canDownload = ref(false)

type SnackbarType = NonNullable<Parameters<(typeof snackbar)["add"]>[0]["type"]>

const snackbarMessage = (title: string, type: SnackbarType = 'error'): void => {
  snackbar.add({
    type,
    title,
    text: ''
  })
}

const api = useApi()


const handleChange = (e: Event) => {
  const { target } = e
  if (!(target instanceof HTMLSelectElement)) {
    console.log("Expected <select>", e, target)
    return
  }
  switch (target.value) {
    case 'default':
      clusterToUse.value = props.cluster
      showLegend.value = false

      break
    case 'complex':
      clusterToUse.value = complexClusterExample
      showLegend.value = false

      break
    case 'legend':
      showLegend.value = true
      break
  }
}

const tooltip = ref<{ text: string[] | undefined, position: [number, number] }>({ text: undefined, position: [0, 0] })

const setTooltip: SetTooltip = (props) => {
  if (!props) {
    tooltip.value.text = undefined
    return
  }
  tooltip.value = props
}

const hasMounted = ref(false)

const rfcsByDraftName = computed(() => {
  const result: Record<string, RfcToBe> = {}
  if (props.rfcsToBe) {
    for (const rfcToBe of props.rfcsToBe) {
      if (rfcToBe.name) {
        result[rfcToBe.name] = rfcToBe
      }
    }
  }
  return result
})

const clusterGraphData = computed(() => {

  // delay building graph until this is available
  if (!rfcsByDraftName.value) {
    return { links: [], nodes: [] }
  }

  const newClusterGraphData: DataParam = {
    links: [],
    nodes: []
  }

  const isNodeParam = (data: unknown): data is NodeParam => {
    const isANode = Boolean((data && typeof data === 'object' && 'id' in data))
    if (!isANode) {
      console.log("!IS A NODE", isANode, data)
    }
    return isANode
  }

  const isLinkParam = (data: unknown): data is LinkParam => {
    return Boolean((data && typeof data === 'object' && 'source' in data && 'target' in data && 'rel' in data))
  }

  const rfcToBeToNodeParam = (rfcToBe: RfcToBe): NodeParam | undefined => {
    const { name, disposition } = rfcToBe
    if (!name) {
      console.warn("rfcToBe had no name?", rfcToBe)
      return
    }

    return {
      id: name,
      rfcToBe,
      rfcNumber: rfcToBe.rfcNumber ?? undefined,
      url: `/docs/${name}`,
      disposition: parseDisposition(disposition),
      isReceived: true,
    }
  }

  let referenceNodes: NodeParam[] = []

  newClusterGraphData.nodes.push(
    ...(clusterToUse.value.documents ?? []).flatMap((clusterMember): NodeParam[] | null => {
      const { name, rfcNumber, disposition, references, isReceived } = clusterMember
      const doc = name ? rfcsByDraftName.value[name] : undefined

      const resolvedRfcNumber = doc ? doc.rfcNumber ?? undefined : rfcNumber ?? undefined

      referenceNodes.push(...(references ?? []).flatMap(reference => {
        const { draftName, targetDraftName } = reference
        const draft = draftName ? rfcsByDraftName.value[draftName] : undefined
        const target = targetDraftName ? rfcsByDraftName.value[targetDraftName] : undefined

        return [
          draft ? rfcToBeToNodeParam(draft) : draftName ? { id: draftName, url: `/docs/${draftName}` } : undefined,
          target ? rfcToBeToNodeParam(target) : targetDraftName ? { id: targetDraftName, url: `/docs/${targetDraftName}` } : undefined,
        ].filter(isNodeParam)
      }))

      return [{
        id: name,
        rfcToBe: doc,
        url: `/docs/${name}`,
        rfcNumber: resolvedRfcNumber,
        isReceived: Boolean(isReceived),
        disposition: parseDisposition(disposition),
      }]
    }).filter(isNodeParam)
  )

  referenceNodes = referenceNodes.filter(
    // only include reference nodes if they weren't already mentioned
    referenceNode => !newClusterGraphData.nodes.some(graphDataNode => graphDataNode.id === referenceNode.id)
  )
  newClusterGraphData.nodes.push(...referenceNodes)

  newClusterGraphData.links.push(
    ...(clusterToUse.value.documents ?? []).flatMap((clusterMember): LinkParam[] | null => {
      const { references } = clusterMember

      return references ? references.map((reference): LinkParam | null => {
        const { draftName, targetDraftName, relationship } = reference

        if (draftName === undefined || targetDraftName === undefined) {
          console.warn("Graph: cluster reference", reference, " has undefined name(s)")
          return null
        }

        return {
          source: draftName,
          target: targetDraftName,
          rel: parseRelationship(relationship),
        }
      }).filter(isLinkParam) : null
    }).filter(isLinkParam)
  )


  newClusterGraphData.nodes = uniqBy(newClusterGraphData.nodes, (node) => node.id)
  newClusterGraphData.links = uniqBy(newClusterGraphData.links, (link) => JSON.stringify([link.source, link.target, link.rel]))

  return newClusterGraphData
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
    clusterGraphData.value
  )

  const chosenGraphData: DrawGraphParameters[0]["data"] = showLegend.value
    ? legendData
    : graphData

  let [leg_el, leg_sim] = drawGraph({
    data: chosenGraphData,
    pushRouter: router.push,
    colorMode: colorMode.value === 'dark' ? 'dark' : 'light',
    setTooltip,
  });

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

const colorMode = useColorMode()

watch(() => colorMode.value, attemptToRenderGraph)
watch(clusterGraphData, attemptToRenderGraph)
watch(showLegend, attemptToRenderGraph)
onMounted(attemptToRenderGraph)

const handleDownload = () => {
  if (!canDownload.value) {
    return snackbarMessage('Still preparing download. Try again soon')
  }
  const { value: container } = containerRef
  if (!container) {
    return snackbarMessage('container ref not found')
  }
  const svgString = container.innerHTML
  downloadTextFile(`cluster-${clusterToUse.value.number}.svg`, 'text/svg', svgString)
}

</script>
