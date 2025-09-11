<template>
  <div v-for="labelFilter in allLabelFilters">
    <RpcTristateButton
      :checked="labelFilter.id && selectedLabelsTristate?.[labelFilter.id] !== undefined ?
        selectedLabelsTristate[labelFilter.id] :
        TRISTATE_MIXED"
      @change="(tristate) => {
        if(!selectedLabelsTristate || !labelFilter.id) {
          console.warn('Can\'t update due to problem with selectedLabelsTristate or labelFilter.id', {
            selectedLabelsTristate,
            labelFilter
          })
          return
        }
        selectedLabelsTristate[labelFilter.id] = tristate
      }"
    >
      <RpcLabel :label="labelFilter"/>
    </RpcTristateButton>
  </div>
</template>

<script setup lang="ts">
import type { Label } from '~~/purple_client'
import { TRISTATE_MIXED } from '~/utils/tristate'
import type { TristateValue } from '~/utils/tristate'

const allLabelFilters = defineModel<Label[]>(
  'all-label-filters',
  { required: true }
)

const selectedLabelsTristate = defineModel<Record<number, TristateValue>>(
  'selected-label-filters',
  { required: true }
)
</script>
