<template>
  <div class="h-full flex flex-col">
    <div class="flex gap-2 justify-between p-2 border-b border-gray-400">
      <span class="flex flex-row items-center text-md font-bold pl-1">
        Document dependencies
      </span>
      <span class="flex flex-row gap-2">
        <BaseButton btn-type="cancel" @click="closeOverlayModal" aria-label="Close modal">
          &times;
        </BaseButton>
      </span>
    </div>
    <div ref="container" class="flex-1 overflow-hidden"></div>
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
        <BaseButton btn-type="cancel" @click="closeOverlayModal" aria-label="Close modal">
          Cancel
        </BaseButton>
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { overlayModalKey } from '~/providers/providerKeys';
import type { Cluster } from '~/purple_client'
import { draw_graph, type DrawGraphParameters } from '~/utils/document_relations';
import { legendData, test_data2 } from '~/utils/document_relations-utils'
import type { DataParam, NodeParam, LinkParam } from '~/utils/document_relations-utils';
import { downloadTextFile } from '~/utils/download';
import { assert } from '~/utils/typescript';

type Props = {
  cluster: Cluster
}

const props = defineProps<Props>()

const overlayModalKeyInjection = inject(overlayModalKey)

if (!overlayModalKeyInjection) {
  throw Error('Expected injection of overlayModalKey')
}

const { closeOverlayModal } = overlayModalKeyInjection

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
      const { rfcNumber, name: draftName } = props.cluster.documents[index]
      assert(rfcNumber)
      return ({
        rfcNumber,
        draftName,
        documentsReferences
      })
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
      ) ?? [])
)

const canDownload = computed(() => Boolean(rfcToBes.value))

const data = computed((): DataParam => {
  return {
    links: [
      ...documentsReferencesByRfcs.value?.map((documentsReferencesByRfc): LinkParam => {
        const { rfcNumber, draftName } = documentsReferencesByRfc

        assert(rfcNumber)
        assert(draftName)

        return {
          source: `rfc${rfcNumber}`,
          rel: 'relinfo',
          target: draftName,
        }
      }) ?? [],

      ...documentsReferencesByRfcs.value?.flatMap((documentsReferencesByRfc): LinkParam[] => {
        const { rfcNumber, draftName, documentsReferences } = documentsReferencesByRfc

        return documentsReferences.map((documentsReference): LinkParam => {
          const {
            draftName: source,
            targetDraftName: target
          } = documentsReference

          assert(source)
          assert(target)

          return {
            source,
            rel: 'refnorm',
            target,
          }
        })
      }) ?? []
    ],
    nodes: [
      ...rfcToBes.value?.map((rfcToBe): NodeParam => {
        const {
          name: id,
          intendedStdLevel: level,
        } = rfcToBe

        assert(id)
        assert(level)

        return {
          id,
          url: `/doc/${id}/`,
          rfc: true,
          "post-wg": undefined,
          expired: undefined,
          replaced: undefined,
          group: undefined,
          level: undefined,
        }
      }) ?? []
    ]
  }
})

watchEffect(() => {
  const { value: container } = containerRef

  if (!container) {
    console.error('container ref not found')
    return
  }

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
