<template>
  <component :is="elementName">
    {{ props.workload.clusterIds.length }}
    <template v-if="props.workload.clusterIds.length === 1">cluster, </template>
    <template v-else>clusters, </template>
  </component>
  <component :is="elementName" v-for="([role, pageCount], index) in orderedRoles">
    {{ pageCount }}
    <BaseBadge :label="role" />
    <template v-if="pageCount === 1">page</template>
    <template v-else>pages</template>
    <template v-if="index === orderedRoles.length - 1">.</template>
    <template v-else>, </template>
  </component>
</template>

<script setup lang="ts">
/**
 * Generally trying to make it render a summary that looks like
 *
 * "2 clusters, 104 first edit pages, 93 second edit pages" etc...
 */
type Props = {
  workload: RpcPersonWorkload
  mode?: 'inline' | 'rows'
}

const props = withDefaults(defineProps<Props>(), { 'mode': 'inline' })

const elementName = computed(() => props.mode === 'inline' ? 'span' : 'div')

const orderedRoles = computed(() => {
  return Object.entries(props.workload.pageCountByRole).sort(([keyA, _valueA], [keyB, _valueB]) => keyA.localeCompare(keyB, 'en'))
})
</script>
