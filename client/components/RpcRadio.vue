<template>
  <div class="relative flex items-start">
    <div class="flex h-6 items-center">
      <input
        v-bind="$attrs"
        :id="inputId"
        :aria-describedby="descriptionId"
        type="radio"
        :class="[caution ? 'border-rose-300 dark:border-rose-500 text-rose-700 dark:text-rose-700 hover:border-rose-400 focus:ring-rose-600' : 'border-gray-300 dark:border-neutral-500 text-violet-600 dark:text-violet-500 hover:border-violet-400 dark:hover:border-violet-500 focus:ring-violet-600 dark:focus:ring-violet-500', 'h-4 w-4 bg-white dark:bg-neutral-900']"
      >
    </div>
    <div class="ml-3 text-sm leading-6">
      <label
        :for="inputId"
        :class="[caution ? 'text-rose-800 dark:text-rose-400' : 'text-gray-900 dark:text-neutral-200', 'font-medium']">
        {{ label }}
      </label>
      <p
        v-if="desc"
        :id="descriptionId"
        :class="[caution ? 'text-rose-700 dark:text-rose-500' : 'text-gray-500 dark:text-neutral-400', 'text-xs']">
        {{ desc }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">

// Fallthrough attributes are applied to an internal element via v-bind="$attrs"
defineOptions({ inheritAttrs: false })

type Props = {
  caution?: boolean,
  desc?: string,
  id?: string,
  label: string,
}

const props = withDefaults(defineProps<Props>(), {
  caution: false,
  desc: undefined,
  id: undefined,
})

const componentId = useId()

// COMPUTED

const inputId = computed(() => props.id || componentId)
const descriptionId = computed(() => props.desc && `${inputId.value}-desc`)

</script>
