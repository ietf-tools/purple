<template>
  <span>
    {{ props.workload.clusterIds.length }}
    <template v-if="props.workload.clusterIds.length === 1">cluster, </template>
    <template v-else>clusters, </template>
  </span>
  <span v-for="([role, pageCount], index) in orderedRoles">
    <BaseBadge :label="role" />
    {{ pageCount }}
    <template v-if="pageCount === 1">page</template>
    <template v-else>pages</template>
    <template v-if="index === orderedRoles.length - 1">.</template>
    <template v-else>, </template>
  </span>
</template>

<script setup lang="ts">
type Props = {
  workload: RpcPersonWorkload
}

const props = defineProps<Props>()

const orderedRoles = computed(() => {
  return Object.entries(props.workload.pageCountByRole).sort(([keyA, valueA], [keyB, valueB]) => keyA.localeCompare(keyB, 'en'))
})
</script>
