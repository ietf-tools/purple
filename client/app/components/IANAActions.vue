<template>
  <ul class="flex flex-col gap-2">
    <li v-for="ianaAction in IANAActionsEntries">
      <RpcRadio name="ianaAction" :value="ianaAction[1]" :checked="ianaAction[1] === ianaChoice"
        :label="labelFor(ianaAction[1])" @change="handleChange" />
    </li>
  </ul>
</template>

<script setup lang="ts">
import type { IanaStatus } from '~/purple_client'
import { type IANAActionsEnum, IANAActionsEntries } from '../utils/iana'

const ianaChoice = defineModel<IANAActionsEnum | undefined>({ required: true })

const api = useApi()
const { data: ianaStatuses } = await useAsyncData('iana-statuses', () => api.ianaStatusesList(), {
  server: false,
  lazy: true,
  default: () => [] as IanaStatus[],
})

const labelFor = (slug: string): string =>
  ianaStatuses.value.find(s => s.slug === slug)?.desc ?? slug

const handleChange = (e: Event) => {
  const { target } = e
  assert(target instanceof HTMLInputElement)
  ianaChoice.value = target.value as IANAActionsEnum
}
</script>
