<template>
  <fieldset class="flex mr-1 items-center">
    <label class="text-gray-900 w-[160px] text-right text-sm font-bold mr-1" :for="props.id"> {{ props.label }}:</label>
    <input
      type="text"
      inputmode="numeric"
      pattern="[0-9]*"
      :id="props.id"
      v-model="model"
      :class="[
        'focus:shadow-gray-300 inline-flex w-full flex-1 items-center justify-center rounded-lg px-3 text-sm leading-none outline-none',
        props.disabled && 'border-gray-300 text-gray-600',
        !props.disabled && 'border-gray-500 text-gray-900'
      ]"
      :disabled="props.disabled"
      :placeholder="props.placeholder"
    />
  </fieldset>
</template>

<script setup lang="ts">

const model = defineModel<string>({ required: true })

type Props = {
  id: string,
  label: string
  disabled?: boolean
  placeholder?: string
}

const props = withDefaults(defineProps<Props>(), { isMultiline: false })
</script>
