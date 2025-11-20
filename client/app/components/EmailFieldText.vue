<template>
  <label :class="['flex flex-row w-full', {
    'items-center': !props.isMultiline
  }]">
    <span class="w-[6em] font-bold">{{ props.label }}:</span>
    <input v-if="!props.isMultiline" :id="props.fieldId" type="text" v-model="value" :class="[props.fieldClass, 'rounded-md text-black dark:text-white bg-white dark:bg-black']" />
    <textarea v-else-if="props.isMultiline" :id="props.fieldId" v-model="value" :class="[props.fieldClass, 'font-mono resize-none text-xs text-black dark:text-white bg-white dark:bg-black rounded-md']" />
  </label>
</template>
<script setup lang="ts">

type Props = {
  label: string
  fieldId: string
  isMultiline: boolean
  fieldClass?: string
}

const props = defineProps<Props>()

const value = defineModel<string>({ required: true })

</script>
