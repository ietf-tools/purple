<template>
  <ul class="flex flex-col gap-2">
    <li v-for="ianaAction in IANAActionsEntries">
      <RpcRadio name="ianaAction" :value="ianaAction[0]" :checked="ianaAction[0] === ianaChoice" :label="ianaAction[1]" @change="handleChange" />
    </li>
  </ul>
</template>

<script setup lang="ts">
import { type IANAActionsEnum, IANAActionsEntries } from '../utils/iana'

const ianaChoice = defineModel<IANAActionsEnum>({ required: true })

const handleChange = (e: Event) => {
  const { target } = e
  assert(target instanceof HTMLInputElement)
  ianaChoice.value = target.value as IANAActionsEnum
}
</script>
