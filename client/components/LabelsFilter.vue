<template>
  <div v-for="labelFilter in allLabelFilters">
    <RpcCheckbox
      :id="domIdBuilder(labelFilter.id)"
      :label="labelFilter.slug"
      size="small"
      :checked="labelFilter.id && selectedLabelsTristate?.[labelFilter.id] ?
        selectedLabelsTristate[labelFilter.id]:
        CHECKBOX_INDETERMINATE"
      :has-indeterminate="true"
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
    />
  </div>
</template>

<script setup lang="ts">
import type { Label } from '~/purple_client'
import { CHECKBOX_INDETERMINATE } from '~/utilities/checkbox'
import type { CheckboxTristate } from '~/utilities/checkbox'

const allLabelFilters = defineModel<Label[]>(
  'all-label-filters',
  { required: true }
)

const selectedLabelsTristate = defineModel<Record<number, CheckboxTristate>>(
  'selected-label-filters',
  { required: true }
)

const domIdBuilder = (id: number | undefined) => `labels-filter-${id}`
</script>
