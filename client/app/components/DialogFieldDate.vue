<template>
  <fieldset class="mb-2 flex items-center">
    <label class="text-gray-900 w-[160px] text-right text-sm font-bold mr-1" :for="props.id"> {{ props.label }}:</label>
    <div class="flex flex-row gap-1 border border-gray-700 rounded-md">
      <span v-if="selectedDateString"
        class="flex flex-row bg-gray-100 text-xs rounded-lg px-2 py-0.5 shadow-md border-1 border-gray-500 items-center gap-1 px-1">
        <b>{{ selectedDateString }}</b>
        <button type="button"
          class="rounded-lg bg-gray-200 focus:bg-gray-300 hover:bg-gray-300 p-0.5 text-black border-none"
          @click="handleClearSelectedDateString"
          :label="`Unselect date ${handleClearSelectedDateString}`">&times;</button>
      </span>
      <input type="date" v-model="tempDateString" :id="props.id" :class="[
        'bg-gray-100 focus:shadow-gray-300 border-none inline-flex rounded-lg px-3 text-sm leading-none outline-none',
        props.disabled && 'border-gray-300 text-gray-600',
        !props.disabled && 'border-gray-500 text-gray-900'
      ]" :disabled="props.disabled" @blur="" />
    </div>
  </fieldset>
</template>

<script setup lang="ts">
const selectedDateString = defineModel<string | undefined>()

const tempDateString = ref<string | undefined>(undefined)

watch(tempDateString, () => {
  if (tempDateString.value) {
    selectedDateString.value = tempDateString.value
    tempDateString.value = undefined
  }
})

type Props = {
  id: string,
  label: string
  disabled?: boolean
}

const props = defineProps<Props>()

const handleClearSelectedDateString = () => {
  selectedDateString.value = undefined
}
</script>
