<template>
  <div v-bind="$attrs"
    :class="['flex gap-1 p-1 text-xs cursor-pointer rounded-sm shadow text-gray-800 dark:text-white bg-white dark:bg-neutral-700 outline outline-1 outline-gray-300 dark:outline-gray-400 focus-within:outline-2 focus-within:outline-purple-600 focus-within:outline-purple-600 dark:focus-within:outline-white ', props.class]"
    @click="handleChange">
    <span :class="{
      'block w-5 h-5 text-center font-semibold font-mono shadow-inner dark:shadow-none border rounded-sm pt-[0.2em]': true,
      'bg-green-100 border-gray-500 shadow-gray-300 text-green-700': props.checked === true,
      'bg-red-100 border-red-600 shadow-gray-300 text-red-800': props.checked === false,
      'bg-transparent border-gray-400 shadow-gray-200': props.checked === TRISTATE_MIXED,
    }">
      <span v-if="props.checked === true">Y</span>
      <span v-else-if="props.checked === false">N</span>
      <span v-else-if="props.checked === TRISTATE_MIXED">&nbsp;</span>
    </span>
    <button ref="button" type="button" :aria-pressed="props.checked"
      class="border-0 bg-transparent focus:border-0 focus:outline-0 pl-1 pr-1">
      <slot />
    </button>
  </div>
</template>

<script setup lang="ts">
import { TRISTATE_MIXED, type TristateValue } from '~/utilities/tristate'
import type { VueStyleClass } from '~/utilities/vue'

/**
 * Implements a tristate button using `aria-pressed`.
 * https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Attributes/aria-pressed
 */

type Props = {
  class?: VueStyleClass
  checked: TristateValue
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'change', value: TristateValue): void
}>()

const button = useTemplateRef('button')

// COMPUTED

const intToTristate = (int: number): TristateValue => {
  // Use modulus to track clicks
  // mod3 === 0 is true
  // mod3 === 1 is false
  // mod3 === 2 is 'mixed'
  const mod3 = int % 3
  return mod3 === 2 ? TRISTATE_MIXED : mod3 === 0 ? true : false
}

const tristateToInt = (tristate: TristateValue): number => {
  return tristate === TRISTATE_MIXED ? 2 : tristate ? 0 : 1
}

const checkCounter = ref<number>(tristateToInt(props.checked))

const handleChange = () => {
  button.value?.focus()
  // use our internal state instead of event.target.checked state
  checkCounter.value++
  emit('change', intToTristate(checkCounter.value))
}

</script>
