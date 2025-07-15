<template>
  <fieldset class="mb-2 flex items-center gap-5">
    <label class="text-gray-900 w-[130px] text-right text-sm font-bold" :for="props.id"> {{ props.label }}:</label>
    <input
      :id="props.id"
      v-model="model"
      class="text-gray-900 bg-gray-100 focus:shadow-gray-300 inline-flex w-full flex-1 items-center justify-center rounded-lg px-3 text-sm leading-none outline-none"
    >
  </fieldset>
</template>

<script setup lang="ts">

const model = defineModel({ required: true })

type Props = {
  id: string,
  label: string
}

const props = defineProps<Props>()

</script>
