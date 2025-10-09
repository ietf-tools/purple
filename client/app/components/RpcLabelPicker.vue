<template>
  <HeadlessCombobox v-model="selectedLabels" as="div" multiple>
    <HeadlessComboboxLabel :id="comboboxLabelId" class="block text-sm font-medium leading-6 text-gray-900 dark:text-neutral-300">
      {{ props.label }}
    </HeadlessComboboxLabel>
    <div class="relative mt-2">
      <HeadlessComboboxInput
        :id="comboboxInputId"
        class="w-full rounded-md border-0 bg-white py-1.5 pl-3 pr-12 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
        :display-value="(lbl) => lbl ? (lbl as Label).slug : ''"
        @change="state.query = $event.target.value"
      />
      <HeadlessComboboxButton :id="comboboxButtonId" class="absolute inset-y-0 right-0 flex items-center rounded-r-md px-2 focus:outline-none">
        <Icon name="heroicons:chevron-up-down-solid" class="h-5 w-5 text-gray-400" aria-hidden="true"/>
      </HeadlessComboboxButton>

      <HeadlessComboboxOptions
        v-if="filteredLabels.length > 0"
        class="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm">
        <HeadlessComboboxOption
          v-for="lbl in filteredLabels" :key="lbl.id" v-slot="{ active, selected }" :value="lbl"
          as="template">
          <li
            :class="['relative cursor-default select-none py-2 pl-3 pr-9', active ? 'bg-indigo-600 text-white' : 'text-gray-900']">
            <div class="flex items-center">
              <span :class="['ml-3 truncate', selected && 'font-semibold']">
                <span v-if="lbl.isException" class="sr-only">Exception</span>
                <RpcLabel :label="lbl"/>
              </span>
            </div>
            <span
              v-if="selected"
              :class="['absolute inset-y-0 right-0 flex items-center pr-4', active ? 'text-white' : 'text-indigo-600']">
              <Icon name="heroicons:check" class="h-5 w-5" aria-hidden="true"/>
            </span>
          </li>
        </HeadlessComboboxOption>
      </HeadlessComboboxOptions>
    </div>
  </HeadlessCombobox>
</template>

<script setup lang="ts">
import type { Label } from '~/purple_client'

// work around hydration mismatch bug in Headless by explicitly generating stable IDs
const comboboxLabelId = useId()
const comboboxButtonId = useId()
const comboboxInputId = useId()

type Props = {
  /**
   * Available labels
   */
  labels?: Label[]
  /**
   * ids of applied labels
   */
  modelValue?: number[]
  /**
   * Component UI label
   */
  label?: string
}

const props = withDefaults(defineProps<Props>(), {
  labels: () => [],
  modelValue: () => [],
  label: 'Choose labels'
})

const emit = defineEmits(['update:modelValue'])

const selectedLabels = computed({
  get () {
    return props.labels.filter((lbl) => {
      if(lbl.id === undefined) {
        return false
      }
      props.modelValue.includes(lbl.id)
    })
  },
  set (value) {
    emit('update:modelValue', value.map((lbl) => lbl.id))
  }
})

const state = reactive({
  query: ''
})

const filteredLabels = computed(() => {
  const sortedLabels = props.labels.toSorted((a, b) => {
    if (a.isException && !b.isException) {
      return -1
    } else if (!a.isException && b.isException) {
      return 1
    }
    return a.slug.localeCompare(b.slug)
  })
  return state.query === ''
    ? sortedLabels
    : sortedLabels.filter((lbl) => {
      return lbl.slug.toLowerCase().includes(state.query.toLowerCase())
    })
})
</script>

<docs>
## Usage
The `LabelPicker` component provides a combobox to manage a set of labels.

The `Labels` prop is a list of objects that should include at least `id`, `slug`, and `color` fields.

The `modelValue` prop is a list of `id` values that are currently selected.
</docs>
