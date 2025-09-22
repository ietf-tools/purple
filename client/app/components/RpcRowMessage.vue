<template>
  <tr v-if="statusArr.some(status => status === 'idle' || status === 'pending')">
    <RpcTdMessage :colspan="props.columnCount">
      Loading...
    </RpcTdMessage>
  </tr>
  <tr v-else-if="props.rowCount === 0 && !statusArr.some(status => status === 'error')">
    <RpcTdMessage :colspan="props.columnCount">
      No rows found
    </RpcTdMessage>
  </tr>
</template>

<script setup lang="ts">

type Status = Awaited<ReturnType<typeof useAsyncData>>['status']['value']

type Props = {
  rowCount: number
  columnCount: number
  status: Status | Status[]
}

const statusArr = computed(()=> {
  const { status } = props
  return Array.isArray(status) ? status : [status]
})

const props = defineProps<Props>()
</script>
