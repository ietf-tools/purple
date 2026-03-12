<template>
  <tr v-if="statusArr.some(status => status === 'pending')">
    <RpcTdMessage :colspan="props.columnCount">
      Loading...
    </RpcTdMessage>
  </tr>
  <tr v-else-if="statusArr.every(status => status === 'success') && props.rowCount === 0">
    <RpcTdMessage :colspan="props.columnCount">
      No rows found
    </RpcTdMessage>
  </tr>
  <tr v-else-if="errorArr.some(error => Boolean(error))">
    <RpcTdMessage :colspan="props.columnCount" class="bg-red-300">
      Error:
      <BaseBadge v-for="error in errorArr" color="red" class="mr-2">
        {{ error }}
      </BaseBadge>
    </RpcTdMessage>
  </tr>
</template>

<script setup lang="ts">
type UseAsyncDataReturn = Awaited<ReturnType<typeof useAsyncData>>
type Status = UseAsyncDataReturn['status']['value']
type Error = UseAsyncDataReturn['error']['value']

type Props = {
  rowCount: number
  columnCount: number
  status: Status | Status[]
  error: Error | Error[]
}

const props = defineProps<Props>()

const statusArr = computed(() => {
  const { status } = props
  return Array.isArray(status) ? status : [status]
})

const errorArr = computed(() => {
  const { error } = props
  return Array.isArray(error) ? error : [error]
})
</script>
