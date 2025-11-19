<template>
  <fieldset class="mb-2 flex items-center">
    <label class="text-gray-900 w-[160px] text-right text-sm font-bold" :for="props.id"> {{ props.label }}:</label>
    <input
      type="date"
      v-model="model"
      :id="props.id"
      :class="[
        'bg-gray-100 focus:shadow-gray-300 inline-flex rounded-lg px-3 text-sm leading-none outline-none',
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
  disabled?: boolean
}

const props = defineProps<Props>()
</script>
