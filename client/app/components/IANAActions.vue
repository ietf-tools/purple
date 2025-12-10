<template>
  <ul class="flex flex-col gap-2">
    <li v-for="ianaAction in IANAActionsEntries">
      <RpcRadio name="ianaAction" :value="ianaAction[1]" :checked="ianaAction[1] === ianaChoice" :label="startCase(ianaAction[0])" @change="handleChange" />
    </li>
  </ul>
</template>

<script setup lang="ts">
import { startCase } from 'lodash-es'
import { type IANAActionsEnum, IANAActionsEntries } from '../utils/iana'

const ianaChoice = defineModel<IANAActionsEnum | undefined>({ required: true })

const handleChange = (e: Event) => {
  const { target } = e
  assert(target instanceof HTMLInputElement)
  ianaChoice.value = target.value as IANAActionsEnum
}
</script>
