<template>
  <div class="w-full h-full">
    graph {{ JSON.stringify(props.cluster) }}

    {{ clusterDocumentsError }}
    {{ JSON.stringify(clusterDocuments) }}


<svg width="320" height="130" xmlns="http://www.w3.org/2000/svg">
  <rect width="300" height="100" x="10" y="10" style="fill:rgb(0,0,255);stroke-width:3;stroke:red" />
  Sorry, your browser does not support inline SVG.
</svg>

    <div ref="container" class="w-full h-full"></div>
  </div>
</template>

<script setup lang="ts">
import type { Cluster } from '~/purple_client'
import { draw_graph } from '~/utilities/document_relations';
import type { Node, Link } from '~/utilities/document_relations';

type Props = {
  cluster: Cluster
}

const props = defineProps<Props>()

const api = useApi()

const containerRef = useTemplateRef('container')

const { data: clusterDocuments, error: clusterDocumentsError } = await useAsyncData(
  () => {
    console.log("name????", props.cluster.documents)
    return Promise.all(
      props.cluster.documents.map(
        (clusterDocument) => {
          console.log(clusterDocument)
          return api.documentsReferencesList({ draftName: clusterDocument.name })
        }
      ))
  },

)

onMounted(() => {
  const { value: container } = containerRef

  if (!container) {
    console.error('container ref not found')
    return
  }

  const legend = {
    nodes: [{
      id: "Individual submission",
      level: "Informational",
      group: ""
    }, {
      id: "Replaced",
      level: "Experimental",
      replaced: true
    }, {
      id: "IESG or RFC queue",
      level: "Proposed Standard",
      "post-wg": true
    }, {
      id: "Product of other group",
      level: "Best Current Practice",
      group: "other group"
    }, {
      id: "Expired",
      level: "Informational",
      group: "this group",
      expired: true
    }, {
      id: "Product of this group",
      level: "Proposed Standard",
      group: "this group"
    }, {
      id: "RFC published",
      level: "Draft Standard",
      group: "other group",
      rfc: true
    }] satisfies Node[],
    links: [{
      source: "Individual submission",
      target: "Replaced",
      rel: "replaces"
    }, {
      source: "Individual submission",
      target: "IESG or RFC queue",
      rel: "refnorm"
    }, {
      source: "Expired",
      target: "RFC published",
      rel: "refunk"
    }, {
      source: "Product of other group",
      target: "IESG or RFC queue",
      rel: "refinfo"
    }, {
      source: "Product of this group",
      target: "Product of other group",
      rel: "refold"
    }, {
      source: "Product of this group",
      target: "Expired",
      rel: "downref"
    }] satisfies Link[]
  };

  let [leg_el, leg_sim] = draw_graph(legend, "this group");

  if (!(leg_el instanceof HTMLElement)) {
    console.error('Received unexpected response from draw_graph', leg_el)
    return
  }

  console.log({leg_el})

  container.appendChild(leg_el)
})
</script>
