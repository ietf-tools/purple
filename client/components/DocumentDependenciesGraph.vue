<template>
  <div>
    graph {{ JSON.stringify(props.cluster) }}

    {{ clusterDocumentsError }}
    {{ JSON.stringify(clusterDocuments) }}
  </div>
</template>

<script setup lang="ts">
import type { Cluster } from '~/purple_client'

type Props = {
  cluster: Cluster
}

const props = defineProps<Props>()

const api = useApi()

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

watch(props.cluster, () => {

})
</script>
