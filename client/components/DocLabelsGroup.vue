<template>
  <div class="flex flex-col shadow-sm mx-auto" :modelValue="props.value" @update:modelValue="handleChange">
    <div class="flex flex-col gap-1">
      <RpcCheckbox
        v-for="label in props.labels"
        :key="label.id"
        :value="label.id!"
        :checked="Boolean(selectedLabelIds?.includes(label.id ?? 0))"
        :class="[
          'pl-1 mb-1 pr-2 rounded-md text-xs font-medium ring-1 ring-inset text-xs',
          badgeColors[label.color ?? 'violet']
        ]"
        @change="handleCheckboxChange"
        size="small"
        :label="`${label.isException ? '⚠️ ' : ''}${label.slug.substring(label.slug.indexOf(SLUG_SEPARATOR) + 1)}`"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Label } from '~/purple_client';
import { SLUG_SEPARATOR } from '../utilities/labels'
import { badgeColors } from '~/utilities/badge'
import { assert } from '~/utilities/typescript';

type Props = {
  slugGroup: string
  labels: Label[]
  value?: number
}

const props = defineProps<Props>()

const selectedLabelIds = defineModel<number[]>()

const handleCheckboxChange = (e: Event) => {
  const { target } = e;
  if (!(target instanceof HTMLInputElement)) {
    console.error(e)
    throw Error(`Unsupported event wasn't from expected element`)
  }
  assert(selectedLabelIds.value)

  const { value: valueString, checked } = target

  const value = parseInt(valueString, 10)
  assert(!Number.isNaN(value))

  if (checked && !selectedLabelIds.value.includes(value)) {
    selectedLabelIds.value.push(value)
  } else if (!checked && selectedLabelIds.value.includes(value)) {
    const indexOf = selectedLabelIds.value.indexOf(value)
    if (indexOf === -1) {
      throw Error(`Unexpected state. Should be able to find indexOf ${value} in ${JSON.stringify(selectedLabelIds.value)}`)
    }
    selectedLabelIds.value.splice(indexOf, 1)
  }
}


</script>
