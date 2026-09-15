<template>
  <div
    v-if="props.compact"
    class="flex flex-wrap items-center gap-x-4 gap-y-1 rounded-lg border border-gray-200 bg-gray-50 px-4 py-3 shadow dark:border-gray-700 dark:bg-neutral-900 sm:px-6">
    <span class="text-base font-semibold text-gray-900 dark:text-gray-200">{{ props.title }}:</span>
    <span v-if="props.labels.length === 0" class="italic">(None)</span>
    <RpcCheckbox
      v-for="label in props.labels"
      :key="label.id"
      :label="`${label.isException ? '⚠️ ' : ''}${label.text}`"
      :value="label.id"
      :checked="Boolean(selectedLabelIds?.includes(label.id ?? 0))"
      :class="[
        'pl-1 pr-2 rounded-md text-xs font-medium ring-1 ring-inset',
        badgeColors[label.color ?? ('gray' satisfies ColorEnum)]
      ]"
      @change="handleCheckboxChange"
      size="small"
      :title="label.text" />
  </div>
  <BaseCard v-else>
    <template #header>
      <CardHeader :title="props.title" />
    </template>
    <p v-if="props.labels.length === 0" class="italic">(None)</p>
    <fieldset v-for="(groupOfLabels, slugGroup) in groupsOfLabels" :key="slugGroup">
      <legend v-if="slugGroup !== UNGROUPED" class="font-bold opacity-75 text-sm pt-2">
        {{ slugGroup }}:
      </legend>
      <RpcCheckbox
        v-if="slugGroup === UNGROUPED"
        v-for="label in groupOfLabels"
        :key="label.id"
        :label="`${label.isException ? '⚠️ ' : ''}${label.text}`"
        :value="label.id"
        :checked="Boolean(selectedLabelIds?.includes(label.id ?? 0))"
        :class="[
          'pl-1 mb-1 pr-2 rounded-md text-xs font-medium ring-1 ring-inset text-xs',
          badgeColors[label.color ?? ('gray' satisfies ColorEnum)]
        ]"
        @change="handleCheckboxChange"
        size="small"
        :title="label.text" />
      <div v-else class="ml-0.5">
        <DocLabelsGroup
          v-model="selectedLabelIds!"
          :value="labelGroupRefs[slugGroup]"
          :labels="groupOfLabels"
          :slug-group="slugGroup.toString()" />
      </div>
    </fieldset>
  </BaseCard>
</template>

<script setup lang="ts">
import { groupBy } from 'es-toolkit/array'
import { type Label, type ColorEnum } from '~/purple_client'
import { SLUG_SEPARATOR, UNGROUPED } from '~/utils/labels'
import { badgeColors } from '~/utils/badge'
import { assert } from '~/utils/typescript'
import { sortObject } from '~/utils/sort'

type Props = {
  title: string
  labels: Label[]
  compact?: boolean
}

const props = withDefaults(defineProps<Props>(), { compact: false })

const selectedLabelIds = defineModel<number[] | null>()

const handleCheckboxChange = (e: Event) => {
  const { target } = e
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
      throw Error(
        `Unexpected state. Should be able to find indexOf ${value} in ${JSON.stringify(selectedLabelIds.value)}`
      )
    }
    selectedLabelIds.value.splice(indexOf, 1)
  }
}

const groupsOfLabels = computed(() =>
  sortObject(
    groupBy(props.labels, (label) =>
      label.text.includes(SLUG_SEPARATOR)
        ? label.text.substring(0, label.text.indexOf(SLUG_SEPARATOR))
        : UNGROUPED
    )
  )
)

const labelGroupRefs = computed(() => {
  assert(selectedLabelIds.value)
  return Object.keys(groupsOfLabels.value).reduce(
    (acc, slugGroup) => {
      const defaultSelectedSlug = groupsOfLabels.value[slugGroup]?.find((label) => {
        assert(selectedLabelIds.value)
        assert(label.id)
        return selectedLabelIds.value.includes(label.id)
      })
      acc[slugGroup] = defaultSelectedSlug?.id
      return acc
    },
    {} as Record<string, number | undefined>
  )
})
</script>
