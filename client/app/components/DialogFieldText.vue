<template>
  <fieldset class="mb-2 flex items-center gap-5 mr-1">
    <label class="text-gray-900 w-[160px] text-right text-sm font-bold" :for="props.id"> {{ props.label }}:</label>
    <input
      v-if="!props.isMultiline"
      :id="props.id"
      v-model="model"
      :class="[
        'bg-gray-100 focus:shadow-gray-300 inline-flex w-full flex-1 items-center justify-center rounded-lg px-3 text-sm leading-none outline-none',
        props.disabled && 'border-gray-300 text-gray-600',
        !props.disabled && 'border-gray-500 text-gray-900'
      ]"
      :disabled="props.disabled"
    />
    <textarea
      v-else
      :id="props.id"
      v-model="model"
      :class="[
        'bg-gray-100 focus:shadow-gray-300 inline-flex w-full flex-1 items-center justify-center rounded-lg px-3 text-sm leading-none outline-none',
        props.disabled && 'border-gray-300 text-gray-600',
        !props.disabled && 'border-gray-500 text-gray-900'
      ]"
      :disabled="props.disabled"
    />
  </fieldset>
</template>

<script setup lang="ts">

const model = defineModel<string>({ required: true })

type Props = {
  id: string,
  label: string
  isMultiline?: boolean
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), { isMultiline: false })
</script>
