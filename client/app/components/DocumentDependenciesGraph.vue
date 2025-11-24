<template>
  <ErrorAlert v-if="rfcsToBeStatus === 'error' || documentsReferencesByRfcsStatus === 'error'"
    title="Loading error. Reload page.">
    {{ rfcToBesError }}
    {{ documentsReferencesByRfcsError }}
  </ErrorAlert>

  <div ref="container" class="overflow-hidden h-[80vh] border border-gray-700 rounded-md bg-white inset-shadow-sm">
  </div>

  <div class="flex gap-2 justify-between py-2 px-1.5">
    <span class="flex flex-row items-center text-sm pl-1">
      Pan and zoom the dependency graph after the layout settles.
    </span>
    <span class="flex flex-row items-center gap-2">
      <RpcCheckbox label="Show legend" :value="true" :checked="showLegend" @change="showLegend = !showLegend"
        size='medium' class="mr-3" />
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
import type { Cluster, RfcToBe, RpcRelatedDocument } from '~/purple_client'
import { draw_graph, type DrawGraphParameters } from '~/utils/document_relations';
import { legendData, test_data2, type Rel } from '~/utils/document_relations-utils'
// import type { DataParam, NodeParam, LinkParam } from '~/utils/document_relations-utils';
import { downloadTextFile } from '~/utils/download';
import { assert } from '~/utils/typescript';

type Props = {
  cluster: Cluster
}

const props = defineProps<Props>()

const api = useApi()

const snackbar = useSnackbar()

const containerRef = useTemplateRef('container')

const showLegend = ref(false)

const { data: documentsReferencesByRfcs, status: documentsReferencesByRfcsStatus, error: documentsReferencesByRfcsError } = await useAsyncData(
  async () => {
    const documentsReferencesArray = await Promise.all(
      props.cluster.documents.map(
        (clusterDocument) => api.documentsReferencesList({ draftName: clusterDocument.name })
      ))
    return documentsReferencesArray.map((documentsReferences, index) => {
      const clusterDocument = props.cluster.documents[index]
      if (!clusterDocument) {
        return undefined
      }
      const { rfcNumber, name: draftName } = clusterDocument
      assert(rfcNumber)
      return ({
        rfcNumber,
        draftName,
        documentsReferences
      })
    }).filter(item => {
      return (item !== undefined)
    })
  }
)

const { data: rfcToBes, status: rfcsToBeStatus, error: rfcToBesError } = await useAsyncData(
  async () =>
    Promise.all(
      documentsReferencesByRfcs.value?.flatMap(
        (documentsReferencesByRfc) => {
          const { documentsReferences } = documentsReferencesByRfc

          return documentsReferences.map(documentReference => {
            const { draftName } = documentReference
            assert(draftName)
            return api.documentsRetrieve({ draftName })
          })
        }
      ) ?? []),
  {
    lazy: true,
    server: false,
    default: () => [] as RfcToBe[]
  }
)

const canDownload = computed(() => Boolean(rfcToBes.value))

type SnackbarType = NonNullable<Parameters<(typeof snackbar)["add"]>[0]["type"]>

const snackbarMessage = (title: string, type: SnackbarType = 'error'): void => {
  snackbar.add({
    type,
    title,
    text: ''
  })
}

const hasMounted = ref(false)

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
  if (rfcsToBeStatus.value !== 'success') {
    console.error(`RFCs ${rfcsToBeStatus.value}, trying again soon`)
    return
  }
  if (documentsReferencesByRfcsStatus.value !== 'success' || !documentsReferencesByRfcs.value) {
    console.error(`RFC references ${documentsReferencesByRfcsStatus.value}, trying again soon`)
    return
  }

  type DrawGraphParametersLink = DrawGraphParameters[0]["links"][number]
  const isLink = (data: unknown): data is DrawGraphParametersLink => {
    return Boolean((data && typeof data === 'object' && 'source' in data && 'target' in data && 'rel' in data))
  }

  type DrawGraphParametersNode = DrawGraphParameters[0]["nodes"][number]
  const isNode = (data: unknown): data is DrawGraphParametersNode => {
    return Boolean((data && typeof data === 'object' && 'id' in data && 'rfc' in data))
  }

  const rfcsToBesWithStreams = rfcToBes.value.filter(rfcToBe => rfcToBe.intendedStream)
  const stream = rfcsToBesWithStreams[0]?.intendedStream!

  const data: DrawGraphParameters[0] = {
    links: [
      ...rfcToBes.value.map((rfcToBe): DrawGraphParametersLink | null => {
        if (typeof rfcToBe.rfcNumber !== 'number' || !rfcToBe.name) {
          return null
        }
        return {
          source: `rfc${rfcToBe.rfcNumber}`,
          target: rfcToBe.name,
          rel: "refqueue" as Rel,
        }
      }).filter(isLink),
      ...documentsReferencesByRfcs.value.flatMap((documentsReferencesByRfc): (DrawGraphParametersLink | null)[] => {
        return documentsReferencesByRfc.documentsReferences.map((documentReference): DrawGraphParametersLink | null => {
          const { draftName, targetDraftName } = documentReference
          if (!draftName || !targetDraftName) {
            return null
          }
          return {
            source: draftName,
            target: targetDraftName,
            rel: documentReference.relationship as Rel
          }
        })
      }).filter(isLink)
    ],
    nodes: [
      ...rfcToBes.value.map((rfcToBe): DrawGraphParametersNode | null => {
        if (typeof rfcToBe.rfcNumber !== 'number' || !rfcToBe.name) {
          return null
        }

        return {
          id: `rfc${rfcToBe.rfcNumber}`,
          rfc: true,
          "post-wg": true,
          expired: false,
          replaced: false,
          group: rfcToBe.intendedStream,
          url: undefined,
          level: parseLevel(rfcToBe.intendedStdLevel),
        }
      }).filter(isNode),
      ...documentsReferencesByRfcs.value.flatMap((documentsReferencesByRfc): (DrawGraphParametersNode | null)[] => {
        return documentsReferencesByRfc.documentsReferences.flatMap((documentReference): DrawGraphParametersNode | null => {
          const { draftName, targetDraftName } = documentReference
          if (!draftName || !targetDraftName) {
            return null
          }
          return {
            id: draftName,
            rfc: false,
            "post-wg": true,
            expired: false,
            replaced: false,
            url: undefined,
          }
        })
      }).filter(isNode)
    ]
  }

  const args: DrawGraphParameters = showLegend.value ? [legendData, "this group"] : [data, stream]

  console.log({ args })

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
}

onMounted(() => {
  hasMounted.value === true
  attemptToRenderGraph()
})

watch([rfcToBes, documentsReferencesByRfcs], attemptToRenderGraph)

const handleDownload = () => {
  if (!canDownload.value) {
    return snackbarMessage('Still preparing download. Try again soon')
  }
  const { value: container } = containerRef
  if (!container) {
    return snackbarMessage('container ref not found')
  }
  const svgString = container.outerHTML
  downloadTextFile(`cluster-${props.cluster.number}.svg`, 'text/svg', svgString)
}
</script>
