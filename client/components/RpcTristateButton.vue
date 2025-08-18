<template>
  <div
    v-bind="$attrs"
    :class="['flex gap-1 p-1 text-xs cursor-pointer rounded-sm shadow text-gray-800 dark:text-white bg-white dark:bg-neutral-700 outline outline-1 outline-gray-300 dark:outline-gray-400 focus-within:outline-2 focus-within:outline-purple-600 focus-within:outline-purple-600 dark:focus-within:outline-white ', props.class]"
    @click="handleChange"
  >
    <span :class="{
      'block w-5 h-5 text-center font-semibold font-mono shadow-inner dark:shadow-none border rounded-sm pt-[0.2em]': true,
      'bg-green-100 border-gray-500 shadow-gray-300 text-green-700': props.checked === true,
      'bg-red-100 border-red-600 shadow-gray-300 text-red-800': props.checked === false,
      'bg-transparent border-gray-400 shadow-gray-200': props.checked === 'mixed',
    }">
      <span v-if="props.checked === true">Y</span>
      <span v-else-if="props.checked === false">N</span>
      <span v-else-if="props.checked === TRISTATE_MIXED">&nbsp;</span>
    </span>
    <button
      ref="button"
      type="button"
      :aria-pressed="props.checked"
      class="border-0 bg-transparent focus:border-0 focus:outline-0 pl-1 pr-1"
    >
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

const checkCounter = ref<number>(props.checked === TRISTATE_MIXED ? 2 : props.checked ? 1 : 0)

const handleChange = () => {
  button.value?.focus()
  // use our internal state instead of event.target.checked state
  checkCounter.value++
  // Use modulus to track clicks
  // mod3 === 0 is false
  // mod3 === 1 is true
  // mod3 === 2 is indeterminate see
  // https://developer.mozilla.org/en-US/docs/Web/API/HTMLInputElement/indeterminate
  const mod3 = checkCounter.value % 3
  emit('change', mod3 === 2 ? TRISTATE_MIXED : Boolean(mod3))
}
</script>
