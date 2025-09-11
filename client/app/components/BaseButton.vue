<template>
  <button
    type="button"
    :class="classForBtnType[props.btnType]">
    <slot />
  </button>
</template>

<script setup lang="ts">
const commonClasses = 'rounded-md px-3 py-2 text-sm font-semibold shadow-sm focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 disabled:cursor-not-allowed'
const classForBtnType = {
  default: `${commonClasses} text-white bg-indigo-600 hover:bg-indigo-500 dark:bg-indigo-600 dark:hover:bg-indigo-700 focus:outline-none disabled:text-gray-100 disabled:bg-indigo-200 dark:disabled:text-gray-500 dark:disabled:bg-indigo-900`,
  cancel: `${commonClasses} text-gray-900 bg-white border border-gray-300 hover:bg-gray-100 dark:bg-gray-800 dark:text-white dark: border-gray-700 dark:hover:bg-gray-700 disabled:text-gray-200 disabled:bg-white dark:disabled:text-gray-500 dark:disabled:bg-gray-900 dark:disabled:border-gray-800`
}

type Props = { btnType: keyof (typeof classForBtnType) }
const props = withDefaults(defineProps<Props>(), { btnType: 'default' })

</script>
