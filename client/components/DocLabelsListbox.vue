<template>
  <ListboxRoot class="flex flex-col shadow-sm mx-auto" :modelValue="props.value" @update:modelValue="handleChange">
    <ListboxContent>
      <ListboxGroup class="flex flex-col gap-1">
        <ListboxItem
          v-for="label in props.labels"
          :key="label.id"
          :value="label.id!"
          :class="[
            'group w-full flex items-center pl-[25px] py-1 focus:ring-purple-800 focus:ring-2 rounded relative select-none outline-none data-[disabled]:opacity-50 rounded-md text-xs font-medium ring-1 ring-inset',
            label.color && badgeColors[label.color]
          ]"
        >
          <div class="absolute left-[5px]">
            <!-- renders an unchecked checkbox -->
            <CheckboxInert class="group-hover:border-purple-400" />
          </div>
          <ListboxItemIndicator class="absolute left-[5px]">
            <!-- renders an checked checkbox ontop of the one below -->
            <CheckboxInert checked="true" />
          </ListboxItemIndicator>
          <span v-if="label.isException">⚠️</span>
          <span class="pl-1 cursor-pointer">{{ label.slug.substring(label.slug.indexOf(SLUG_SEPARATOR) + 1) }}</span>
        </ListboxItem>
      </ListboxGroup>
    </ListboxContent>
  </ListboxRoot>
</template>

<script setup lang="ts">
import { ListboxContent, ListboxGroup, ListboxItem, ListboxItemIndicator, ListboxRoot } from 'reka-ui'
import type { AcceptableValue } from 'reka-ui'
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

const handleChange = computed(() => {
  return (value: AcceptableValue): void => {

    assert(selectedLabelIds.value, `Expected selectedLabelIds.value`)

    const eraseExistingGroupSelection = () =>
      props.labels.forEach(label => {
        assert(selectedLabelIds.value)
        assert(label.id)
        if (selectedLabelIds.value.includes(label.id)) {
          const indexOf = selectedLabelIds.value.indexOf(label.id)
          assert(indexOf !== -1, `Unexpected state. Should be able to find indexOf ${label.id} in ${JSON.stringify(selectedLabelIds.value)}`)
          selectedLabelIds.value?.splice(indexOf, 1)
        }
      })

    if (value && typeof value === 'number' && !selectedLabelIds.value.includes(value)) {
      eraseExistingGroupSelection()
      selectedLabelIds.value.push(value)
    } else if (value === undefined) {
      eraseExistingGroupSelection()
    }
  }
})

</script>
