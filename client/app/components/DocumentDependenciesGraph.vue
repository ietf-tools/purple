<template>
  <h2 class="flex flex-row items-center text-md font-bold pl-1">
    Document dependencies
  </h2>

  <div ref="container" class="overflow-hidden h-full">
  </div>

  <div class="flex gap-2 justify-between border-t border-gray-400 p-2">
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
import type { Cluster, RfcToBe } from '~/purple_client'
import { draw_graph, type DrawGraphParameters } from '~/utils/document_relations';
import { legendData, test_data2 } from '~/utils/document_relations-utils'
// import type { DataParam, NodeParam, LinkParam } from '~/utils/document_relations-utils';
import { downloadTextFile } from '~/utils/download';
import { assert } from '~/utils/typescript';

type Props = {
  cluster: Cluster
}

const props = defineProps<Props>()

const api = useApi()

const containerRef = useTemplateRef('container')

const showLegend = ref(false)

const { data: documentsReferencesByRfcs, error: documentsReferencesByRfcsError } = await useAsyncData(
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

const { data: rfcToBes, error: rfcToBesError } = await useAsyncData(
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

// const data = computed((): DataParam => {
//   return {
//     links: [
//       ...documentsReferencesByRfcs.value?.map((documentsReferencesByRfc): LinkParam => {
//         const { rfcNumber, draftName } = documentsReferencesByRfc

//         assert(rfcNumber)
//         assert(draftName)

//         return {
//           source: `rfc${rfcNumber}`,
//           rel: 'relinfo', //
//           target: draftName,
//         }
//       }) ?? [],

//       ...documentsReferencesByRfcs.value?.flatMap((documentsReferencesByRfc): LinkParam[] => {
//         const { rfcNumber, draftName, documentsReferences } = documentsReferencesByRfc

//         return documentsReferences.map((documentsReference): LinkParam => {
//           const {
//             draftName: source,
//             targetDraftName: target
//           } = documentsReference

//           assert(source)
//           assert(target)

//           return {
//             source,
//             rel: 'refnorm',
//             target,
//           }
//         })
//       }) ?? []
//     ],
//     nodes: [
//       ...rfcToBes.value?.map((rfcToBe): NodeParam => {
//         const {
//           name: id,
//           intendedStdLevel: level,
//         } = rfcToBe

//         assert(id)
//         assert(level)

//         return {
//           id,
//           url: `/doc/${id}/`,
//           rfc: true,
//           "post-wg": undefined,
//           expired: undefined,
//           replaced: undefined,
//           group: undefined,
//           level: undefined,
//         }
//       }) ?? []
//     ]
//   }
// })

onMounted(() => {
  const { value: container } = containerRef

  if (!container) {
    console.error('container ref not found')
    return
  }

  console.log("container ref found")

  const args: DrawGraphParameters = showLegend.value ? [legendData, "this group"] : [test_data2, "stir"]

  let [leg_el, leg_sim] = draw_graph(...args);

  if (!(leg_el instanceof SVGElement) || !leg_sim) {
    console.error('Received unexpected response from draw_graph', { leg_el, leg_sim })
    return
  }

  while (container.firstChild) {
    container.removeChild(container.firstChild)
  }

  container.appendChild(leg_el)

  if (leg_sim instanceof SVGSVGElement) {
    console.log({ leg_sim })
    throw Error('Expected `leg_sim` to be D3 Simulation Node not SVGSVGElement. See console.')
  } else {
    leg_sim.restart();
  }
})

const handleDownload = () => {
  if (!canDownload.value) {
    alert('Not ready to download')
    return
  }
  const { value: container } = containerRef
  if (!container) {
    console.error('container ref not found')
    return
  }
  const svgString = container.outerHTML
  downloadTextFile(`cluster-${props.cluster.number}.svg`, 'text/svg', svgString)
}
</script>
