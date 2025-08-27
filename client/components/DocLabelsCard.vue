<template>
  <BaseCard>
    <template #header>
      <CardHeader :title="props.title"/>
    </template>
    <p v-if="props.labels.length === 0" class="italic">(None)</p>
    <fieldset v-for="(groupOfLabels, slugGroup) in groupsOfLabels" :key="slugGroup">
      <legend v-if="slugGroup !== UNGROUPED" class="font-bold opacity-75 text-sm pt-2">{{slugGroup}}:</legend>
      <RpcCheckbox
        v-if="slugGroup === UNGROUPED"
        v-for="label in groupOfLabels"
        :key="label.id"
        :label="`${label.isException ? '⚠️ ' : ''}${label.slug}`"
        :value="label.id"
        :checked="Boolean(selectedLabelIds?.includes(label.id ?? 0))"
        :class="[
          'pl-1 mb-1 pr-2 rounded-md text-xs font-medium ring-1 ring-inset text-xs',
          badgeColors[label.color ?? 'violet']
        ]"
        @change="handleCheckboxChange"
        size='small'
        :title="label.slug"
      />
      <div v-else class="ml-0.5">
        <DocLabelsGroup v-model="selectedLabelIds!" :value="labelGroupRefs[slugGroup]" :labels="groupOfLabels" :slug-group="slugGroup.toString()" />
      </div>
    </fieldset>
  </BaseCard>
</template>

<script setup lang="ts">
import { groupBy } from 'lodash-es'
import type { Label } from '~/purple_client'
import { SLUG_SEPARATOR, UNGROUPED } from '../utilities/labels'
import { badgeColors } from '~/utilities/badge'
import { assert } from '~/utilities/typescript'
import { sortObject } from '~/utilities/sort'

type Props = {
  title: string
  labels: Label[]
}

const props = defineProps<Props>()

const selectedLabelIds = defineModel<number[] | null>()

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

  if(checked && !selectedLabelIds.value.includes(value)) {
    selectedLabelIds.value.push(value)
  } else if (!checked && selectedLabelIds.value.includes(value)) {
    const indexOf = selectedLabelIds.value.indexOf(value)
    if(indexOf === -1) {
      throw Error(`Unexpected state. Should be able to find indexOf ${value} in ${JSON.stringify(selectedLabelIds.value)}`)
    }
    selectedLabelIds.value.splice(indexOf, 1)
  }
}


const groupsOfLabels = computed(() => sortObject(
    groupBy(
      props.labels,
      (label) => label.slug.includes(SLUG_SEPARATOR) ?
                  label.slug.substring(0, label.slug.indexOf(SLUG_SEPARATOR)) :
                  UNGROUPED
    )
  )
)

const labelGroupRefs = computed(() => {
    assert(selectedLabelIds.value)
    return Object.keys(groupsOfLabels.value)
      .reduce((acc, slugGroup) => {
        const defaultSelectedSlug = groupsOfLabels.value[slugGroup].find(label => {
          assert(selectedLabelIds.value)
          assert(label.id)
          return selectedLabelIds.value.includes(label.id)
        })
        acc[slugGroup] = defaultSelectedSlug?.id
        return acc
      }, {} as Record<string, number | undefined>)
})

</script>
