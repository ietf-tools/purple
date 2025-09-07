<template>
  <div class="w-full h-full">
    graph

    <pre>{{ JSON.stringify(data, null, 2) }}</pre>
    <hr />

    <div ref="container" class="w-full h-full"></div>
  </div>
</template>

<script setup lang="ts">
import type { Cluster } from '~/purple_client'
import { draw_graph } from '~/utilities/document_relations';
import { test_data2 } from '~/utilities/document_relations-utils'
import type { DataParam, Node, Link, NodeParam, LinkParam } from '~/utilities/document_relations-utils';
import { assert } from '~/utilities/typescript';

type Props = {
  cluster: Cluster
}

const props = defineProps<Props>()

const api = useApi()

const containerRef = useTemplateRef('container')

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

onMounted(() => {
  const { value: container } = containerRef

  if (!container) {
    console.error('container ref not found')
    return
  }


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

console.log(data.value)

  let [leg_el, leg_sim] = draw_graph(data.value, "stir");

  if (!(leg_el instanceof SVGElement) || !leg_sim) {
    console.error('Received unexpected response from draw_graph', { leg_el, leg_sim })
    return
  }

  console.log({ leg_el })

  container.appendChild(leg_el)

  leg_sim.restart();
})
</script>
